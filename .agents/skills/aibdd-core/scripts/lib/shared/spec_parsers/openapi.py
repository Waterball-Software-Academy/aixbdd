"""OpenAPI (`*.api.yml` / `*.openapi.yml`) spec parser.

Each OpenAPI operation (e.g., POST /rooms/{roomNo}/join) maps to one
`ApiOperationPart`. The part carries operation-level identity (path, method,
operationId) plus two structured collections:

  - `request_inputs`: every path/query/header parameter AND every property of
    the requestBody schema (the first `application/json` media type today).
  - `response_properties`: every property of every 2xx response schema (first
    `application/json` media type per status code today).

`$ref` nodes are resolved via prance's RefResolver. Inline schema nodes keep
call-site `target_part_path` anchors; ref-backed parameters and top-level schema
properties use definition-site anchors (the file and JSON Pointer where the
parameter or schema property is declared).
"""

from __future__ import annotations

import copy
from pathlib import Path

from prance.util.resolver import RefResolver
from prance.util.url import ResolutionError
from ruamel.yaml import YAML

from shared.spec_parts import (
    ApiOperationPart,
    PartKind,
    RequestInput,
    ResponseProp,
)
from shared.spec_parsers.base import SpecParser

_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}
_yaml_loader = YAML(typ="safe")


class OpenAPIParseError(Exception):
    """Raised when an OpenAPI spec cannot be loaded or $ref resolution fails."""


def _escape_json_pointer(token: str) -> str:
    # RFC 6901: ~ → ~0, / → ~1 (order matters: do ~ first)
    return token.replace("~", "~0").replace("/", "~1")


def _split_ref(ref: str, base_spec_label: str) -> tuple[str, str]:
    if ref.startswith("#"):
        return base_spec_label, ref
    if "#" in ref:
        file_part, pointer = ref.split("#", 1)
        base_path = Path(base_spec_label)
        spec_label = (base_path.parent / file_part).as_posix()
        return spec_label, f"#{pointer}"
    raise OpenAPIParseError(f"Unsupported $ref format: {ref!r}")


def _definition_anchor(ref: str, base_spec_label: str) -> str:
    spec_label, pointer = _split_ref(ref, base_spec_label)
    return f"{spec_label}{pointer}"


def _load_resolved_openapi(path: Path) -> tuple[dict, dict, str]:
    spec_label = path.as_posix()
    with path.open() as fh:
        raw_doc = _yaml_loader.load(fh) or {}
    resolved_doc = copy.deepcopy(raw_doc)
    try:
        resolver = RefResolver(resolved_doc, url=str(path.resolve()))
        resolver.resolve_references()
    except ResolutionError as exc:
        raise OpenAPIParseError(
            f"Failed to resolve $ref in OpenAPI spec {spec_label}: {exc}"
        ) from exc
    except Exception as exc:
        raise OpenAPIParseError(
            f"Failed to parse OpenAPI spec {spec_label}: {exc}"
        ) from exc
    return raw_doc, resolver.specs, spec_label


class OpenAPISpecParser(SpecParser):
    def parse(self, path: Path) -> list[ApiOperationPart]:
        raw_doc, resolved_doc, spec_label = _load_resolved_openapi(path)
        parts: list[ApiOperationPart] = []
        for url_path, raw_operations in (raw_doc.get("paths") or {}).items():
            resolved_operations = (resolved_doc.get("paths") or {}).get(url_path) or {}
            path_escaped = _escape_json_pointer(url_path)
            for method, raw_op in (raw_operations or {}).items():
                if method.lower() not in _HTTP_METHODS:
                    continue
                resolved_op = (resolved_operations or {}).get(method) or {}
                op_path = f"{spec_label}#/paths/{path_escaped}/{method}"
                parts.append(
                    ApiOperationPart(
                        kind=PartKind.api_operation,
                        spec_file=path,
                        target_part_path=op_path,
                        path=url_path,
                        path_escaped=path_escaped,
                        method=method.lower(),
                        operation_id=resolved_op.get("operationId", ""),
                        request_inputs=tuple(
                            _collect_request_inputs(
                                raw_op, resolved_op, op_path, spec_label
                            )
                        ),
                        response_properties=tuple(
                            _collect_response_properties(
                                raw_op, resolved_op, op_path, spec_label
                            )
                        ),
                    )
                )
        return parts


def _collect_request_inputs(
    raw_op: dict,
    resolved_op: dict,
    op_path: str,
    spec_label: str,
):
    raw_params = raw_op.get("parameters") or []
    resolved_params = resolved_op.get("parameters") or []
    for i, raw_param in enumerate(raw_params):
        resolved_param = resolved_params[i] if i < len(resolved_params) else {}
        if "$ref" in raw_param:
            target = _definition_anchor(raw_param["$ref"], spec_label)
        else:
            target = f"{op_path}/parameters/{i}"
        yield RequestInput(
            name=resolved_param["name"],
            source=resolved_param["in"],
            required=bool(resolved_param.get("required", False)),
            target_part_path=target,
        )

    raw_rb = raw_op.get("requestBody") or {}
    resolved_rb = resolved_op.get("requestBody") or {}
    for mt, raw_mt_doc in (raw_rb.get("content") or {}).items():
        resolved_mt_doc = ((resolved_rb.get("content") or {}).get(mt)) or {}
        raw_schema = (raw_mt_doc or {}).get("schema") or {}
        resolved_schema = (resolved_mt_doc or {}).get("schema") or {}
        mt_escaped = _escape_json_pointer(mt)
        if "$ref" in raw_schema:
            schema_base = _definition_anchor(raw_schema["$ref"], spec_label)
        else:
            schema_base = (
                f"{op_path}/requestBody/content/{mt_escaped}/schema"
            )
        required_props = set(resolved_schema.get("required") or [])
        for prop_name in (resolved_schema.get("properties") or {}):
            yield RequestInput(
                name=prop_name,
                source="body",
                required=prop_name in required_props,
                target_part_path=f"{schema_base}/properties/{prop_name}",
            )


def _collect_response_properties(
    raw_op: dict,
    resolved_op: dict,
    op_path: str,
    spec_label: str,
):
    raw_responses = raw_op.get("responses") or {}
    resolved_responses = resolved_op.get("responses") or {}
    for status_code, raw_resp in raw_responses.items():
        if not str(status_code).startswith("2"):
            continue
        resolved_resp = resolved_responses.get(status_code) or {}
        for mt, raw_mt_doc in ((raw_resp or {}).get("content") or {}).items():
            resolved_mt_doc = ((resolved_resp.get("content") or {}).get(mt)) or {}
            raw_schema = (raw_mt_doc or {}).get("schema") or {}
            resolved_schema = (resolved_mt_doc or {}).get("schema") or {}
            mt_escaped = _escape_json_pointer(mt)
            if "$ref" in raw_schema:
                schema_base = _definition_anchor(raw_schema["$ref"], spec_label)
            else:
                schema_base = (
                    f"{op_path}/responses/{status_code}/content/{mt_escaped}/schema"
                )
            for prop_name in (resolved_schema.get("properties") or {}):
                yield ResponseProp(
                    name=prop_name,
                    json_path=f"$.{prop_name}",
                    target_part_path=f"{schema_base}/properties/{prop_name}",
                )
