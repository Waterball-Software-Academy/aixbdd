"""When step for evaluate()."""

from __future__ import annotations

from behave import when

from dsl_cli.eval_rules.rules import evaluate


@when("evaluate runs")
def step_evaluate(context):
    shared = getattr(context, "eval_shared_names", set())
    context.eval_report = evaluate(context.eval_entries_by_file, shared)
