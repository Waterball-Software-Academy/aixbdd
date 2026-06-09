"""Then steps for dispatcher features."""

from __future__ import annotations

from behave import then


@then('the dispatched parser is an instance of "{type_name}"')
def step_assert_parser_type(context, type_name: str):
    actual = type(context.dispatched_parser).__name__
    assert actual == type_name, (
        f"expected dispatched parser type {type_name!r}, got {actual!r}"
    )
