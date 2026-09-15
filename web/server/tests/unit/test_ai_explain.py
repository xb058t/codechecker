# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

""" Test the AI report explanation layer. """


import unittest

from codechecker_server.ai import providers
from codechecker_server.ai.config import AIConfig
from codechecker_server.ai.explain import (
    PathEvent, ReportContext, explain_report)
from codechecker_server.ai.prompt import (
    ANSWER_FIELDS, VERDICTS, answer_schema, build_source_window,
    format_bug_path)


class SourceWindowTestCase(unittest.TestCase):
    """
    The excerpt handed to the model must be centred on the reported line.
    A prefix truncation would routinely miss the finding altogether.
    """

    def test_window_is_centred_on_the_report(self):
        content = "\n".join(f"line {i}" for i in range(1, 5001))

        text, start, end = build_source_window(content, 4200, 100)

        self.assertLessEqual(start, 4200)
        self.assertGreaterEqual(end, 4200)
        self.assertIn("line 4200", text)
        self.assertEqual(end - start + 1, 100)

    def test_whole_file_returned_when_short(self):
        text, start, end = build_source_window("a\nb\nc", 2, 400)

        self.assertEqual((start, end), (1, 3))
        self.assertTrue(text.splitlines()[1].endswith("| b"))

    def test_window_shifts_back_at_end_of_file(self):
        content = "\n".join(f"line {i}" for i in range(1, 201))

        _, start, end = build_source_window(content, 199, 50)

        self.assertEqual((start, end), (151, 200))

    def test_missing_source(self):
        self.assertEqual(build_source_window("", 1, 10), ('', 0, 0))
        self.assertEqual(build_source_window(None, 1, 10), ('', 0, 0))


class BugPathTestCase(unittest.TestCase):
    """ The analyser's own reasoning is the key triage context. """

    def setUp(self):
        self.events = [
            PathEvent("a.c", 10, "Assuming 'p' is null"),
            PathEvent("a.c", 12, "Dereference of null pointer")]

    def test_events_are_numbered_with_locations(self):
        out = format_bug_path(self.events, 50)

        self.assertIn("1. [a.c:10] Assuming 'p' is null", out)
        self.assertIn("2. [a.c:12] Dereference of null pointer", out)

    def test_long_paths_are_truncated(self):
        out = format_bug_path(self.events, 1)

        self.assertIn("1 further steps omitted", out)

    def test_empty_path_is_stated_explicitly(self):
        self.assertIn("did not record", format_bug_path([], 50))


class ResponseParsingTestCase(unittest.TestCase):
    """ Models do not always honour a request for raw JSON. """

    def test_plain_json(self):
        self.assertEqual(providers.parse_json_response('{"a": 1}'), {"a": 1})

    def test_markdown_fenced_json(self):
        self.assertEqual(
            providers.parse_json_response('```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(
            providers.parse_json_response('```\n{"a": 1}\n```'), {"a": 1})

    def test_unusable_answers_raise(self):
        for bad in ('', 'not json at all'):
            with self.assertRaises(providers.AIProviderError):
                providers.parse_json_response(bad)


class AnswerSchemaTestCase(unittest.TestCase):
    """
    One schema pins the answer for every provider, in two dialects.
    """

    def test_every_field_is_required(self):
        schema = answer_schema()

        self.assertEqual(set(schema['required']), set(ANSWER_FIELDS))
        self.assertEqual(set(schema['properties']), set(ANSWER_FIELDS))

    def test_standard_dialect(self):
        schema = answer_schema()

        self.assertEqual(schema['type'], 'object')
        self.assertEqual(schema['properties']['confidence']['type'],
                         'integer')
        self.assertFalse(schema['additionalProperties'])

    def test_gemini_dialect(self):
        """ Gemini wants upper case types and rejects additionalProperties. """
        schema = answer_schema(upper_case_types=True)

        self.assertEqual(schema['type'], 'OBJECT')
        self.assertEqual(schema['properties']['confidence']['type'],
                         'INTEGER')
        self.assertNotIn('additionalProperties', schema)

    def test_verdict_enum_matches_the_accepted_verdicts(self):
        enum = answer_schema()['properties']['verdict']['enum']

        self.assertEqual(set(enum), set(VERDICTS))


class RetryDecisionTestCase(unittest.TestCase):
    """
    A busy provider is worth another try; an empty wallet is not.
    """

    def setUp(self):
        self.is_retryable = providers.BaseProvider._is_retryable

    def test_transient_failures_are_retried(self):
        for status in (429, 500, 502, 503, 504):
            self.assertTrue(self.is_retryable(status, 'overloaded'), status)

    def test_client_errors_are_not_retried(self):
        for status in (400, 401, 403, 404, 422):
            self.assertFalse(self.is_retryable(status, ''), status)

    def test_exhausted_quota_is_not_retried(self):
        """ These arrive as 429/402 but can never succeed on a retry. """
        for body in ('{"error":{"code":"insufficient_quota"}}',
                     '{"error":{"code":"credit_balance_exhausted"}}',
                     '{"error":{"message":"Insufficient Balance"}}',
                     'You exceeded your current quota'):
            self.assertFalse(self.is_retryable(429, body), body)

    def test_overload_is_retried_despite_sharing_the_status(self):
        overloaded = ('{"error":{"code":503,"message":"This model is '
                      'currently experiencing high demand."}}')
        self.assertTrue(self.is_retryable(503, overloaded))


class RetryDelayTestCase(unittest.TestCase):
    """ Retry-After wins over the built-in backoff when it is usable. """

    class FakeResponse:
        def __init__(self, retry_after=None):
            self.headers = {}
            if retry_after is not None:
                self.headers['Retry-After'] = retry_after

    def test_backoff_schedule_when_no_header(self):
        delay = providers.BaseProvider._retry_delay(self.FakeResponse(), 0)
        self.assertEqual(delay, providers.BACKOFF_SCHEDULE[0])

    def test_retry_after_is_honoured(self):
        delay = providers.BaseProvider._retry_delay(
            self.FakeResponse('7'), 0)
        self.assertEqual(delay, 7.0)

    def test_retry_after_is_capped(self):
        delay = providers.BaseProvider._retry_delay(
            self.FakeResponse('9000'), 0)
        self.assertEqual(delay, 30.0)

    def test_http_date_retry_after_falls_back(self):
        delay = providers.BaseProvider._retry_delay(
            self.FakeResponse('Wed, 21 Oct 2026 07:28:00 GMT'), 1)
        self.assertEqual(delay, providers.BACKOFF_SCHEDULE[1])

    def test_attempt_beyond_schedule_is_clamped(self):
        delay = providers.BaseProvider._retry_delay(self.FakeResponse(), 99)
        self.assertEqual(delay, providers.BACKOFF_SCHEDULE[-1])


class ConfigTestCase(unittest.TestCase):
    """ The feature must stay off unless it is fully configured. """

    def test_absent_section_disables_the_feature(self):
        self.assertFalse(AIConfig({}).is_available)
        self.assertFalse(AIConfig(None).is_available)

    def test_model_without_key_is_not_offered(self):
        cfg = AIConfig({"enabled": True, "models": [
            {"id": "m", "provider": "deepseek", "api_key": ""}]})

        self.assertFalse(cfg.is_available)
        self.assertEqual(cfg.models, [])

    def test_usable_model_becomes_the_default(self):
        cfg = AIConfig({"enabled": True, "models": [
            {"id": "m", "provider": "deepseek", "api_key": "k"}]})

        self.assertTrue(cfg.is_available)
        self.assertEqual(cfg.default_model, "m")

    def test_unknown_default_falls_back(self):
        cfg = AIConfig({"enabled": True, "default_model": "nope", "models": [
            {"id": "m", "provider": "deepseek", "api_key": "k"}]})

        self.assertEqual(cfg.default_model, "m")

    def test_invalid_entries_are_skipped(self):
        cfg = AIConfig({"enabled": True, "models": [
            {"id": "no-provider", "api_key": "k"},
            {"provider": "deepseek", "api_key": "k"},
            {"id": "good", "provider": "deepseek", "api_key": "k"}]})

        self.assertEqual([m.id for m in cfg.models], ["good"])


class FakeProvider:
    """ Stands in for a real completion endpoint. """

    last_prompts = {}

    def __init__(self, _model_config, _timeout):
        self.last_usage = (1234, 567)

    def complete(self, system_prompt, user_prompt):
        FakeProvider.last_prompts = {'system': system_prompt,
                                     'user': user_prompt}
        return ('```json\n'
                '{"background": "The checker flags a null dereference.",'
                ' "verdict": "likely true positive",'
                ' "confidence": 0.9,'
                ' "true_positive_case": "p is never checked.",'
                ' "false_positive_case": "None apparent."}\n'
                '```')


class ExplainReportTestCase(unittest.TestCase):
    """ The full path from a report context to a structured explanation. """

    def setUp(self):
        self.__original = providers.PROVIDERS.copy()
        providers.PROVIDERS['deepseek'] = FakeProvider

        self.config = AIConfig({"enabled": True, "models": [
            {"id": "deepseek-chat", "provider": "deepseek",
             "api_key": "k"}]})

        self.context = ReportContext(
            checker_name="core.NullDereference",
            checker_message="Dereference of null pointer",
            file_path="src/a.c",
            line=12,
            column=5,
            analyzer_name="clangsa",
            severity="HIGH",
            file_content="\n".join(f"line {i}" for i in range(1, 100)),
            checker_documentation="doc_url: http://example.com",
            path_events=[PathEvent("src/a.c", 10, "Assuming 'p' is null")])

    def tearDown(self):
        providers.PROVIDERS.clear()
        providers.PROVIDERS.update(self.__original)

    def test_answer_is_normalised(self):
        result = explain_report(self.context, self.config)

        self.assertEqual(result.verdict, "LIKELY_TRUE_POSITIVE")
        # A probability is accepted as well as a percentage.
        self.assertEqual(result.confidence, 90)
        self.assertEqual(result.model, "deepseek-chat")
        self.assertIn("null dereference", result.background)

    def test_usage_is_carried_through(self):
        result = explain_report(self.context, self.config)

        self.assertEqual(result.input_tokens, 1234)
        self.assertEqual(result.output_tokens, 567)

    def test_prompt_carries_the_triage_context(self):
        explain_report(self.context, self.config)
        prompt = FakeProvider.last_prompts['user']

        for needle in ("core.NullDereference", "src/a.c:12:5", "clangsa",
                       "HIGH", "Assuming 'p' is null", "doc_url",
                       "the report is on line 12"):
            self.assertIn(needle, prompt)

    def test_disabled_server_is_rejected(self):
        with self.assertRaises(providers.AIProviderError) as ctx:
            explain_report(self.context, AIConfig({}))

        self.assertIn("not enabled", str(ctx.exception))

    def test_unknown_provider_is_reported(self):
        config = AIConfig({"enabled": True, "models": [
            {"id": "m", "provider": "nope", "api_key": "k"}]})

        with self.assertRaises(providers.AIProviderError) as ctx:
            explain_report(self.context, config)

        self.assertIn("Unknown AI provider", str(ctx.exception))

    def test_unknown_model_is_reported(self):
        with self.assertRaises(providers.AIProviderError) as ctx:
            explain_report(self.context, self.config, "no-such-model")

        self.assertIn("not available", str(ctx.exception))
