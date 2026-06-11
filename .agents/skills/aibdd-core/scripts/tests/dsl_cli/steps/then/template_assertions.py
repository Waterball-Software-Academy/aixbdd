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


@then('template "{name}" param_binding "{key}" has target "{expected}"')
def step_assert_param_binding_target(context, name: str, key: str, expected: str):
    t = _by_name(context, name)
    assert key in t.param_bindings, (
        f"template {name} has no param_binding {key!r}; got {list(t.param_bindings)}"
    )
    actual = t.param_bindings[key].target
    assert actual == expected, (
        f"template {name}.param_bindings[{key}].target mismatch:\n"
        f"  expected: {expected}\n  actual:   {actual}"
    )


@then('template "{name}" has no param_binding "{key}"')
def step_assert_no_param_binding(context, name: str, key: str):
    t = _by_name(context, name)
    assert key not in t.param_bindings, (
        f"template {name} should NOT have param_binding {key!r}, but it does; "
        f"got {list(t.param_bindings)}"
    )


@then('template "{name}" has target_part_path "{expected}"')
def step_assert_template_target_part_path(context, name: str, expected: str):
    t = _by_name(context, name)
    assert t.target_part_path == expected, (
        f"template {name}.target_part_path mismatch:\n"
        f"  expected: {expected}\n  actual:   {t.target_part_path}"
    )


@then('template "{name}" has no datatable_binding "{key}"')
def step_assert_no_datatable_binding(context, name: str, key: str):
    t = _by_name(context, name)
    assert key not in t.datatable_bindings, (
        f"template {name} should NOT have datatable_binding {key!r}, but it does"
    )


@then('template "{name}" datatable_binding "{key}" has required {expected}')
def step_assert_datatable_required(context, name: str, key: str, expected: str):
    t = _by_name(context, name)
    assert key in t.datatable_bindings, (
        f"template {name} has no datatable_binding {key!r}; got {list(t.datatable_bindings)}"
    )
    expected_bool = expected.strip().lower() == "true"
    actual = t.datatable_bindings[key].required
    assert actual == expected_bool, (
        f"template {name}.datatable_bindings[{key}].required: expected {expected_bool}, got {actual}"
    )


@then('template "{name}" datatable_binding "{key}" has default_value "{expected}"')
def step_assert_datatable_default_value(context, name: str, key: str, expected: str):
    t = _by_name(context, name)
    assert key in t.datatable_bindings, (
        f"template {name} has no datatable_binding {key!r}; got {list(t.datatable_bindings)}"
    )
    actual = t.datatable_bindings[key].default_value
    assert actual == expected, (
        f"template {name}.datatable_bindings[{key}].default_value: expected {expected!r}, got {actual!r}"
    )


@then('template "{name}" datatable_binding "{key}" has target "{expected}"')
def step_assert_datatable_target(context, name: str, key: str, expected: str):
    t = _by_name(context, name)
    assert key in t.datatable_bindings, (
        f"template {name} has no datatable_binding {key!r}; got {list(t.datatable_bindings)}"
    )
    actual = t.datatable_bindings[key].target
    assert actual == expected, (
        f"template {name}.datatable_bindings[{key}].target mismatch:\n"
        f"  expected: {expected}\n  actual:   {actual}"
    )
