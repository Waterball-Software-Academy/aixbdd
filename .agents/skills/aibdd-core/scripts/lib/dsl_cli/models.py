"""Dataclass + Enum contracts shared across dsl_cli modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from shared.spec_parts import (
    ApiOperationPart,
    Column,
    RefPart,
    TablePart,
    Part,
    PartKind,
    RequestInput,
    ResponseProp,
)

__all__ = [
    "AddedEntry",
    "ApiOperationPart",
    "CandidateBinding",
    "CatalogMatch",
    "Column",
    "DSLInstructionTemplate",
    "DSLEntry",
    "DatatableBinding",
    "RefPart",
    "TablePart",
    "EvalReport",
    "GenerationReport",
    "ParamBinding",
    "Part",
    "PartKind",
    "RequestInput",
    "ResponseProp",
    "Violation",
]


@dataclass
class ParamBinding:
    target: str


@dataclass
class DatatableBinding:
    target: str
    required: bool
    default_value: str | None = None


@dataclass(frozen=True)
class CandidateBinding:
    key: str
    target: str


@dataclass
class DSLInstructionTemplate:
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
    handler: str
    name: str
    target_part_path: str
    format: str
    param_bindings: dict[str, ParamBinding] = field(default_factory=dict)
    datatable_bindings: dict[str, DatatableBinding] = field(default_factory=dict)


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
