"""Shared exception-capture assertion steps.

Cross-capability plumbing: any suite whose ``When`` step stashes a raised
error on ``context.captured_exception`` can assert on it with these ``Then``
steps. Used by spec_parsers (dispatch/parse failures) and dsl_cli
(preset-loader load errors). The capturing ``When`` step is suite-specific and
lives with its own capability.
"""

from __future__ import annotations

from behave import then


@then('the captured exception is of type "{type_name}"')
def step_assert_exception_type(context, type_name: str):
    exc = context.captured_exception
    assert exc is not None, "no exception was captured"
    assert type(exc).__name__ == type_name, (
        f"expected exception type {type_name!r}, got {type(exc).__name__!r}: {exc}"
    )


@then('the captured exception message mentions "{needle}"')
def step_assert_exception_message(context, needle: str):
    exc = context.captured_exception
    assert exc is not None, "no exception was captured"
    assert needle in str(exc), (
        f"exception message {str(exc)!r} does not mention {needle!r}"
    )
