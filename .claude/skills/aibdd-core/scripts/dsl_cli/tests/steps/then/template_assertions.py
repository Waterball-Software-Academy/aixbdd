"""Then steps for L3 plugin features (operate on context.templates)."""

from __future__ import annotations

from behave import then


def _by_name(context, name: str):
    matches = [t for t in context.templates if t.name == name]
    assert matches, f"no template with name {name!r}; got {[t.name for t in context.templates]}"
    return matches[0]


@then('a template with name "{name}" exists with handler "{handler}"')
def step_assert_template_handler(context, name: str, handler: str):
    t = _by_name(context, name)
    assert t.handler == handler, (
        f"template {name}.handler: expected {handler!r}, got {t.handler!r}"
    )


@then('template "{name}" has candidate keys: {csv}')
def step_assert_candidate_keys(context, name: str, csv: str):
    t = _by_name(context, name)
    expected = [k.strip() for k in csv.split(",")]
    actual = [cb.key for cb in t.candidate_bindings]
    assert actual == expected, (
        f"template {name} candidate keys mismatch:\n"
        f"  expected: {expected}\n  actual:   {actual}"
    )


@then('template "{name}" candidate "{key}" has target "{expected}"')
def step_assert_candidate_target(context, name: str, key: str, expected: str):
    t = _by_name(context, name)
    matches = [cb for cb in t.candidate_bindings if cb.key == key]
    assert matches, f"template {name} has no candidate {key!r}"
    assert matches[0].target == expected, (
        f"template {name}.candidate[{key}].target mismatch:\n"
        f"  expected: {expected}\n  actual:   {matches[0].target}"
    )


@then('template "{name}" has target_part_path "{expected}"')
def step_assert_template_target_part_path(context, name: str, expected: str):
    t = _by_name(context, name)
    assert t.target_part_path == expected, (
        f"template {name}.target_part_path mismatch:\n"
        f"  expected: {expected}\n  actual:   {t.target_part_path}"
    )
