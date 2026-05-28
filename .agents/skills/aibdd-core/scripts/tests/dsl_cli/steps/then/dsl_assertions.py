"""Then steps for dsl_reader features."""

from __future__ import annotations

from behave import then


def _entry_by_name(context, name: str):
    matches = [e for e in context.loaded_entries if e.name == name]
    assert matches, f"no entry named {name!r}; got {[e.name for e in context.loaded_entries]}"
    return matches[0]


@then("loaded entries count is {count:d}")
def step_assert_entries_count(context, count: int):
    actual = len(context.loaded_entries)
    assert actual == count, f"expected {count} entries, got {actual}"


@then('entry "{name}" has handler "{expected}"')
def step_assert_entry_handler(context, name: str, expected: str):
    e = _entry_by_name(context, name)
    assert e.handler == expected, f"{name}.handler: expected {expected!r}, got {e.handler!r}"


@then('entry "{name}" has target_part_path "{expected}"')
def step_assert_entry_target(context, name: str, expected: str):
    e = _entry_by_name(context, name)
    assert e.target_part_path == expected, (
        f"{name}.target_part_path mismatch:\n  expected: {expected}\n  actual:   {e.target_part_path}"
    )


@then('entry "{name}" has param_binding "{key}" with target "{expected}"')
def step_assert_param_binding(context, name: str, key: str, expected: str):
    e = _entry_by_name(context, name)
    assert key in e.param_bindings, (
        f"{name}.param_bindings missing key {key!r}; got {list(e.param_bindings)}"
    )
    assert e.param_bindings[key].target == expected, (
        f"{name}.param_bindings[{key}].target mismatch:\n  expected: {expected}\n  actual:   {e.param_bindings[key].target}"
    )


@then(
    'entry "{name}" has datatable_binding "{key}" with required {required_str:w} and default_value "{default}"'
)
def step_assert_datatable_binding(
    context, name: str, key: str, required_str: str, default: str
):
    e = _entry_by_name(context, name)
    assert key in e.datatable_bindings, (
        f"{name}.datatable_bindings missing key {key!r}; got {list(e.datatable_bindings)}"
    )
    db = e.datatable_bindings[key]
    expected_required = required_str.lower() == "true"
    assert db.required == expected_required, (
        f"{name}.datatable_bindings[{key}].required: expected {expected_required}, got {db.required}"
    )
    assert db.default_value == default, (
        f"{name}.datatable_bindings[{key}].default_value: expected {default!r}, got {db.default_value!r}"
    )


@then("the resolved parts set has exactly {count:d} items")
def step_assert_resolved_count(context, count: int):
    actual = len(context.resolved_parts)
    assert actual == count, f"expected {count} resolved parts, got {actual}"


@then('the resolved parts set contains "{expected}"')
def step_assert_resolved_contains(context, expected: str):
    assert expected in context.resolved_parts, (
        f"resolved parts set missing {expected!r}; got {context.resolved_parts}"
    )
