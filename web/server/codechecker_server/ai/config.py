# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------
"""
The ``ai`` section of ``server_config.json``.
See docs/web/server_config.md for the reference.
"""

from codechecker_common.logger import get_logger

LOG = get_logger('server')

DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_MAX_SOURCE_LINES = 400
DEFAULT_MAX_PATH_EVENTS = 50


class AIModelConfig:
    """ One model the server may use. """

    def __init__(self, raw):
        if 'id' not in raw:
            raise ValueError("An AI model entry is missing the 'id' field.")
        if 'provider' not in raw:
            raise ValueError(
                f"AI model '{raw['id']}' is missing the 'provider' field.")

        self.id = raw['id']
        self.display_name = raw.get('display_name', self.id)
        self.provider = raw['provider']

        self.model = raw.get('model', self.id)
        self.api_key = raw.get('api_key')

        # Overrides the provider's endpoint, for a proxy or gateway.
        self.api_url = raw.get('api_url')

        # Both are ignored by providers that reject them.
        self.temperature = raw.get('temperature', 0.2)
        self.effort = raw.get('effort', 'medium')

    @property
    def is_usable(self):
        return bool(self.api_key)


class AIConfig:
    def __init__(self, raw=None):
        raw = raw or {}

        self.enabled = raw.get('enabled', False)
        self.timeout = raw.get('timeout', DEFAULT_TIMEOUT)
        self.max_source_lines = raw.get('max_source_lines',
                                        DEFAULT_MAX_SOURCE_LINES)
        self.max_path_events = raw.get('max_path_events',
                                       DEFAULT_MAX_PATH_EVENTS)

        self.models = []
        for entry in raw.get('models', []):
            try:
                model = AIModelConfig(entry)
            except ValueError as ex:
                LOG.warning("Ignoring invalid AI model configuration: %s", ex)
                continue

            if not model.is_usable:
                # The shipped config lists these keyless on purpose.
                if self.enabled:
                    LOG.warning(
                        "AI model '%s' has no API key configured, skipping "
                        "it. Set it through $ENV:...$ or $SECRET:...$ in "
                        "server_config.json.", model.id)
                continue

            self.models.append(model)

        configured_default = raw.get('default_model')
        if configured_default and not self.get_model(configured_default):
            if self.enabled:
                LOG.warning(
                    "The configured default AI model '%s' is not available, "
                    "falling back to the first usable model.",
                    configured_default)
            configured_default = None

        self.default_model = configured_default or (
            self.models[0].id if self.models else None)

        if self.enabled and not self.models:
            LOG.warning("AI report explanation is enabled but no usable model "
                        "is configured; the feature stays turned off.")

    @property
    def is_available(self):
        """ On, with at least one usable model. """
        return self.enabled and bool(self.models)

    def get_model(self, model_id):
        """ ``model_id``, or the default when empty. None if unknown. """
        if not model_id:
            model_id = self.default_model

        return next((m for m in self.models if m.id == model_id), None)
