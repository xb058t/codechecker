# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------
"""
Clients for the AI providers. Each returns the answer as JSON, so the
orchestration layer need not care which service produced it.
"""

import json
import time

import requests

from codechecker_common.logger import get_logger

from .prompt import answer_schema

LOG = get_logger('server')

# Busy or briefly down, rather than refusing the request.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

# A 429 is either "slow down" or "out of money"; only the body tells them
# apart, and only the first is worth retrying.
PERMANENT_MARKERS = (
    'insufficient_quota',
    'credit_balance_exhausted',
    'insufficient balance',
    'exceeded your current quota',
)

MAX_ATTEMPTS = 3
BACKOFF_SCHEDULE = (1.0, 3.0)  # before the 2nd and 3rd


class AIProviderError(Exception):
    """ Raised when a provider could not produce a usable answer. """


class BaseProvider:
    default_api_url = None

    def __init__(self, model_config, timeout):
        self._config = model_config
        self._timeout = timeout

        # (input, output) tokens of the last completion, or None.
        self.last_usage = None

    @property
    def api_url(self):
        return self._config.api_url or self.default_api_url

    def complete(self, system_prompt, user_prompt):
        """ Send the prompts, return the raw answer as a JSON string. """
        raise NotImplementedError()

    def _record_openai_style_usage(self, data):
        """ Usage as the OpenAI compatible endpoints report it. """
        usage = data.get('usage') or {}
        if usage:
            self.last_usage = (usage.get('prompt_tokens'),
                               usage.get('completion_tokens'))

    @staticmethod
    def _is_retryable(status_code, body):
        """ Whether a failed response is worth sending again. """
        if status_code not in RETRYABLE_STATUS:
            return False

        lowered = (body or '').lower()
        return not any(marker in lowered for marker in PERMANENT_MARKERS)

    @staticmethod
    def _retry_delay(response, attempt):
        """ Retry-After when the provider sends one, else the schedule. """
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return max(0.0, min(float(retry_after), 30.0))
            except ValueError:
                pass  # an HTTP date rather than seconds

        return BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]

    def _post(self, url, headers, payload):
        """ POST and decode, retrying transient failures. """
        last_error = None

        for attempt in range(MAX_ATTEMPTS):
            try:
                response = requests.post(url,
                                         headers=headers,
                                         json=payload,
                                         timeout=self._timeout)
            except requests.Timeout as ex:
                raise AIProviderError(
                    f"The AI provider did not answer within {self._timeout} "
                    "seconds.") from ex
            except requests.RequestException as ex:
                raise AIProviderError(
                    f"Could not reach the AI provider: {ex}") from ex

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as ex:
                    raise AIProviderError(
                        "The AI provider returned a malformed "
                        "response.") from ex

            # The body usually carries the real reason.
            detail = response.text[:500] if response.text else ''
            last_error = (
                f"The AI provider answered with HTTP {response.status_code}. "
                f"{detail}")

            if not self._is_retryable(response.status_code, response.text):
                break

            if attempt < MAX_ATTEMPTS - 1:
                delay = self._retry_delay(response, attempt)
                LOG.info(
                    "The AI provider answered with HTTP %s; retrying in %.1fs "
                    "(attempt %d of %d).", response.status_code, delay,
                    attempt + 1, MAX_ATTEMPTS)
                time.sleep(delay)

        raise AIProviderError(last_error)


class DeepSeekProvider(BaseProvider):
    """ An OpenAI compatible chat completion endpoint. """

    default_api_url = 'https://api.deepseek.com/chat/completions'

    def complete(self, system_prompt, user_prompt):
        headers = {
            'Authorization': f"Bearer {self._config.api_key}",
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self._config.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': self._config.temperature,
            'stream': False,
            'response_format': {'type': 'json_object'}
        }

        data = self._post(self.api_url, headers, payload)
        self._record_openai_style_usage(data)

        try:
            return data['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError) as ex:
            raise AIProviderError(
                "The DeepSeek response did not contain a completion.") from ex


class OpenAIProvider(BaseProvider):
    """
    Same dialect as DeepSeek, but the current models reject sampling
    parameters and name the output cap ``max_completion_tokens``.
    """

    default_api_url = 'https://api.openai.com/v1/chat/completions'

    def complete(self, system_prompt, user_prompt):
        headers = {
            'Authorization': f"Bearer {self._config.api_key}",
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self._config.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_completion_tokens': 16000,
            'response_format': {
                'type': 'json_schema',
                'json_schema': {
                    'name': 'report_explanation',
                    'strict': True,
                    'schema': answer_schema()
                }
            }
        }

        data = self._post(self.api_url, headers, payload)
        self._record_openai_style_usage(data)

        try:
            choice = data['choices'][0]
        except (KeyError, IndexError, TypeError) as ex:
            raise AIProviderError(
                "The OpenAI response did not contain a completion.") from ex

        if choice.get('finish_reason') == 'length':
            LOG.warning("The OpenAI answer was truncated at the token limit.")

        content = (choice.get('message') or {}).get('content')

        if not content:
            refusal = (choice.get('message') or {}).get('refusal')
            if refusal:
                raise AIProviderError(
                    f"OpenAI declined to answer: {refusal}")
            raise AIProviderError(
                "The OpenAI response did not contain any text.")

        return content


class GeminiProvider(BaseProvider):
    """ The model name is part of the URL, so ``api_url`` is the root. """

    default_api_url = 'https://generativelanguage.googleapis.com/v1beta'

    def complete(self, system_prompt, user_prompt):
        url = (f"{self.api_url.rstrip('/')}/models/"
               f"{self._config.model}:generateContent")

        headers = {
            'x-goog-api-key': self._config.api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'systemInstruction': {
                'parts': [{'text': system_prompt}]
            },
            'contents': [{
                'role': 'user',
                'parts': [{'text': user_prompt}]
            }],
            'generationConfig': {
                'temperature': self._config.temperature,
                'responseMimeType': 'application/json',
                'responseSchema': answer_schema(upper_case_types=True)
            }
        }

        data = self._post(url, headers, payload)

        usage = data.get('usageMetadata') or {}
        if usage:
            # Reasoning is billed as output but reported separately.
            output = ((usage.get('candidatesTokenCount') or 0)
                      + (usage.get('thoughtsTokenCount') or 0))
            self.last_usage = (usage.get('promptTokenCount'), output)

        try:
            candidate = data['candidates'][0]
        except (KeyError, IndexError, TypeError) as ex:
            # A blocked prompt returns no candidates, only a reason.
            reason = (data.get('promptFeedback', {}).get('blockReason')
                      if isinstance(data, dict) else None)
            if reason:
                raise AIProviderError(
                    f"Gemini refused to answer the prompt: {reason}.") from ex
            raise AIProviderError(
                "The Gemini response did not contain a candidate.") from ex

        if candidate.get('finishReason') == 'MAX_TOKENS':
            LOG.warning("The Gemini answer was truncated at the token limit.")

        try:
            parts = candidate['content']['parts']
            return ''.join(part.get('text', '') for part in parts)
        except (KeyError, TypeError) as ex:
            raise AIProviderError(
                "The Gemini response did not contain any text.") from ex


class AnthropicProvider(BaseProvider):
    """
    Claude, through the Anthropic SDK rather than raw HTTP: it handles
    retries and error typing itself.
    """

    def complete(self, system_prompt, user_prompt):
        try:
            import anthropic
        except ImportError as ex:
            raise AIProviderError(
                "The 'anthropic' package is required for the Claude "
                "provider. Install it with 'pip install anthropic'.") from ex

        client_args = {'api_key': self._config.api_key,
                       'timeout': float(self._timeout)}
        if self._config.api_url:
            client_args['base_url'] = self._config.api_url

        client = anthropic.Anthropic(**client_args)

        # No temperature: the current Claude models reject it.
        try:
            response = client.messages.create(
                model=self._config.model,
                max_tokens=16000,
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_prompt}],
                output_config={
                    'effort': self._config.effort,
                    'format': {
                        'type': 'json_schema',
                        'schema': answer_schema()
                    }
                })
        except anthropic.AuthenticationError as ex:
            raise AIProviderError(
                "The Claude API key was rejected.") from ex
        except anthropic.RateLimitError as ex:
            raise AIProviderError(
                "The Claude API rate limit was reached.") from ex
        except anthropic.APITimeoutError as ex:
            raise AIProviderError(
                f"Claude did not answer within {self._timeout} "
                "seconds.") from ex
        except anthropic.APIStatusError as ex:
            raise AIProviderError(
                f"The Claude API answered with HTTP {ex.status_code}. "
                f"{str(ex.message)[:500]}") from ex
        except anthropic.APIConnectionError as ex:
            raise AIProviderError(
                f"Could not reach the Claude API: {ex}") from ex

        if response.usage:
            self.last_usage = (response.usage.input_tokens,
                               response.usage.output_tokens)

        if response.stop_reason == 'refusal':
            category = getattr(response.stop_details, 'category', None)
            raise AIProviderError(
                "Claude declined to answer this report"
                + (f" ({category})." if category else "."))

        text = next((block.text for block in response.content
                     if block.type == 'text'), None)

        if not text:
            raise AIProviderError(
                "The Claude response did not contain any text.")

        return text


PROVIDERS = {
    'anthropic': AnthropicProvider,
    'deepseek': DeepSeekProvider,
    'gemini': GeminiProvider,
    'openai': OpenAIProvider
}


def create_provider(model_config, timeout):
    provider_cls = PROVIDERS.get(model_config.provider)

    if not provider_cls:
        known = ', '.join(sorted(PROVIDERS))
        raise AIProviderError(
            f"Unknown AI provider '{model_config.provider}'. "
            f"Supported providers are: {known}.")

    return provider_cls(model_config, timeout)


def parse_json_response(text):
    """ Decode the answer, unwrapping a Markdown fence if one is there. """
    if not text:
        raise AIProviderError("The AI provider returned an empty answer.")

    cleaned = text.strip()

    if cleaned.startswith('```'):
        lines = cleaned.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]
        cleaned = '\n'.join(lines).strip()

    try:
        return json.loads(cleaned)
    except ValueError as ex:
        LOG.debug("Unparsable AI answer: %s", cleaned[:1000])
        raise AIProviderError(
            "The AI provider did not return valid JSON.") from ex
