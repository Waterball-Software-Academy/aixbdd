"""web-service preset's part-to-DSL plugin.

Contract: `generate_templates(parts, context) -> list[DSLInstructionTemplate]`.

Mapping owned by this preset:
  - ApiOperationPart →
      operation-invoke
      operation-response-success-and-failure
      operation-response-success-readmodel   (only if the response has body properties)
  - TablePart →
      state-builder
      state-verifier
  - RefPart →
      state-relationship-verifier

Per spec.md / Policy 2 + Risk R5, this plugin is the SSOT for:
  - which handlers each part-kind expands to
  - the name auto-gen rule (<operationId>.<handler> for OpenAPI,
    <table_name>.<handler> for DBML)
  - the binding target URI scheme each handler emits:
      * operation-invoke / response-success-and-failure → OpenAPI spec anchor
      * operation-response-success-readmodel            → `response:` JSONPath
      * state-builder / state-verifier / state-relationship-verifier
                                                        → DBML spec anchor

core's `eval_rules/` does NOT re-check handler→scheme mapping. We guarantee
scheme legality constructively here.
"""

from __future__ import annotations

from dsl_cli.models import (
    ApiOperationPart,
    CandidateBinding,
    DatatableBinding,
    DSLInstructionTemplate,
    RefPart,
    TablePart,
)


def generate_templates(parts, context):
    templates: list[DSLInstructionTemplate] = []
    for part in parts:
        if isinstance(part, ApiOperationPart):
            templates.extend(_for_api_operation(part))
        elif isinstance(part, TablePart):
            templates.extend(_for_table(part))
        elif isinstance(part, RefPart):
            templates.extend(_for_ref(part))
        # Unknown part kinds are silently skipped: a future preset that adds
        # new spec_parsers can layer in without disturbing existing ones.
    return templates


# ---- ApiOperationPart fan-out ---------------------------------------------


def _for_api_operation(part):
    op_id = part.operation_id or _fallback_op_id(part)
    invoke = DSLInstructionTemplate(
        handler="operation-invoke",
        name=f"{op_id}.operation-invoke",
        target_part_path=part.target_part_path,
        source_spec_path=part.spec_file,
        candidate_bindings=tuple(
            CandidateBinding(key=ri.name, target=ri.target_part_path)
            for ri in part.request_inputs
        ),
    )
    response_status = DSLInstructionTemplate(
        handler="operation-response-success-and-failure",
        name=f"{op_id}.operation-response-success-and-failure",
        target_part_path=f"{part.target_part_path}/responses/200",
        source_spec_path=part.spec_file,
        candidate_bindings=(),
    )
    out = [invoke, response_status]
    if part.response_properties:
        readmodel = DSLInstructionTemplate(
            handler="operation-response-success-readmodel",
            name=f"{op_id}.operation-response-success-readmodel",
            target_part_path=(
                f"{part.target_part_path}/responses/200/content/application~1json/schema"
            ),
            source_spec_path=part.spec_file,
            candidate_bindings=tuple(
                CandidateBinding(key=rp.name, target=f"response:{rp.json_path}")
                for rp in part.response_properties
            ),
        )
        out.append(readmodel)
    return out


def _fallback_op_id(part):
    return f"{part.method}_{part.path_escaped}"


# ---- TablePart fan-out ----------------------------------------------------


def _for_table(part):
    not_null_names = {c.name for c in part.not_null_columns}
    builder = DSLInstructionTemplate(
        handler="state-builder",
        name=f"{part.table_name}.state-builder",
        target_part_path=part.target_part_path,
        source_spec_path=part.spec_file,
        candidate_bindings=tuple(
            CandidateBinding(key=c.name, target=c.target_part_path)
            for c in part.columns
            if c.name not in not_null_names
        ),
        datatable_bindings={
            c.name: DatatableBinding(
                target=c.target_part_path,
                required=False,
                default_value=c.default_value if c.has_default else "<FILL IN>",
            )
            for c in part.not_null_columns
            if not (c.is_pk and c.has_increment)
        },
    )
    verifier = DSLInstructionTemplate(
        handler="state-verifier",
        name=f"{part.table_name}.state-verifier",
        target_part_path=part.target_part_path,
        source_spec_path=part.spec_file,
        candidate_bindings=tuple(
            CandidateBinding(key=c.name, target=c.target_part_path)
            for c in part.columns
        ),
    )
    return [builder, verifier]


def _for_ref(part):
    relation_token = "to" if part.operator == ">" else "link"
    verifier = DSLInstructionTemplate(
        handler="state-relationship-verifier",
        name=(
            f"{part.from_table}_{part.from_column}_"
            f"{relation_token}_{part.to_table}_{part.to_column}.state-relationship-verifier"
        ),
        target_part_path=part.target_part_path,
        source_spec_path=part.spec_file,
        candidate_bindings=(
            CandidateBinding(
                key=f"{part.from_table}_{part.from_column}",
                target=part.from_target_part_path,
            ),
            CandidateBinding(
                key=f"{part.to_table}_{part.to_column}",
                target=part.to_target_part_path,
            ),
        ),
    )
    return [verifier]
