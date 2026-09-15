#!/usr/bin/env python3
# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------
"""
Explain a report with the models configured in a server_config.json, without
running a server. Useful for comparing models and iterating on the prompt.

Examples:

    # Every configured model, on a built-in sample.
    ./try_ai_explain.py --all

    # One model, against a real finding.
    ./try_ai_explain.py --model gemini-flash \\
        --file src/parser.c --line 214 \\
        --checker core.NullDereference \\
        --message "Dereference of null pointer"

    # Show the prompt without calling anyone.
    ./try_ai_explain.py --dry-run
"""

import argparse
import json
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

DEFAULT_CONFIG = os.path.expanduser("~/.codechecker/server_config.json")

SAMPLE_SOURCE = """\
#include <stdlib.h>
#include <string.h>

struct config {
    char *name;
    int   retries;
};

struct config *load_config(const char *path)
{
    struct config *cfg = malloc(sizeof(*cfg));

    if (!path)
        return NULL;

    cfg->name = strdup(path);
    cfg->retries = 3;

    return cfg;
}
"""

SAMPLE = {
    'checker': 'core.NullDereference',
    'message': "Access to field 'name' results in a dereference of a null "
               "pointer (loaded from variable 'cfg')",
    'file_path': 'sample/config.c',
    'line': 16,
    'column': 5,
    'analyzer': 'clangsa',
    'severity': 'HIGH',
    'path_events': [
        ("sample/config.c", 11,
         "Memory is allocated, 'malloc' may return a null pointer"),
        ("sample/config.c", 13, "Assuming 'path' is non-null"),
        ("sample/config.c", 16,
         "Access to field 'name' results in a dereference of a null pointer")
    ]
}


def _ai():
    """ Deferred so the repository paths are registered first. """
    for path in (os.path.join(REPO_ROOT, 'web', 'server'),
                 os.path.join(REPO_ROOT, 'web'),
                 REPO_ROOT):
        if path not in sys.path:
            sys.path.insert(0, path)

    from codechecker_server.ai import config, explain, prompt, providers
    return config, explain, prompt, providers


def load_config(path, timeout):
    """
    The ai section of a server_config.json, with $ENV: and $SECRET: keys
    resolved the way the server resolves them.
    """
    config, _, _, _ = _ai()

    if not os.path.exists(path):
        raise SystemExit(f"No such configuration file: {path}")

    with open(path, 'r', encoding='utf-8') as handle:
        raw = json.load(handle).get('ai')

    if not raw:
        raise SystemExit(f"{path} has no 'ai' section.")

    secrets_path = os.path.join(os.path.dirname(path), 'server_secrets.json')
    secrets = {}
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r', encoding='utf-8') as handle:
            secrets = json.load(handle)

    for model in raw.get('models', []):
        key = model.get('api_key', '')
        if key.startswith('$ENV:'):
            model['api_key'] = os.environ.get(key[5:-1], '')
        elif key.startswith('$SECRET:'):
            model['api_key'] = secrets.get(key[8:-1], '')

    # The tool is explicitly asking for an explanation, so the server's own
    # on/off switch does not apply.
    raw['enabled'] = True
    if timeout:
        raw['timeout'] = timeout

    return config.AIConfig(raw)


def build_context(args):
    """ The report context, from the arguments or the sample. """
    _, explain, _, _ = _ai()

    if not args.file:
        return explain.ReportContext(
            checker_name=SAMPLE['checker'],
            checker_message=SAMPLE['message'],
            file_path=SAMPLE['file_path'],
            line=SAMPLE['line'],
            column=SAMPLE['column'],
            analyzer_name=SAMPLE['analyzer'],
            severity=SAMPLE['severity'],
            file_content=SAMPLE_SOURCE,
            path_events=[explain.PathEvent(f, ln, msg)
                         for f, ln, msg in SAMPLE['path_events']])

    with open(args.file, 'r', encoding='utf-8', errors='ignore') as handle:
        source = handle.read()

    return explain.ReportContext(
        checker_name=args.checker,
        checker_message=args.message,
        file_path=args.file,
        line=args.line,
        column=args.column,
        analyzer_name=args.analyzer,
        severity=args.severity,
        file_content=source)


def render(model_id, explanation, elapsed):
    print()
    print('=' * 72)
    print(f"{model_id}  ({elapsed:.1f}s)")
    print('=' * 72)
    print(f"Verdict    : {explanation.verdict}")
    print(f"Confidence : {explanation.confidence}%")
    if explanation.input_tokens is not None:
        print(f"Usage      : {explanation.input_tokens} in + "
              f"{explanation.output_tokens} out")

    for title, body in (("Background", explanation.background),
                        ("Case for a true positive",
                         explanation.true_positive_case),
                        ("Case for a false positive",
                         explanation.false_positive_case)):
        print()
        print(title)
        print('-' * 72)
        print(body)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--config', default=DEFAULT_CONFIG,
                        help=f"Configuration to read models from. "
                             f"Default: {DEFAULT_CONFIG}")
    parser.add_argument('--model', action='append', dest='models',
                        help="Model id to query; repeatable. Defaults to the "
                             "configured default model.")
    parser.add_argument('--all', action='store_true',
                        help="Query every configured model.")
    parser.add_argument('--list', action='store_true',
                        help="List the configured models and exit.")
    parser.add_argument('--dry-run', action='store_true',
                        help="Print the prompt instead of calling a provider.")

    parser.add_argument('--file', help="Source file the report refers to.")
    parser.add_argument('--line', type=int, default=1)
    parser.add_argument('--column', type=int, default=0)
    parser.add_argument('--checker', default='unknown')
    parser.add_argument('--message', default='')
    parser.add_argument('--analyzer', default=None)
    parser.add_argument('--severity', default=None)

    parser.add_argument('--timeout', type=int, default=None)
    parser.add_argument('--max-source-lines', type=int, default=None)

    args = parser.parse_args()

    if args.file and not args.message:
        parser.error("--message is required together with --file.")

    context = build_context(args)

    if args.dry_run:
        _, _, prompt, _ = _ai()
        print(prompt.SYSTEM_PROMPT)
        print(prompt.build_user_prompt(
            context, args.max_source_lines or 400, 50))
        return 0

    cfg = load_config(args.config, args.timeout)
    if args.max_source_lines:
        cfg.max_source_lines = args.max_source_lines

    if args.list:
        for model in cfg.models:
            default = " (default)" if model.id == cfg.default_model else ""
            print(f"  {model.id:<16} {model.display_name}{default}")
        return 0

    if not cfg.models:
        raise SystemExit(
            f"No usable model in {args.config}; every entry lacks a key.")

    wanted = cfg.models if args.all else [
        m for m in cfg.models
        if m.id in (args.models or [cfg.default_model])]

    if not wanted:
        known = ', '.join(m.id for m in cfg.models)
        raise SystemExit(f"No such model. Configured: {known}")

    _, explain, _, providers = _ai()

    failures = 0
    for model in wanted:
        started = time.time()
        try:
            explanation = explain.explain_report(context, cfg, model.id)
        except providers.AIProviderError as ex:
            print(f"\n{model.id}: FAILED - {ex}", file=sys.stderr)
            failures += 1
            continue

        render(model.id, explanation, time.time() - started)

    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
