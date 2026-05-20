"""When steps that exercise the fixture step itself (meta-feature)."""

from __future__ import annotations

from behave import when


@when("the file at context.last_file_path is read")
def step_read_last_file(context):
    context.read_content = context.last_file_path.read_text()


@when('the file at context.files["{alias}"] is read')
def step_read_aliased_file(context, alias: str):
    context.read_content = context.files[alias].read_text()
