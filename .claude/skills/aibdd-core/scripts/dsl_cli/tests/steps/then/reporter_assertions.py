"""Then steps for reporter features."""

from __future__ import annotations

from behave import then


@then('the rendered generation report contains "{needle}"')
def step_assert_gen_report_contains(context, needle: str):
    assert needle in context.rendered_generation_report, (
        f"rendered generation report missing {needle!r}; got:\n{context.rendered_generation_report}"
    )


@then('the rendered eval report contains "{needle}"')
def step_assert_eval_report_contains(context, needle: str):
    assert needle in context.rendered_eval_report, (
        f"rendered eval report missing {needle!r}; got:\n{context.rendered_eval_report}"
    )
