"""When steps for spec_parsers/dispatcher.py."""

from __future__ import annotations

from behave import when

from shared.spec_parsers.dispatcher import dispatch_spec_parser


@when("dispatch_spec_parser is called on the last file")
def step_dispatch_last(context):
    context.dispatched_parser = dispatch_spec_parser(context.last_file_path)


@when('dispatch_spec_parser is called on the file aliased "{alias}"')
def step_dispatch_aliased(context, alias: str):
    context.dispatched_parser = dispatch_spec_parser(context.files[alias])


@when("dispatch_spec_parser is called on the last file and captures the exception")
def step_dispatch_capture(context):
    try:
        dispatch_spec_parser(context.last_file_path)
    except Exception as exc:
        context.captured_exception = exc
        return
    context.captured_exception = None
