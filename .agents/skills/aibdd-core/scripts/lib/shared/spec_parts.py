"""Spec parser output types shared across dsl_cli and boundary preset plugins."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal


class PartKind(str, Enum):
    api_operation = "api_operation"
    table = "table"
    ref = "ref"


@dataclass(frozen=True)
class Part:
    """A locatable element inside a Contract / Data spec."""

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
    path_escaped: str
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
class TablePart(Part):
    table_name: str
    columns: tuple[Column, ...] = ()
    not_null_columns: tuple[Column, ...] = ()


@dataclass(frozen=True)
class RefPart(Part):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    operator: Literal[">", "-"]
    from_target_part_path: str
    to_target_part_path: str
