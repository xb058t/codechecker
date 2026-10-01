# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------
"""
The EricAI client. EricAI serves its models through a LiteLLM proxy, which
speaks the OpenAI chat completion dialect and takes short-lived OAuth2 access
tokens: of the server's service principal, or of a signed in user.
"""

import base64
import json
import os
import shlex
import subprocess
import threading
import time

import requests

from codechecker_common.logger import get_logger

LOG = get_logger('server')

# Busy or briefly down, rather than refusing the request.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

MAX_ATTEMPTS = 3
BACKOFF_SCHEDULE = (1.0, 3.0)  # before the 2nd and 3rd


class AIProviderError(Exception):
    """ Raised when EricAI could not produce a usable answer. """


class OAuth2TokenCache:
    """
    EricAI access tokens, from the OAuth2 client credentials flow or from a
    ``token_command``. They live for about an hour, so one is shared by every
    request until it nears expiry.
    """

    # Renew this long before expiry, so a token never lapses mid-request.
    EXPIRY_MARGIN = 120  # seconds

    def __init__(self):
        self._lock = threading.Lock()
        self._tokens = {}

    # Assumed when a token does not tell its own expiry.
    DEFAULT_LIFETIME = 3000  # seconds

    @staticmethod
    def _key(ericai):
        if ericai.token_command:
            return (ericai.token_command,)
        return (ericai.token_url, ericai.client_id, ericai.scope)

    def get(self, ericai, timeout):
        # Held during the request, so concurrent explanations wait for one
        # token rather than each fetching their own.
        with self._lock:
            cached = self._tokens.get(self._key(ericai))
            if cached and cached[1] > time.monotonic() + self.EXPIRY_MARGIN:
                return cached[0]

            token, lifetime = self._request(ericai, timeout)
            self._tokens[self._key(ericai)] = \
                (token, time.monotonic() + lifetime)
            return token

    def invalidate(self, ericai):
        with self._lock:
            self._tokens.pop(self._key(ericai), None)

    @classmethod
    def _request(cls, ericai, timeout):
        """ A new token and its lifetime in seconds. """
        if ericai.token_command:
            return cls._run_token_command(ericai.token_command, timeout,
                                          ericai.token_command_dir)

        return cls._request_client_credentials(ericai, timeout)

    @classmethod
    def _run_token_command(cls, command, timeout, cwd=None):
        """
        The command prints the token on its standard output. It must not
        wait for an interactive login, which nobody would ever complete.
        """
        try:
            result = subprocess.run(shlex.split(command),
                                    capture_output=True,
                                    text=True,
                                    timeout=timeout,
                                    cwd=os.path.expanduser(cwd)
                                    if cwd else None,
                                    check=False)
        except (OSError, ValueError, subprocess.TimeoutExpired) as ex:
            raise AIProviderError(
                f"Could not run the EricAI token command: {ex}") from ex

        # Never the output: it is the token, or part of one.
        if result.returncode != 0:
            detail = (result.stderr or '').strip()[-300:]
            raise AIProviderError(
                "The EricAI token command failed with exit code "
                f"{result.returncode}. {detail}".strip())

        lines = (result.stdout or '').strip().splitlines()
        token = lines[-1].strip() if lines else ''
        if not token:
            raise AIProviderError(
                "The EricAI token command did not print a token.")

        return token, cls._jwt_lifetime(token)

    @classmethod
    def _jwt_lifetime(cls, token):
        """ Seconds until the ``exp`` claim, read without verification. """
        try:
            payload = token.split('.')[1]
            payload += '=' * (-len(payload) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload))
            return int(claims['exp'] - time.time())
        except (IndexError, KeyError, TypeError, ValueError):
            return cls.DEFAULT_LIFETIME

    @staticmethod
    def _request_client_credentials(ericai, timeout):
        """ A token of the server's service principal. """
        try:
            response = requests.post(ericai.token_url,
                                     data={
                                         'grant_type': 'client_credentials',
                                         'client_id': ericai.client_id,
                                         'client_secret':
                                             ericai.client_secret,
                                         'scope': ericai.scope
                                     },
                                     timeout=timeout,
                                     verify=ericai.verify)
        except requests.RequestException as ex:
            raise AIProviderError(
                f"Could not reach the OAuth2 token endpoint: {ex}") from ex

        try:
            data = response.json()
        except ValueError:
            data = {}

        token = data.get('access_token') if isinstance(data, dict) else None
        if response.status_code != 200 or not token:
            # Never the secret: only what the identity provider said.
            reason = data.get('error_description') or data.get('error') \
                if isinstance(data, dict) else None
            raise AIProviderError(
                "Could not get an OAuth2 access token for EricAI "
                f"(HTTP {response.status_code}). {reason or ''}".strip())

        try:
            lifetime = int(data.get('expires_in', 3600))
        except (TypeError, ValueError):
            lifetime = 3600

        return token, lifetime


OAUTH2_TOKENS = OAuth2TokenCache()


class EricAIClient:
    """ Asks one EricAI model for a completion. """

    def __init__(self, ericai_config, model_config, timeout):
        self._ericai = ericai_config
        self._model = model_config
        self._timeout = timeout

        # (input, output) tokens of the last completion, or None.
        self.last_usage = None

        # HTTP status of the last completion request, or None.
        self.last_status = None

        # The logged in user a request is made for, or None.
        self.on_behalf_of = None

    @property
    def api_url(self):
        """ The chat completion endpoint under the configured root. """
        url = self._ericai.api_url.rstrip('/')

        if url.endswith('/chat/completions'):
            return url

        return f"{url}/chat/completions"

    def complete(self, system_prompt, user_prompt):
        """ Send the prompts, return the raw answer as a JSON string. """
        try:
            return self._complete(system_prompt, user_prompt)
        except AIProviderError:
            # A token can be revoked before it expires; fetch a new one
            # and try once more.
            if self.last_status != 401:
                raise

        OAUTH2_TOKENS.invalidate(self._ericai)
        return self._complete(system_prompt, user_prompt)

    def _complete(self, system_prompt, user_prompt):
        payload = {
            'model': self._model.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': self._model.temperature,
            'stream': False,
            'response_format': {'type': 'json_object'}
        }

        data = self._post(self.api_url, self._headers(), payload)

        usage = data.get('usage') or {}
        if usage:
            self.last_usage = (usage.get('prompt_tokens'),
                               usage.get('completion_tokens'))

        try:
            choice = data['choices'][0]
            content = choice['message']['content']
        except (KeyError, IndexError, TypeError) as ex:
            raise AIProviderError(
                "The EricAI response did not contain a completion.") from ex

        if choice.get('finish_reason') == 'length':
            LOG.warning("The EricAI answer was truncated at the token limit.")

        return content

    def _headers(self):
        token = OAUTH2_TOKENS.get(self._ericai, self._timeout)
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        user = self._forwarded_user()
        if user:
            headers[self._ericai.user_header] = user

        return headers

    def _forwarded_user(self):
        """ The user to name in ``user_header``, as an e-mail address. """
        user = self.on_behalf_of
        if not self._ericai.user_header or not user:
            return None

        if '@' not in user and self._ericai.user_email_domain:
            user = f"{user}@{self._ericai.user_email_domain}"

        if '@' not in user:
            LOG.debug("Not forwarding user '%s': not an e-mail address.",
                      user)
            return None

        return user

    @staticmethod
    def _is_retryable(status_code):
        """ Whether a failed response is worth sending again. """
        return status_code in RETRYABLE_STATUS

    @staticmethod
    def _retry_delay(response, attempt):
        """ Retry-After when EricAI sends one, else the schedule. """
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
                                         timeout=self._timeout,
                                         verify=self._ericai.verify)
            except requests.Timeout as ex:
                raise AIProviderError(
                    f"EricAI did not answer within {self._timeout} "
                    "seconds.") from ex
            except requests.RequestException as ex:
                raise AIProviderError(
                    f"Could not reach EricAI: {ex}") from ex

            self.last_status = response.status_code

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as ex:
                    raise AIProviderError(
                        "EricAI returned a malformed response.") from ex

            # The body usually carries the real reason.
            detail = response.text[:500] if response.text else ''
            last_error = (
                f"EricAI answered with HTTP {response.status_code}. "
                f"{detail}")

            if not self._is_retryable(response.status_code):
                break

            if attempt < MAX_ATTEMPTS - 1:
                delay = self._retry_delay(response, attempt)
                LOG.info(
                    "EricAI answered with HTTP %s; retrying in %.1fs "
                    "(attempt %d of %d).", response.status_code, delay,
                    attempt + 1, MAX_ATTEMPTS)
                time.sleep(delay)

        raise AIProviderError(last_error)


def fetch_models(ericai, timeout):
    """ EricAI's model list: the entries of its OpenAI style /models. """
    root = ericai.api_url.rstrip('/')
    if root.endswith('/chat/completions'):
        root = root[:-len('/chat/completions')]

    token = OAUTH2_TOKENS.get(ericai, timeout)
    try:
        response = requests.get(f"{root}/models",
                                headers={'Authorization': f"Bearer {token}"},
                                timeout=timeout,
                                verify=ericai.verify)
    except requests.RequestException as ex:
        raise AIProviderError(f"Could not reach EricAI: {ex}") from ex

    if response.status_code == 401:
        # Revoked before it expired; the next call fetches a new one.
        OAUTH2_TOKENS.invalidate(ericai)

    if response.status_code != 200:
        raise AIProviderError(
            f"EricAI answered the model list with HTTP "
            f"{response.status_code}.")

    try:
        data = response.json()
    except ValueError as ex:
        raise AIProviderError(
            "EricAI returned a malformed model list.") from ex

    return data.get('data') if isinstance(data, dict) else data


def parse_json_response(text):
    """ Decode the answer, unwrapping a Markdown fence if one is there. """
    if not text:
        raise AIProviderError("EricAI returned an empty answer.")

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
            "EricAI did not return valid JSON.") from ex
