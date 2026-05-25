"""Dataclass + Enum contracts shared across dsl_cli modules.

These are pure structures; no I/O, no logic. They appear in the public surface
of spec_parsers, preset plugin, writer, eval_rules, reporter, and orchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal


# ---------- Part hierarchy (output of spec_parsers) ----------


class PartKind(str, Enum):
    api_operation = "api_operation"
    dbml_table = "dbml_table"
    dbml_ref = "dbml_ref"


@dataclass(frozen=True)
class Part:
    """A locatable element inside a Contract / Data spec.

    `target_part_path` is the canonical identity used by diff.py for the
    resolve-vs-unresolved set difference (see Phase 5).
    """

    kind: PartKind
    spec_file: Path
    target_part_path: str


@dataclass(frozen=True)
class RequestInput:
    name: str
    source: Literal["path", "query", "body", "header", "cookie"]
    required: bool
    target_part_path: str


@dataclass(frozen=True)
class ResponseProp:
    name: str
    json_path: str
    target_part_path: str


@dataclass(frozen=True)
class ApiOperationPart(Part):
    path: str
    path_escaped: str  # RFC 6901 escaped (/ → ~1) for use inside target_part_path
    method: Literal["get", "post", "put", "patch", "delete", "options", "head"]
    operation_id: str
    request_inputs: tuple[RequestInput, ...] = ()
    response_properties: tuple[ResponseProp, ...] = ()


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    nullable: bool
    is_pk: bool
    has_default: bool
    target_part_path: str
    default_value: str | None = None
    has_increment: bool = False


@dataclass(frozen=True)
class DbmlTablePart(Part):
    table_name: str
    columns: tuple[Column, ...] = ()
    not_null_columns: tuple[Column, ...] = ()


@dataclass(frozen=True)
class DbmlRefPart(Part):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    operator: Literal[">", "-"]
    from_target_part_path: str
    to_target_part_path: str


# ---------- DSL entry / template structures ----------


@dataclass
class ParamBinding:
    """`param_bindings[<key>]` — required-by-definition (key MUST appear in format).

    Schema lives on the YAML side as `{<key>: {target: ...}}`.
    """

    target: str


@dataclass
class DatatableBinding:
    """`datatable_bindings[<key>]` — required-ness is explicit; optional may have default."""

    target: str
    required: bool
    default_value: str | None = None


@dataclass(frozen=True)
class CandidateBinding:
    """A spec-derived binding candidate listed as a YAML comment in the HARNESS skeleton.

    SEMANTIC writers pick each candidate and place it in either `param_bindings`
    or `datatable_bindings`, then delete the candidate comment block. Plugins
    emit these when they know about a binding but cannot decide its placement.
    """

    key: str
    target: str


@dataclass
class DSLInstructionTemplate:
    """HARNESS-phase skeleton emitted by the preset plugin.

    `format` is the `<FILL IN>` placeholder; `name` is plugin auto-gen
    (`<spec-native-id>.<handler>`); `param_bindings` and `datatable_bindings`
    default to empty dicts and SEMANTIC fills them from `candidate_bindings`.

    `source_spec_path` drives writer.route_template_to_file() to decide which
    `*.dsl.yml` to land in.
    """

    handler: str
    name: str
    target_part_path: str
    source_spec_path: Path
    candidate_bindings: tuple[CandidateBinding, ...] = ()
    param_bindings: dict[str, ParamBinding] = field(default_factory=dict)
    datatable_bindings: dict[str, DatatableBinding] = field(default_factory=dict)
    format: str = "<FILL IN>"


@dataclass
class DSLEntry:
    """A fully-resolved entry loaded from `*.dsl.yml` (SEMANTIC-filled).

    Identical surface to DSLInstructionTemplate minus `candidate_bindings`
    (those are HARNESS-only and never persist) and `source_spec_path` (not
    stored on disk; the entry's `target_part_path` carries spec linkage).
    """

    handler: str
    name: str
    target_part_path: str
    format: str
    param_bindings: dict[str, ParamBinding] = field(default_factory=dict)
    datatable_bindings: dict[str, DatatableBinding] = field(default_factory=dict)


# ---------- Reports ----------


@dataclass(frozen=True)
class AddedEntry:
    entry_name: str
    target_file: Path
    handler: str


@dataclass
class GenerationReport:
    added_entries: list[AddedEntry] = field(default_factory=list)
    skipped_parts: list[str] = field(default_factory=list)
    processed_specs: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class Violation:
    rule_id: str
    entry_name: str
    entry_file: Path
    message: str
    severity: Literal["error", "warning"] = "error"
    hint: str | None = None


@dataclass
class EvalReport:
    status: Literal["PASS", "FAIL"]
    total_entries: int
    violations: list[Violation] = field(default_factory=list)


# ---------- Catalog query ----------


@dataclass(frozen=True)
class CatalogMatch:
    name: str
    handler: str
    target_part_path: str
    source_file: str
    source_scope: Literal["regular", "shared"]
    format: str
    param_bindings: dict[str, dict[str, str]] = field(default_factory=dict)
    datatable_bindings: dict[str, dict[str, str | bool]] = field(default_factory=dict)
