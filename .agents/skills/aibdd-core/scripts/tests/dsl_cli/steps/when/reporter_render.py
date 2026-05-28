"""When steps for reporter features."""

from __future__ import annotations

from pathlib import Path

from behave import when

from dsl_cli.models import AddedEntry, EvalReport, GenerationReport, Violation
from dsl_cli.reporter import render_eval_report, render_generation_report


@when("a GenerationReport with the following added entries is rendered")
@when("a GenerationReport with the following added entries is rendered:")
def step_render_gen_report(context):
    report = GenerationReport(
        added_entries=[
            AddedEntry(
                entry_name=row["entry_name"],
                target_file=Path(row["target_file"]),
                handler=row["handler"],
            )
            for row in context.table
        ]
    )
    context.rendered_generation_report = render_generation_report(report)


@when('an EvalReport with status "{status}" total_entries {total:d} and no violations is rendered')
def step_render_eval_report_pass(context, status: str, total: int):
    report = EvalReport(status=status, total_entries=total, violations=[])
    context.rendered_eval_report = render_eval_report(report)


@when('an EvalReport with status "{status}" and the following violations is rendered')
@when('an EvalReport with status "{status}" and the following violations is rendered:')
def step_render_eval_report_with_violations(context, status: str):
    violations = [
        Violation(
            rule_id=row["rule_id"],
            entry_name=row["entry_name"],
            entry_file=Path(row["entry_file"]),
            message=row["message"],
            hint=row["hint"] if row["hint"] else None,
        )
        for row in context.table
    ]
    report = EvalReport(status=status, total_entries=len(violations), violations=violations)
    context.rendered_eval_report = render_eval_report(report)
