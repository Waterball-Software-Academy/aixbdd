"""When steps for writer features.

State carried on context:
  - context.routed_path: result of route_template_to_file()
  - context.buffered_template: a DSLInstructionTemplate accumulated by
    incremental Givens (handler / name / target_part_path / candidate
    bindings) so a single feature can describe a complex template across
    multiple step rows.
"""

from __future__ import annotations

from pathlib import Path

from behave import when

from dsl_cli.models import CandidateBinding, DSLInstructionTemplate
from dsl_cli.writer import append_templates, route_template_to_file


def _ensure_buffer(context):
    if getattr(context, "buffered_template", None) is None:
        context.buffered_template = DSLInstructionTemplate(
            handler="",
            name="",
            target_part_path="",
            source_spec_path=Path("__pending__"),
        )


@when('route_template_to_file routes a template with source_spec_path "{spec}"')
def step_route(context, spec: str):
    template = DSLInstructionTemplate(
        handler="x",
        name="x",
        target_part_path=f"{spec}#anchor",
        source_spec_path=Path(spec),
    )
    context.routed_path = route_template_to_file(template)


@when('I append a template skeleton with the following fields to "{relpath}"')
@when('I append a template skeleton with the following fields to "{relpath}":')
def step_append_with_fields(context, relpath: str):
    _ensure_buffer(context)
    fields = {row["field"]: row["value"] for row in context.table}
    context.buffered_template.handler = fields.get("handler", context.buffered_template.handler)
    context.buffered_template.name = fields.get("name", context.buffered_template.name)
    context.buffered_template.target_part_path = fields.get(
        "target_part_path", context.buffered_template.target_part_path
    )
    target = context.tmp_root / relpath
    append_templates(target, [context.buffered_template])
    context.last_file_path = target
    context.buffered_template = None  # reset for next step


@when("the template has candidate bindings")
@when("the template has candidate bindings:")
def step_add_candidate_bindings(context):
    _ensure_buffer(context)
    bindings = tuple(
        CandidateBinding(key=row["key"], target=row["target"]) for row in context.table
    )
    context.buffered_template.candidate_bindings = bindings


@when('I flush the template buffer to "{relpath}"')
def step_flush_template(context, relpath: str):
    target = context.tmp_root / relpath
    # Overwrite (the previous append already wrote without candidates; this
    # second step writes a fresh skeleton that *does* carry the candidates).
    target.write_text("")
    append_templates(target, [context.buffered_template])
    context.last_file_path = target
    context.buffered_template = None
