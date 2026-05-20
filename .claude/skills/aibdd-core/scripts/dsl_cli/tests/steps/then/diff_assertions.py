"""Then steps for diff.py prefix-match feature."""

from __future__ import annotations

from behave import then


def _unresolved_targets(context) -> set[str]:
    return {p.target_part_path for p in context.unresolved}


@then('unresolved parts include "{target}"')
def step_assert_unresolved_includes(context, target: str):
    actual = _unresolved_targets(context)
    assert target in actual, (
        f"expected {target!r} in unresolved set, but unresolved = {actual}"
    )


@then('unresolved parts do not include "{target}"')
def step_assert_unresolved_excludes(context, target: str):
    actual = _unresolved_targets(context)
    assert target not in actual, (
        f"expected {target!r} NOT in unresolved set, but it is; unresolved = {actual}"
    )
