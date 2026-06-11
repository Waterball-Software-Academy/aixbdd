"""web-service preset's DSL-to-ISA translation plugin.

Contract (boundary preset plugin, consumed by dsl_to_isa orchestrator):
    HANDLER_TABLE: dict mapping handler name -> (translate_fn, instruction_name)
    prepare_context(contracts_dir, data_dir) -> (context, error)
    validate_step(step, context) -> str | None
    translate_step(step, context) -> (params, isa_steps)

This module is the SSOT for which handlers the web-service preset supports and
how each maps to ISA instructions. The orchestrator loads it by path and calls
the contract functions; it holds no web-service knowledge of its own.

All web-service-specific logic lives here:
  - Prerequisites: contracts/isa.yml + data/entity_to_table_mapping.yml
    (a different boundary — e.g. web-frontend — defines its own, or none)
  - DBML parsing (entity_setup / entity_validate)
  - OpenAPI navigation (api_call / response_validate)
  - Handler names and instruction formats
  - Fragment parsing (JSON Pointer, DBML fragment)
"""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path

from ruamel.yaml.scalarstring import DoubleQuotedScalarString, SingleQuotedScalarString
from shared.dsl_yaml import load_dsl_yaml
from shared.spec_parsers.openapi import OpenAPISpecParser


_FILL_IN_SENTINEL = "<FILL IN>"

_ACTOR_SLOT_KEYWORD = "UID"

_SECURITY_SCHEME_MARKER = "/components/securitySchemes/"

_NAMED_GROUP_RE = re.compile(r"\(\?P<([A-Za-z_][A-Za-z0-9_]*)>[^)]*\)")


def _instruction_format(
    isa_instructions,
    instruction_name: str,
    data_format: str | None = None,
) -> str:
    data = isa_instructions or {}
    instructions = data.get("instructions", []) if isinstance(data, dict) else data
    fallback: str | None = None
    for instruction in instructions or []:
        if not isinstance(instruction, dict):
            continue
        if (
            instruction.get("instruction_type") != instruction_name
            and instruction.get("name") != instruction_name
        ):
            continue
        fmt = str(instruction.get("format") or "")
        if data_format is not None and instruction.get("data_format") == data_format:
            return fmt
        if fallback is None:
            fallback = fmt
    if fallback is not None:
        return fallback
    raise KeyError(f"instruction {instruction_name!r} not found in isa.yml")


def _unescape_regex_literals(text: str) -> str:
    return re.sub(r"\\([(){}\[\].,+*?|^$\\])", r"\1", text)


def _clean_regex_literal(text: str) -> str:
    text = re.sub(r"\\s[*+]", " ", text)        # \s* / \s+ -> single space
    text = re.sub(r"([^\\])\?", r"\1", text)    # punctuation followed by ? -> drop the ?
    return _unescape_regex_literals(text)


def _render_instruction(
    isa_instructions,
    instruction_name: str,
    slots: dict[str, object],
    data_format: str | None = None,
) -> str:
    fmt = _instruction_format(isa_instructions, instruction_name, data_format)
    if fmt.startswith("^"):
        fmt = fmt[1:]
    if fmt.endswith("$") and not fmt.endswith("\\$"):
        fmt = fmt[:-1]
    chunks: list[str] = []
    last = 0
    for match in _NAMED_GROUP_RE.finditer(fmt):
        literal_before = fmt[last:match.start()]
        slot_name = match.group(1)
        value = str(slots.get(slot_name, ""))

        # Detect actor-alternation block: literal before this named group contains
        # a No-Actor alternation (e.g. \((?:No Actor|UID=""|UID="), and actor slot
        # holds the correct branch value. Render entire block as (actor) and skip.
        if not value and "actor" in slots and "No Actor" in literal_before:
            close_m = re.match(r'^"\)\\\)', fmt[match.end():])
            if close_m:
                chunks.append(f"({slots['actor']})")
                last = match.end() + close_m.end()
                continue

        chunks.append(_clean_regex_literal(literal_before))
        if slot_name == "actor" and match.start() == 0:
            value = f"({value})"
        chunks.append(value)
        last = match.end()
    chunks.append(_clean_regex_literal(fmt[last:]))
    return "".join(chunks)

# ---------------------------------------------------------------------------
# Fragment / path parsing helpers
# ---------------------------------------------------------------------------

def _extract_table_name_from_target(target_part_path: str) -> str | None:
    """Extract table name from a DBML target_part_path fragment.

    Examples:
      "data/domain.dbml#rooms"       -> "rooms"
      "data/domain.dbml#rooms.col"   -> "rooms"
      "contracts/foo.yml#/paths/..."  -> None  (OpenAPI path, starts with /)
      ""                              -> None
    """
    if "#" not in target_part_path:
        return None
    fragment = target_part_path.split("#", 1)[1]
    if not fragment or fragment.startswith("/") or fragment.startswith("ref:"):
        return None
    return fragment.split(".")[0]


def _extract_column_name_from_target(target_part_path: str) -> str | None:
    if "#" not in target_part_path:
        return None
    fragment = target_part_path.split("#", 1)[1]
    if "." not in fragment:
        return None
    return fragment.split(".", 1)[1]


def _json_pointer_to_keys(fragment: str) -> list[str]:

    if fragment.startswith("#"):
        fragment = fragment[1:]
    if not fragment.startswith("/"):
        return [fragment] if fragment else []
    parts = fragment[1:].split("/")
    return [p.replace("~1", "/").replace("~0", "~") for p in parts]


# ---------------------------------------------------------------------------
# OpenAPI navigation helpers
# ---------------------------------------------------------------------------

@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


class _OpenAPILookup:
    def __init__(self, parts):
        self.operations = {part.target_part_path: part for part in parts}
        self.request_inputs = {}
        for part in parts:
            for request_input in part.request_inputs:
                self.request_inputs[request_input.target_part_path] = request_input


_OPENAPI_LOOKUP_CACHE: dict[tuple[str, str], _OpenAPILookup] = {}

def _resolve_spec_file(contracts_dir: str, file_part: str) -> Path:

    contracts_path = Path(contracts_dir)
    boundary_root = contracts_path.parent
    codebase_root = boundary_root.parent

    candidates: list[Path] = []
    if file_part.startswith(f"{boundary_root.name}/"):
        candidates.append(codebase_root / file_part)
    candidates.append(boundary_root / file_part)
    if not file_part.startswith(f"{boundary_root.name}/"):
        candidates.append(codebase_root / boundary_root.name / file_part)

    for path in candidates:
        if path.is_file():
            return path

    raise FileNotFoundError(
        f"spec file not found for {file_part!r} (tried: "
        + ", ".join(str(p) for p in candidates)
        + ")"
    )


def _split_openapi_target(target_part_path: str) -> tuple[str, str]:
    """Split an OpenAPI target into file part and ``#`` fragment."""
    if "#" not in target_part_path:
        raise ValueError(f"target_part_path has no fragment: {target_part_path!r}")
    file_part, fragment = target_part_path.split("#", 1)
    return file_part, "#" + fragment


def _parser_root_and_path(contracts_dir: str, file_part: str) -> tuple[Path, Path]:
    """Return cwd + relative parser path that preserves DSL anchor prefixes."""
    contracts_path = Path(contracts_dir)
    boundary_root = contracts_path.parent
    codebase_root = boundary_root.parent

    if Path(file_part).is_absolute():
        return Path("/"), Path(file_part).resolve().relative_to("/")
    if file_part.startswith(f"{boundary_root.name}/"):
        return codebase_root, Path(file_part)
    return boundary_root, Path(file_part)


def _load_openapi_lookup(
    contracts_dir: str,
    target_part_path: str,
) -> tuple[_OpenAPILookup, str, str]:
    file_part, fragment = _split_openapi_target(target_part_path)
    spec_path = _resolve_spec_file(contracts_dir, file_part)
    cache_key = (str(spec_path.resolve()), file_part)
    if cache_key not in _OPENAPI_LOOKUP_CACHE:
        parser_root, parser_path = _parser_root_and_path(contracts_dir, file_part)
        with _chdir(parser_root):
            parts = OpenAPISpecParser().parse(parser_path)
        _OPENAPI_LOOKUP_CACHE[cache_key] = _OpenAPILookup(parts)
    return _OPENAPI_LOOKUP_CACHE[cache_key], file_part, fragment


def _operation_target(file_part: str, fragment: str) -> str:
    return f"{file_part}{fragment}"


def _get_body_field_name(body_target: str) -> str | None:
    """Extract the field name from a requestBody target_part_path.

    e.g. .../schema/properties/player_id -> "player_id"
    """
    if "#" not in body_target:
        return None
    _, fragment = body_target.split("#", 1)
    keys = _json_pointer_to_keys("#" + fragment)
    if keys:
        return keys[-1]
    return None


def _extract_status_code_from_fragment(fragment: str) -> str | None:
    """Extract HTTP status code from a responses fragment.

    Handles:
      #/paths/.../post/responses/200           -> "200"
      #/paths/.../post/responses/200/content/... -> "200"
    """
    m = re.search(r"/responses/(\d{3})", fragment)
    if m:
        return m.group(1)
    return None


def _get_parent_operation_fragment(fragment: str) -> str:
    """Get the operation fragment from a response fragment.

    e.g. #/paths/~1rooms/post/responses/200/content/... -> #/paths/~1rooms/post
    """
    # Find the operation portion (everything up to /responses/...)
    keys = _json_pointer_to_keys(fragment)
    # Walk back to find the method key (get/post/put/patch/delete)
    http_methods = {"get", "post", "put", "patch", "delete", "options", "head"}
    for i, key in enumerate(keys):
        if key.lower() in http_methods:
            # Reconstruct fragment up to and including the method key
            op_keys = keys[:i + 1]
            parts = ["/" + k.replace("~", "~0").replace("/", "~1") for k in op_keys]
            return "#" + "".join(parts)
    return fragment


# ---------------------------------------------------------------------------
# prepare_context — web-service prerequisites (isa.yml + entity_to_table_mapping)
# ---------------------------------------------------------------------------

# Handlers that require entity_to_table_mapping.yml to be present
ENTITY_HANDLERS: frozenset[str] = frozenset({"state-builder", "state-verifier"})


def _load_entity_map(path: Path) -> dict[str, str]:
    """Load entity→table map from flat or nested YAML layouts."""
    raw = load_dsl_yaml(path)
    if not raw or not isinstance(raw, dict):
        return {}

    if "entity_to_table_mapping" in raw:
        entries = raw.get("entity_to_table_mapping") or []
        out: dict[str, str] = {}
        for item in entries:
            if isinstance(item, dict):
                out.update({str(k): str(v) for k, v in item.items()})
        return out

    return {str(k): str(v) for k, v in raw.items()}


def prepare_context(contracts_dir: str, data_dir: str) -> tuple[dict | None, str | None]:
    """Check + load web-service prerequisites; return (context, error).

    contracts/isa.yml is required (it is the ISA instruction set the translator
    renders against). data/entity_to_table_mapping.yml is loaded when present;
    its absence only becomes an error if a state-* handler is actually used, so
    that absence is reported per-step in validate_step.
    """
    contracts_path = Path(contracts_dir)
    data_path = Path(data_dir)

    isa_yml = contracts_path / "isa.yml"
    if not isa_yml.exists():
        return None, (
            f"contracts/isa.yml not found at {isa_yml}. "
            "Run /aibdd-plan 02-contracts-design to generate it."
        )

    entity_map_yml = data_path / "entity_to_table_mapping.yml"
    entity_map: dict[str, str] = {}
    if entity_map_yml.exists():
        entity_map = _load_entity_map(entity_map_yml)

    context = {
        "isa_instructions": load_dsl_yaml(isa_yml),
        "entity_map": entity_map,
        "entity_map_path": str(entity_map_yml),
        "contracts_dir": contracts_dir,
    }
    return context, None


# ---------------------------------------------------------------------------
# validate_step — web-service-specific validation
# ---------------------------------------------------------------------------

def validate_step(step: dict, context: dict) -> str | None:
    handler = step.get("handler", "")
    entity_map = context["entity_map"]

    if handler in ENTITY_HANDLERS:
        if not entity_map:
            return (
                f"data/entity_to_table_mapping.yml not found at "
                f"{context['entity_map_path']}. Run 01-table-to-entity first."
            )
        target = step.get("target_part_path", "")
        table_name = _extract_table_name_from_target(target)
        if table_name and table_name not in entity_map:
            return (
                f"entity `{table_name}` not in data/entity_to_table_mapping.yml"
            )

    return None


# ---------------------------------------------------------------------------
# Per-handler translators
# ---------------------------------------------------------------------------

def _translate_ref_verifier(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    isa_instructions = context["isa_instructions"]
    entity_map = context["entity_map"]
    param_bindings: dict = step.get("param_bindings") or {}
    isa_steps = []
    for dsl_key, binding in param_bindings.items():
        target = binding.get("target", "") if isinstance(binding, dict) else str(binding)
        table_name = _extract_table_name_from_target(target)
        col_name = _extract_column_name_from_target(target)
        key = col_name or dsl_key
        entity_name = entity_map.get(table_name, table_name) if table_name else ""
        instruction = _render_instruction(
            isa_instructions,
            instruction_name,
            {"entity": entity_name},
            data_format="data_table",
        )
        table = {key: DoubleQuotedScalarString("{{" + dsl_key + "}}")}
        isa_steps.append({"instruction": instruction, "table": table})
    params = list(param_bindings.keys())
    return params, isa_steps


def _translate_entity(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    isa_instructions = context["isa_instructions"]
    entity_map = context["entity_map"]
    target = step.get("target_part_path", "")
    param_bindings: dict = step.get("param_bindings") or {}
    datatable_bindings: dict = step.get("datatable_bindings") or {}

    table_name = _extract_table_name_from_target(target)
    entity_name = entity_map.get(table_name, table_name) if table_name else ""

    instruction = _render_instruction(
        isa_instructions,
        instruction_name,
        {"entity": entity_name},
        data_format="data_table",
    )

    table = {}
    for bindings in (param_bindings, datatable_bindings):
        for dsl_key, binding in bindings.items():
            if isinstance(binding, dict):
                col_name = _extract_column_name_from_target(binding.get("target", ""))
            else:
                col_name = _extract_column_name_from_target(str(binding)) or str(binding)
            if col_name:
                table[DoubleQuotedScalarString(col_name)] = DoubleQuotedScalarString(
                    "{{" + dsl_key + "}}"
                )

    params = _build_params(datatable_bindings)
    return params, [{"instruction": instruction, "table": table}]


def _translate_api_call(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    """Translate operation-invoke -> api_call."""
    isa_instructions = context["isa_instructions"]
    contracts_dir = context["contracts_dir"]
    target = step.get("target_part_path", "")
    param_bindings: dict = step.get("param_bindings") or {}
    datatable_bindings: dict = dict(step.get("datatable_bindings") or {})

    lookup, file_part, fragment = _load_openapi_lookup(contracts_dir, target)
    operation = lookup.operations.get(_operation_target(file_part, fragment))
    summary = operation.summary if operation else ""

    actor_key = _find_actor_binding(datatable_bindings)
    actor_binding = datatable_bindings.pop(actor_key, None) if actor_key else None
    actor = _resolve_actor(actor_key, operation)

    instruction = _render_instruction(
        isa_instructions,
        instruction_name,
        {"actor": actor, "summary": summary},
        data_format="data_table",
    )

    table = {}

    for dsl_key, binding in param_bindings.items():
        if isinstance(binding, dict):
            param_target = binding.get("target", "")
        else:
            param_target = str(binding)

        request_input = lookup.request_inputs.get(param_target)
        if request_input and request_input.source != "body":
            param_location = request_input.source
            param_name = request_input.name
            prefix_map = {"path": "P:", "header": "H:", "query": "Q:"}
            prefix = prefix_map.get(param_location, "")
            key = f"{prefix}{param_name}"
            table[DoubleQuotedScalarString(key)] = DoubleQuotedScalarString(
                "{{" + dsl_key + "}}"
            )
        else:
            field_name = request_input.name if request_input else _get_body_field_name(param_target)
            if field_name:
                table[DoubleQuotedScalarString(field_name)] = DoubleQuotedScalarString(
                    "{{" + dsl_key + "}}"
                )

    # Process datatable_bindings (request body fields)
    for dsl_key, binding in datatable_bindings.items():
        if isinstance(binding, dict):
            body_target = binding.get("target", "")
        else:
            body_target = str(binding)
        request_input = lookup.request_inputs.get(body_target)
        field_name = request_input.name if request_input else _get_body_field_name(body_target)
        if field_name:
            table[field_name] = DoubleQuotedScalarString("{{" + dsl_key + "}}")

    params = _build_params(datatable_bindings)
    params = _inject_actor_param(params, actor_key, actor_binding)

    return params, [{"instruction": instruction, "table": table}]


def _find_actor_binding(datatable_bindings: dict) -> str | None:
    for dsl_key, binding in datatable_bindings.items():
        target = binding.get("target", "") if isinstance(binding, dict) else str(binding)
        if _SECURITY_SCHEME_MARKER in target:
            return dsl_key
    return None


def _resolve_actor(actor_key: str | None, operation) -> str:
    if actor_key is not None:
        return _ACTOR_SLOT_KEYWORD + '="{{' + actor_key + '}}"'
    if operation and operation.security_schemes:
        return _FILL_IN_SENTINEL
    return "No Actor"


def _translate_response_validate_status_only(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    """Translate operation-response-success-and-failure -> response_validate (status-only)."""
    isa_instructions = context["isa_instructions"]
    contracts_dir = context["contracts_dir"]
    target = step.get("target_part_path", "")

    lookup, file_part, fragment = _load_openapi_lookup(contracts_dir, target)

    # Extract status code from fragment: .../responses/200
    status_code = _extract_status_code_from_fragment(fragment)

    # Get parent operation summary
    op_fragment = _get_parent_operation_fragment(fragment)
    operation = lookup.operations.get(_operation_target(file_part, op_fragment))
    summary = operation.summary if operation else ""

    instruction = _render_instruction(
        isa_instructions,
        instruction_name,
        {"summary": summary, "status_code": status_code},
        data_format="data_table",
    )

    return [], [{"instruction": instruction, "table": {}}]


def _translate_response_readmodel(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    """Translate operation-response-success-readmodel -> response_validate (body fields)."""
    isa_instructions = context["isa_instructions"]
    contracts_dir = context["contracts_dir"]
    target = step.get("target_part_path", "")
    param_bindings: dict = step.get("param_bindings") or {}
    datatable_bindings: dict = step.get("datatable_bindings") or {}

    lookup, file_part, fragment = _load_openapi_lookup(contracts_dir, target)

    # Extract status code from fragment path like .../responses/200/content/...
    status_code = _extract_status_code_from_fragment(fragment)

    # Get parent operation summary
    op_fragment = _get_parent_operation_fragment(fragment)
    operation = lookup.operations.get(_operation_target(file_part, op_fragment))
    summary = operation.summary if operation else ""

    instruction = _render_instruction(
        isa_instructions,
        instruction_name,
        {"summary": summary, "status_code": status_code},
        data_format="data_table",
    )

    # Build table with response: URI scheme from both binding kinds.
    # readmodel asserts the read model, so every observed field must become a
    # table row: param_bindings (inline format fields) first, then
    # datatable_bindings (appended data-table fields).
    # target: "response:$.fieldName" -> fieldName
    table = {}
    for bindings in (param_bindings, datatable_bindings):
        for dsl_key, binding in bindings.items():
            if isinstance(binding, dict):
                resp_target = binding.get("target", "")
            else:
                resp_target = str(binding)
            # response:$.fieldName -> fieldName
            field_name = _parse_response_field(resp_target)
            if field_name:
                table[field_name] = DoubleQuotedScalarString("{{" + dsl_key + "}}")

    # param_bindings (inline read-model fields) fold into the assertion table
    # only; params still derives from datatable_bindings alone.
    params = _build_params(datatable_bindings)

    return params, [{"instruction": instruction, "table": table}]


def _parse_response_field(resp_target: str) -> str | None:
    """Extract field name from a response:$.fieldName target.

    "response:$.roomNo"     -> "roomNo"
    "response:$.foo.bar"    -> "bar" (last segment)
    """
    if not resp_target.startswith("response:"):
        return None
    json_path = resp_target[len("response:"):]
    # Strip leading $. if present
    if json_path.startswith("$."):
        json_path = json_path[2:]
    # Take the last dot-separated segment
    return json_path.split(".")[-1] if json_path else None


def _translate_time_control(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    """Translate time-control -> time_control."""
    isa_instructions = context["isa_instructions"]
    param_bindings: dict = step.get("param_bindings") or {}

    # Get the single param key (the DSL time variable name)
    if param_bindings:
        time_key = next(iter(param_bindings.keys()))
    else:
        time_key = "時間"

    instruction = _render_instruction(
        isa_instructions,
        instruction_name,
        {"time": "{{" + time_key + "}}"},
    )

    return [], [{"instruction": instruction, "table": {}}]


def _translate_passthrough(step: dict, context: dict, instruction_name: str) -> tuple[list, list]:
    """external-stub / unrecognised: emit nothing."""
    return [], []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# SQL current-time defaults across dialects: now()/getdate() (parens),
# current_timestamp (bare or with parens). Case-insensitive.
_SQL_NOW_DEFAULT_RE = re.compile(
    r"^\s*(?:now\(\s*\)|getdate\(\s*\)|current_timestamp(?:\s*\(\s*\))?)\s*$",
    re.IGNORECASE,
)
_DSL_TIME_NOW_MACRO = '@time("now")'


def _normalize_default_value(value):
    if isinstance(value, str) and _SQL_NOW_DEFAULT_RE.match(value):
        return _DSL_TIME_NOW_MACRO
    return value


def _build_params(datatable_bindings: dict):
    entries = []
    has_default = False
    for dsl_key, binding in datatable_bindings.items():
        if isinstance(binding, dict) and "default_value" in binding:
            entries.append((dsl_key, _normalize_default_value(binding["default_value"])))
            has_default = True
        else:
            entries.append((dsl_key, None))

    if has_default:
        return {dsl_key: default for dsl_key, default in entries}
    return [dsl_key for dsl_key, _ in entries]


def _inject_actor_param(params, actor_key: str | None, actor_binding):
    if actor_key is None:
        return params
    if isinstance(actor_binding, dict):
        default = actor_binding.get("default_value", "")
    else:
        default = str(actor_binding)
    merged = dict(params) if isinstance(params, dict) else {key: None for key in params}
    merged[actor_key] = default
    return merged


HANDLER_TABLE: dict[str, tuple] = {
    "state-builder": (_translate_entity, "entity_setup"),
    "state-verifier": (_translate_entity, "entity_validate"),
    "state-relationship-verifier": (_translate_ref_verifier, "entity_validate"),
    "operation-invoke": (_translate_api_call, "api_call"),
    "operation-response-success-and-failure": (_translate_response_validate_status_only, "response_validate"),
    "operation-response-success-readmodel": (_translate_response_readmodel, "response_validate"),
    "time-control": (_translate_time_control, "time_control"),
    "external-stub": (_translate_passthrough, "custom"),
}


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def translate_step(step: dict, context: dict) -> tuple[list, list]:
    """Translate a DSL step to ISA params + isa_steps.

    Returns (params, isa_steps) where params is a list and isa_steps is a list of dicts.
    """
    handler = step.get("handler", "")
    entry = HANDLER_TABLE.get(handler)
    if entry is None:
        return [], []
    translate_fn, instruction_name = entry
    return translate_fn(step, context, instruction_name)
