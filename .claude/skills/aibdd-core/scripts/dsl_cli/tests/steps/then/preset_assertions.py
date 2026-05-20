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
