"""Then steps for eval-rules features."""

from __future__ import annotations

from behave import then


@then('EvalReport status is "{expected}"')
def step_assert_eval_status(context, expected: str):
    actual = context.eval_report.status
    assert actual == expected, (
        f"EvalReport.status: expected {expected!r}, got {actual!r}; "
        f"violations: {[v.rule_id for v in context.eval_report.violations]}"
    )


@then('a violation with rule_id "{rule_id}" is present')
def step_assert_violation_present(context, rule_id: str):
    ids = [v.rule_id for v in context.eval_report.violations]
    assert rule_id in ids, (
        f"expected a violation with rule_id {rule_id!r}; got {ids}"
    )


@then("no violations are present")
def step_assert_no_violations(context):
    assert context.eval_report.violations == [], (
        f"expected no violations; got: "
        f"{[(v.rule_id, v.message) for v in context.eval_report.violations]}"
    )


@then('no violation with rule_id "{rule_id}" is present')
def step_assert_no_violation_for_rule(context, rule_id: str):
    ids = [v.rule_id for v in context.eval_report.violations]
    assert rule_id not in ids, (
        f"expected no violation with rule_id {rule_id!r}; "
        f"but found: {[v.message for v in context.eval_report.violations if v.rule_id == rule_id]}"
    )
