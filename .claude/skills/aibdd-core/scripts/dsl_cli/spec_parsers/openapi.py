"""OpenAPI (`*.api.yml` / `*.openapi.yml`) spec parser.

Each OpenAPI operation (e.g., POST /rooms/{roomNo}/join) maps to one
`ApiOperationPart`. The part carries operation-level identity (path, method,
operationId) plus two structured collections:

  - `request_inputs`: every path/query/header parameter AND every property of
    the requestBody schema (the first `application/json` media type today).
  - `response_properties`: every property of every 2xx response schema (first
    `application/json` media type per status code today).

target_part_path uses RFC 6901 JSON Pointer with `/` escaped as `~1` so the
pointer can sit safely inside a path fragment.
"""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

from dsl_cli.models import (
    ApiOperationPart,
    PartKind,
    RequestInput,
    ResponseProp,
)
from dsl_cli.spec_parsers.base import SpecParser

_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}
_yaml_loader = YAML(typ="safe")


def _escape_json_pointer(token: str) -> str:
    # RFC 6901: ~ → ~0, / → ~1 (order matters: do ~ first)
    return token.replace("~", "~0").replace("/", "~1")


class OpenAPISpecParser(SpecParser):
    def parse(self, path: Path) -> list[ApiOperationPart]:
        with path.open() as fh:
            doc = _yaml_loader.load(fh) or {}
        spec_label = path.as_posix()
        parts: list[ApiOperationPart] = []
        for url_path, operations in (doc.get("paths") or {}).items():
            path_escaped = _escape_json_pointer(url_path)
            for method, op in (operations or {}).items():
                if method.lower() not in _HTTP_METHODS:
                    continue
                op_path = f"{spec_label}#/paths/{path_escaped}/{method}"
                parts.append(
                    ApiOperationPart(
                        kind=PartKind.api_operation,
                        spec_file=path,
                        target_part_path=op_path,
                        path=url_path,
                        path_escaped=path_escaped,
                        method=method.lower(),
                        operation_id=op.get("operationId", ""),
                        request_inputs=tuple(_collect_request_inputs(op, op_path)),
                        response_properties=tuple(_collect_response_properties(op, op_path)),
                    )
                )
        return parts


def _collect_request_inputs(op: dict, op_path: str):
    for i, param in enumerate(op.get("parameters") or []):
        yield RequestInput(
            name=param["name"],
            source=param["in"],
            required=bool(param.get("required", False)),
            target_part_path=f"{op_path}/parameters/{i}",
        )
    rb = op.get("requestBody") or {}
    for mt, mt_doc in (rb.get("content") or {}).items():
        mt_escaped = _escape_json_pointer(mt)
        schema = (mt_doc or {}).get("schema") or {}
        required_props = set(schema.get("required") or [])
        for prop_name in (schema.get("properties") or {}):
            yield RequestInput(
                name=prop_name,
                source="body",
                required=prop_name in required_props,
                target_part_path=(
                    f"{op_path}/requestBody/content/{mt_escaped}/schema/properties/{prop_name}"
                ),
            )


def _collect_response_properties(op: dict, op_path: str):
    for status_code, resp in (op.get("responses") or {}).items():
        if not str(status_code).startswith("2"):
            continue
        for mt, mt_doc in ((resp or {}).get("content") or {}).items():
            mt_escaped = _escape_json_pointer(mt)
            schema = (mt_doc or {}).get("schema") or {}
            schema_path = (
                f"{op_path}/responses/{status_code}/content/{mt_escaped}/schema"
            )
            for prop_name in (schema.get("properties") or {}):
                yield ResponseProp(
                    name=prop_name,
                    json_path=f"$.{prop_name}",
                    target_part_path=f"{schema_path}/properties/{prop_name}",
                )
