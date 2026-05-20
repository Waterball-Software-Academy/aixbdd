"""Then steps for the meta-feature on the fixture step."""

from __future__ import annotations

from behave import then


@then('the read content is "{expected}"')
def step_assert_read_content(context, expected: str):
    actual = context.read_content.rstrip("\n")
    assert actual == expected, (
        f"read content mismatch:\n  expected: {expected!r}\n  actual:   {actual!r}"
    )
