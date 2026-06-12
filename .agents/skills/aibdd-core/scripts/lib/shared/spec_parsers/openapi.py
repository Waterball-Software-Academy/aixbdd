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


def _split_ref_full(ref: str, base_spec_label: str) -> tuple[str, str]:
    if ref.startswith("#"):
        return base_spec_label, ref[1:]
    base_dir = Path(base_spec_label).parent
    if "#" in ref:
        file_part, pointer = ref.split("#", 1)
        return (base_dir / file_part).as_posix(), pointer
    return (base_dir / ref).as_posix(), ""


def _navigate_pointer(doc: dict, pointer_body: str):
    node = doc
    for token in pointer_body.split("/"):
        if token == "":
            continue
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or token not in node:
            raise OpenAPIParseError(f"$ref pointer {pointer_body!r} not found")
        node = node[token]
    return node


def _resolve_raw_node(
    node, base_spec_label: str, raw_cache: dict
) -> tuple[object, str, str]:
    seen: set[str] = set()
    home_label = base_spec_label
    home_pointer = ""
    followed = False
    while isinstance(node, dict) and "$ref" in node:
        followed = True
        new_label, pointer_body = _split_ref_full(node["$ref"], home_label)
        key = f"{new_label}#{pointer_body}"
        if key in seen:
            raise OpenAPIParseError(f"circular $ref: {node['$ref']!r}")
        seen.add(key)
        doc = _load_raw(new_label, raw_cache)
        node = _navigate_pointer(doc, pointer_body) if pointer_body else doc
        home_label, home_pointer = new_label, pointer_body
    if not followed:
        return node, base_spec_label, ""
    return node, home_label, home_pointer


def _load_raw(spec_label: str, raw_cache: dict) -> dict:
    if spec_label not in raw_cache:
        with Path(spec_label).open() as fh:
            raw_cache[spec_label] = _yaml_loader.load(fh) or {}
    return raw_cache[spec_label]


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
        raw_cache: dict[str, dict] = {spec_label: raw_doc}
        parts: list[ApiOperationPart] = []
        for url_path, raw_path_item_node in (raw_doc.get("paths") or {}).items():
            resolved_operations = (resolved_doc.get("paths") or {}).get(url_path) or {}
            path_escaped = _escape_json_pointer(url_path)

            pi_is_ref = isinstance(raw_path_item_node, dict) and "$ref" in raw_path_item_node
            raw_path_item, ref_pi_label, ref_pi_pointer = _resolve_raw_node(
                raw_path_item_node, spec_label, raw_cache
            )
            if pi_is_ref:
                pi_label, pi_pointer = ref_pi_label, ref_pi_pointer
            else:
                pi_label, pi_pointer = spec_label, f"/paths/{path_escaped}"
            path_item_path = f"{pi_label}#{pi_pointer}"

            raw_path_params = (raw_path_item or {}).get("parameters") or []
            resolved_path_params = (resolved_operations or {}).get("parameters") or []

            for method, raw_op_node in (raw_path_item or {}).items():
                if method.lower() not in _HTTP_METHODS:
                    continue
                resolved_op = (resolved_operations or {}).get(method) or {}

                op_is_ref = isinstance(raw_op_node, dict) and "$ref" in raw_op_node
                raw_op, ref_op_label, ref_op_pointer = _resolve_raw_node(
                    raw_op_node, pi_label, raw_cache
                )
                if op_is_ref:
                    op_label, op_pointer = ref_op_label, ref_op_pointer
                else:
                    op_label, op_pointer = pi_label, f"{pi_pointer}/{method}"
                op_path = f"{op_label}#{op_pointer}"

                parts.append(
                    ApiOperationPart(
                        kind=PartKind.api_operation,
                        spec_file=path,
                        target_part_path=op_path,
                        path=url_path,
                        path_escaped=path_escaped,
                        method=method.lower(),
                        operation_id=resolved_op.get("operationId")
                        or raw_op.get("operationId", ""),
                        summary=resolved_op.get("summary")
                        or raw_op.get("summary", ""),
                        request_inputs=tuple(
                            _collect_request_inputs(
                                raw_op,
                                resolved_op,
                                op_path,
                                op_label,
                                raw_path_params,
                                resolved_path_params,
                                path_item_path,
                            )
                        ),
                        response_properties=tuple(
                            _collect_response_properties(
                                raw_op, resolved_op, op_path, op_label
                            )
                        ),
                        auth_required=_collect_auth_required(raw_op, raw_doc),
                    )
                )
        return parts


def _collect_auth_required(raw_op: dict, raw_doc: dict) -> bool:
    if "security" in raw_op:
        requirements = raw_op.get("security") or []
    else:
        requirements = raw_doc.get("security") or []
    return any(isinstance(requirement, dict) and requirement for requirement in requirements)


def _iter_schema_props(
    raw_schema: dict | None,
    resolved_schema: dict,
    base: str,
    spec_label: str,
):
    resolved_schema = resolved_schema or {}

    if isinstance(raw_schema, dict) and "$ref" in raw_schema:
        base = _definition_anchor(raw_schema["$ref"], spec_label)
        raw_schema = None

    resolved_branches = resolved_schema.get("allOf")
    if resolved_branches:
        raw_branches = (
            raw_schema.get("allOf") if isinstance(raw_schema, dict) else None
        )
        for i, resolved_branch in enumerate(resolved_branches):
            raw_branch = (
                raw_branches[i]
                if raw_branches and i < len(raw_branches)
                else None
            )
            yield from _iter_schema_props(
                raw_branch, resolved_branch, f"{base}/allOf/{i}", spec_label
            )
        return

    required_props = set(resolved_schema.get("required") or [])
    for prop_name in (resolved_schema.get("properties") or {}):
        yield (
            prop_name,
            prop_name in required_props,
            f"{base}/properties/{prop_name}",
        )


def _collect_request_inputs(
    raw_op: dict,
    resolved_op: dict,
    op_path: str,
    spec_label: str,
    raw_path_params: list,
    resolved_path_params: list,
    path_item_path: str,
):
    op_param_keys: set[tuple[str, str]] = set()
    op_params: list[tuple[dict, str]] = []
    raw_params = raw_op.get("parameters") or []
    resolved_params = resolved_op.get("parameters") or []
    for i, raw_param in enumerate(raw_params):
        resolved_param = resolved_params[i] if i < len(resolved_params) else {}
        if "$ref" in raw_param:
            target = _definition_anchor(raw_param["$ref"], spec_label)
        else:
            target = f"{op_path}/parameters/{i}"
        op_param_keys.add((resolved_param["name"], resolved_param["in"]))
        op_params.append((resolved_param, target))

    for i, raw_param in enumerate(raw_path_params):
        resolved_param = (
            resolved_path_params[i] if i < len(resolved_path_params) else {}
        )
        if (resolved_param["name"], resolved_param["in"]) in op_param_keys:
            continue
        if "$ref" in raw_param:
            target = _definition_anchor(raw_param["$ref"], spec_label)
        else:
            target = f"{path_item_path}/parameters/{i}"
        yield RequestInput(
            name=resolved_param["name"],
            source=resolved_param["in"],
            required=bool(resolved_param.get("required", False)),
            target_part_path=target,
        )

    for resolved_param, target in op_params:
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
        base = f"{op_path}/requestBody/content/{mt_escaped}/schema"
        for prop_name, required, anchor in _iter_schema_props(
            raw_schema, resolved_schema, base, spec_label
        ):
            yield RequestInput(
                name=prop_name,
                source="body",
                required=required,
                target_part_path=anchor,
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
            base = f"{op_path}/responses/{status_code}/content/{mt_escaped}/schema"
            for prop_name, _required, anchor in _iter_schema_props(
                raw_schema, resolved_schema, base, spec_label
            ):
                yield ResponseProp(
                    name=prop_name,
                    json_path=f"$.{prop_name}",
                    target_part_path=anchor,
                )
