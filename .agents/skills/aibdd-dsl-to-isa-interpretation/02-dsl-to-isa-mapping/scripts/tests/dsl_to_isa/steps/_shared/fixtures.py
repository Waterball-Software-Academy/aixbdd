"""Shared fixture steps.

`Given a temporary file at "<relpath>" with content`:
    write doc string to context.tmp_root/<relpath>; store path in
    context.last_file_path.

`Given a temporary file at "<relpath>" with content (saved as "<alias>")`:
    same plus stash under context.files[alias] (for multi-file scenarios where
    context.last_file_path would otherwise be overwritten by subsequent files).

Behave 1.3 quirk: when a Gherkin step is followed by a doc string ('''...'''),
the parser keeps the trailing ':' in the step text used for matching. So every
step decorator that may be used with a doc string follow-up is double-decorated
with both no-colon and with-colon variants. Apply this pattern to any future
step that takes a doc string.
"""

from __future__ import annotations

from pathlib import Path

from behave import given


def _write_file(context, relpath: str) -> Path:
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text)
    context.last_file_path = target
    return target


@given('a temporary file at "{relpath}" with content')
@given('a temporary file at "{relpath}" with content:')
def step_create_temp_file_with_content(context, relpath: str):
    _write_file(context, relpath)


@given('a temporary file at "{relpath}" with content (saved as "{alias}")')
@given('a temporary file at "{relpath}" with content (saved as "{alias}"):')
def step_create_temp_file_with_alias(context, relpath: str, alias: str):
    target = _write_file(context, relpath)
    context.files[alias] = target
