"""Then steps for preset_loader L1 features."""

from __future__ import annotations

from behave import then


@then('the loaded module exposes attribute "{attr}"')
def step_assert_module_attr(context, attr: str):
    assert hasattr(context.loaded_module, attr), (
        f"loaded module missing attribute {attr!r}; has {dir(context.loaded_module)}"
    )


@then("calling generate_templates with empty parts and empty context returns an empty list")
def step_assert_generate_templates_empty(context):
    result = context.loaded_module.generate_templates([], {})
    assert result == [], f"expected [], got {result!r}"


@then("the two loaded modules are not the same object")
def step_assert_two_distinct_modules(context):
    hist = context.loaded_modules_history
    assert len(hist) == 2, f"expected 2 loaded modules in history, got {len(hist)}"
    assert hist[0] is not hist[1], (
        "two loads returned the same module object — sys.modules cache leak?"
    )
