"""Then steps unique to L4 orchestrator features."""

from __future__ import annotations

from behave import then


@then("the second run's GenerationReport has 0 added entries")
def step_assert_second_run_zero_added(context):
    count = len(context.second_generation_report.added_entries)
    assert count == 0, (
        f"second run unexpectedly added {count} entries: "
        f"{[a.entry_name for a in context.second_generation_report.added_entries]}"
    )


@then('the eval-run EvalReport status is "{expected}"')
def step_assert_eval_run_status(context, expected: str):
    actual = context.eval_report.status
    assert actual == expected, (
        f"EvalReport.status: expected {expected!r}, got {actual!r}; "
        f"violations: {[v.rule_id for v in context.eval_report.violations]}"
    )


@then('the eval-run EvalReport violations include rule_id "{rule_id}"')
def step_assert_eval_run_includes_rule(context, rule_id: str):
    ids = [v.rule_id for v in context.eval_report.violations]
    assert rule_id in ids, (
        f"expected eval violations to include {rule_id!r}; got {ids}"
    )
