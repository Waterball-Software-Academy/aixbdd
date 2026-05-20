"""When step for diff.compute_unresolved."""

from __future__ import annotations

from behave import when

from dsl_cli.diff import compute_unresolved


@when("compute_unresolved is called")
def step_compute_unresolved(context):
    context.unresolved = compute_unresolved(context.parts, context.resolved_targets)
