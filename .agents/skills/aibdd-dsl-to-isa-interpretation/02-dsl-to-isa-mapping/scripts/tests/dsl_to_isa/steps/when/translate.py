"""When steps for dsl_to_isa translation."""

from __future__ import annotations

from behave import when

from steps.given.extras import _run_translate


@when("dsl_to_isa translates the last dsl file")
def step_translate_last_dsl(context):
    _run_translate(context, context.last_file_path)


@when("dsl_to_isa runs")
def step_translate_runs(context):
    """Variant with no specific file — env-driven (TRUTH_BOUNDARY_PACKAGES_DIR)."""
    _run_translate(context, dsl_path=None)
