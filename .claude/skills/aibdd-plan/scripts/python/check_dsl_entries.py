#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from _common import (
    collect_yaml_files,
    emit,
    load_profile,
    load_yaml,
    placeholders,
    read_args,
    resolve_arg_path,
    violation,
)


def _resolve_allowed_target_prefixes(
    args_path: Path,
    args: dict[str, str],
    violations: list[dict[str, Any]],
) -> tuple[str, ...] | None:
    """Read allowed_l4_target_prefixes from the boundary profile.

    Profile chain: BOUNDARY_YML#boundaries[0].type → <type>.profile.yml.
    Returns None and appends a violation when the profile or field is
    unresolvable; this is a hard config error, not a fallback case.
    """
    profile = load_profile(args_path, args)
    if not isinstance(profile, dict):
        violations.append(
            violation(
                "DSL_PROFILE_MISSING",
                str(args_path),
                "boundary profile not resolvable from BOUNDARY_YML#boundaries[0].type "
                "(check kickoff and aibdd-core/references/boundary-type-profiles/)",
            )
        )
        return None
    prefixes = profile.get("allowed_l4_target_prefixes")
    if not isinstance(prefixes, list) or not prefixes:
        violations.append(
            violation(
                "DSL_PROFILE_FIELD_MISSING",
                str(args_path),
                "boundary profile missing required field 'allowed_l4_target_prefixes' "
                "(see aibdd-core/references/boundary-profile-contract.md)",
            )
        )
        return None
    return tuple(str(p) for p in prefixes)

_TRANSPORT_HEADERS_EXCLUDED_FROM_EXACT_MATCH = frozenset(
    {
        "authorization",
        "x-actor-role",
        "x-request-id",
        "x-correlation-id",
        "accept",
        "content-type",
    }
)


def entries_from(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        entries = data.get("entries") or data.get("Entries")
        if isinstance(entries, list):
            return [x for x in entries if isinstance(x, dict)]
    return []


def binding_target(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("target", ""))
    return ""


def _schema_fields(schema: Any, doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize OpenAPI object schema properties into contract `fields` shape."""
    if not isinstance(schema, dict):
        return []
    if isinstance(schema.get("$ref"), str):
        ref = schema["$ref"]
        if ref.startswith("#/"):
            cur: Any = doc
            for part in ref[2:].split("/"):
                if isinstance(cur, dict):
                    cur = cur.get(part)
                else:
                    cur = None
                    break
            schema = cur if isinstance(cur, dict) else {}
    props = schema.get("properties") if isinstance(schema, dict) else {}
    required = set(schema.get("required") or []) if isinstance(schema, dict) else set()
    out: list[dict[str, Any]] = []
    if isinstance(props, dict):
        for name, prop in props.items():
            item: dict[str, Any] = {"name": str(name), "required": str(name) in required}
            if isinstance(prop, dict) and prop.get("type"):
                item["type"] = prop.get("type")
            out.append(item)
    return out


def _normalize_openapi_operations(rel_posix: str, data: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    """Index OpenAPI path operations by operationId using the DSL contract anchor shape."""
    out: dict[tuple[str, str], dict[str, Any]] = {}
    paths = data.get("paths")
    if not isinstance(paths, dict):
        return out
    for _path, path_doc in paths.items():
        if not isinstance(path_doc, dict):
            continue
        path_level_params = path_doc.get("parameters") if isinstance(path_doc.get("parameters"), list) else []
        for method, op in path_doc.items():
            if str(method).lower() not in {"get", "post", "put", "patch", "delete", "head", "options"}:
                continue
            if not isinstance(op, dict) or not op.get("operationId"):
                continue
            oid = str(op["operationId"])
            rq = {"params": [], "headers": [], "body": {"fields": []}}
            for p in [*path_level_params, *(op.get("parameters") or [])]:
                if not isinstance(p, dict):
                    continue
                bucket = "headers" if p.get("in") == "header" else "params" if p.get("in") in {"query", "path"} else None
                if bucket:
                    rq[bucket].append({"name": p.get("name"), "required": bool(p.get("required"))})
            body = op.get("requestBody")
            if isinstance(body, dict):
                content = body.get("content") or {}
                media = content.get("application/json") if isinstance(content, dict) else None
                schema = media.get("schema") if isinstance(media, dict) else None
                rq["body"]["fields"] = _schema_fields(schema, data)
            resp_fields: list[dict[str, Any]] = []
            responses = op.get("responses") or {}
            if isinstance(responses, dict):
                for code in ("200", "201", "202", "204", "default"):
                    resp = responses.get(code)
                    if not isinstance(resp, dict):
                        continue
                    content = resp.get("content") or {}
                    media = content.get("application/json") if isinstance(content, dict) else None
                    schema = media.get("schema") if isinstance(media, dict) else None
                    resp_fields = _schema_fields(schema, data)
                    break
            out[(rel_posix, oid)] = {"operation_id": oid, "request": rq, "response": {"fields": resp_fields}}
    return out


def load_operations_index(contracts_dir: Path | None) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    if contracts_dir is None or not contracts_dir.is_dir():
        return out
    for yml in collect_yaml_files(contracts_dir):
        rel_posix = "contracts/" + yml.relative_to(contracts_dir).as_posix()
        data = load_yaml(yml) or {}
        if isinstance(data.get("openapi"), str) or isinstance(data.get("paths"), dict):
            out.update(_normalize_openapi_operations(rel_posix, data))
            continue

        ops = data.get("operations")
        if not isinstance(ops, list):
            continue
        for item in ops:
            if isinstance(item, dict) and item.get("operation_id"):
                oid = str(item["operation_id"])
                out[(rel_posix, oid)] = item
    return out


def required_input_binding_targets(rel_contract_file: str, op_doc: dict[str, Any]) -> set[str]:
    """Full refs like contracts/a.yml#get-op.request.params.id (headers omitted per transport skip list)."""
    oid = str(op_doc.get("operation_id", ""))
    targets: set[str] = set()
    rq = op_doc.get("request")
    if not isinstance(rq, dict):
        return targets

    for p in rq.get("params") or []:
        if isinstance(p, dict) and p.get("required"):
            targets.add(f"{rel_contract_file}#{oid}.request.params.{p['name']}")

    for h in rq.get("headers") or []:
        if isinstance(h, dict) and h.get("required"):
            ln = str(h.get("name", "")).strip().lower()
            if ln in _TRANSPORT_HEADERS_EXCLUDED_FROM_EXACT_MATCH:
                continue
            raw_name = next(
                (
                    str(hx.get("name"))
                    for hx in rq.get("headers") or []
                    if isinstance(hx, dict) and str(hx.get("name", "")).strip().lower() == ln
                ),
                str(h.get("name", "")),
            )
            targets.add(f"{rel_contract_file}#{oid}.request.headers.{raw_name}")

    body = rq.get("body") or {}
    if isinstance(body, dict):
        for f in body.get("fields") or []:
            if isinstance(f, dict) and f.get("required"):
                targets.add(f"{rel_contract_file}#{oid}.request.body.{f['name']}")
    return targets


def parse_contract_ref(ref: Any) -> tuple[str | None, str | None]:
    if not isinstance(ref, str) or "#" not in ref:
        return None, None
    left, right = ref.split("#", 1)
    ls, rs = left.strip(), right.strip()
    return (ls or None, rs or None)


def dotted_get_local(obj: Any, path_parts: list[str]) -> Any:
    cur = obj
    for part in path_parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def yaml_anchor_under_data_root(data_root: Path, rel_file: str, anchor: str) -> bool:
    p = data_root / rel_file.replace("\\", "/")
    if not p.is_file():
        return False
    if p.suffix == ".dbml":
        text = p.read_text(encoding="utf-8")
        if "." not in anchor:
            return False
        table_name, column_name = anchor.split(".", 1)
        table_match = re.search(rf"(?ms)^Table\s+{re.escape(table_name)}\s*\{{(.*?)^}}", text)
        if not table_match:
            return False
        body = table_match.group(1)
        return re.search(rf"(?m)^\s*{re.escape(column_name)}\s+\w+", body) is not None
    doc = load_yaml(p)
    if doc is None:
        return False
    if isinstance(doc, dict) and isinstance(doc.get("entities"), list):
        if "." not in anchor:
            return False
        ent, tail = anchor.split(".", 1)
        segments = tail.split(".")
        first_level = segments[0]
        for e in doc.get("entities") or []:
            if not isinstance(e, dict):
                continue
            if str(e.get("entity_id")) != ent:
                continue
            fnames = {str(f.get("name")) for f in (e.get("fields") or []) if isinstance(f, dict)}
            if first_level in fnames and len(segments) == 1:
                return True
        return False
    pp = [x for x in anchor.split(".") if x]
    return dotted_get_local(doc, pp) is not None


def collect_response_specs(resp: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    fields = resp.get("fields") or []
    for f in fields:
        if not isinstance(f, dict):
            continue
        fn = str(f.get("name", "")).strip()
        if not fn:
            continue
        names.add(fn)
        for kid in f.get("item_fields") or []:
            if isinstance(kid, dict) and kid.get("name"):
                names.add(f"{fn}.{kid['name']}")
    return names


def is_id_like_target(tgt: str) -> bool:
    tail = tgt.split("#", 1)[-1].split(":")[-1]
    last = tail.split(".")[-1]
    return bool(re.search(r"(^id$|_id$|Id$|ID$|\.id$)", last))


def has_id_word(name: str) -> bool:
    return bool(re.search(r"(^|[\s_-])ID($|[\s_-])|id", name, re.IGNORECASE))


def raw_payload_smell(name: str) -> bool:
    return bool(re.search(r"(json|yaml|payload|dto|request\s*body|api\s*body|db\s*row)", name, re.IGNORECASE))


def verify_contract_anchor_tail(tail: str, op_doc: dict[str, Any]) -> tuple[bool, str | None]:
    """tail = '{op}.request.{params|body|headers}.{...}'"""
    segments = tail.split(".")
    if len(segments) < 4:
        return False, "contract anchor tail too short"
    oid_seg, req_kw, bucket = segments[0], segments[1], segments[2]
    _rest = segments[3:]
    if oid_seg != str(op_doc.get("operation_id", "")):
        return False, f"operation_id mismatch in anchor tail ({oid_seg})"
    if req_kw != "request":
        return False, "expected .request. in contract anchor"
    rq = op_doc.get("request")
    if not isinstance(rq, dict):
        return False, "operation has no request block"
    if bucket == "params":
        name = _rest[0] if _rest else ""
        for p in rq.get("params") or []:
            if isinstance(p, dict) and str(p.get("name")) == name:
                return True, None
        return False, f"unknown request.params.{name}"
    if bucket == "body":
        name = _rest[0] if _rest else ""
        body = rq.get("body") or {}
        fields = body.get("fields") if isinstance(body, dict) else None
        if not isinstance(fields, list):
            return False, "no request.body.fields"
        for fld in fields:
            if isinstance(fld, dict) and str(fld.get("name")) == name:
                return True, None
        return False, f"unknown request.body.{name}"
    if bucket == "headers":
        name = _rest[0] if _rest else ""
        for h in rq.get("headers") or []:
            if isinstance(h, dict) and str(h.get("name")) == name:
                return True, None
        return False, f"unknown request.headers.{name}"
    if bucket == "response" and _rest[:1] == ["fields"]:
        resp = op_doc.get("response")
        if not isinstance(resp, dict):
            return False, "no response"
        allowed = collect_response_specs(resp)
        deep = ".".join(_rest[1:])
        if deep in allowed or deep.split(".")[0] in allowed:
            return True, None
        return False, f"unknown response field path {deep}"
    return True, None


def response_probe_top(path_suffix: str) -> str:
    s = path_suffix.strip().lstrip("$").lstrip(".").strip()
    s = re.sub(r"\[\*\]", "", s)
    return s.split(".", 1)[0] if s else ""


# ---------------------------------------------------------------------------
# Aggregate-given DBML NOT-NULL coverage gate (rule-oriented).
#
# `aibdd-plan` requires every `L4.preset.handler == aggregate-given` DSL entry
# to fully bind the NOT-NULL columns of its target DBML table. Each rule below
# is a single predicate over `DbmlColumn`; the gate composes them via
# `_first_match` instead of nested conditionals.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DbmlColumn:
    name: str
    raw_type: str
    modifiers: tuple[str, ...]  # lowercased modifier tokens, e.g. "pk", "not null", "default: now()"

    def has(self, token: str) -> bool:
        return token in self.modifiers

    def has_prefix(self, prefix: str) -> bool:
        return any(m.startswith(prefix) for m in self.modifiers)


@dataclass(frozen=True)
class ExemptionRule:
    rule_id: str
    description: str
    matches: Callable[[DbmlColumn], bool]


# Each rule answers exactly one question: "is this NOT-NULL column allowed to
# stay unbound by an aggregate-given builder?" — first match wins, order matters
# only for diagnostic clarity (more specific rules first).
_AGGREGATE_GIVEN_EXEMPTIONS: tuple[ExemptionRule, ...] = (
    ExemptionRule(
        rule_id="pk-auto-increment",
        description="PK marked [increment] is generated by the database.",
        matches=lambda col: col.has("pk") and col.has("increment"),
    ),
    ExemptionRule(
        rule_id="dbml-explicit-default",
        description="Column declares an explicit DBML [default: ...] modifier.",
        matches=lambda col: col.has_prefix("default:") or col.has("default"),
    ),
)


def _is_dbml_column_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith("//"):
        return False
    keyword = s.split(None, 1)[0].lower()
    return keyword not in {"note:", "note", "indexes", "ref:", "enum"}


_DBML_COLUMN_HEAD_RE = re.compile(r"^(\w+)\s+([\w\(\),\s]+?)(?:\s+\[(.*)$|\s*$)")
_DBML_TABLE_RE = re.compile(r"(?ms)^Table\s+(\w+)\s*\{(.*?)^\}", re.MULTILINE)
_DBML_MODIFIER_GROUP_RE = re.compile(r"\[([^\]]*)\]")


def _parse_dbml_column(line: str) -> DbmlColumn | None:
    if not _is_dbml_column_line(line):
        return None
    stripped = line.strip()
    head = re.match(r"^(\w+)\s+([\w\(\)]+)\s*(.*)$", stripped)
    if head is None:
        return None
    name, raw_type, tail = head.group(1), head.group(2), head.group(3) or ""
    if name.lower() == "table":
        return None
    modifiers: list[str] = []
    for group in _DBML_MODIFIER_GROUP_RE.findall(tail):
        for token in group.split(","):
            t = token.strip().lower()
            if t:
                modifiers.append(t)
    return DbmlColumn(name=name, raw_type=raw_type, modifiers=tuple(modifiers))


def _parse_dbml_tables(dbml_text: str) -> dict[str, list[DbmlColumn]]:
    tables: dict[str, list[DbmlColumn]] = {}
    for match in _DBML_TABLE_RE.finditer(dbml_text):
        table_name, body = match.group(1), match.group(2)
        cols = (_parse_dbml_column(line) for line in body.splitlines())
        tables[table_name] = [c for c in cols if c is not None]
    return tables


def _load_dbml_table_cache(data_dir: Path | None) -> dict[tuple[str, str], list[DbmlColumn]]:
    """Returns: {(rel_dbml_path_with_data_prefix, table_name): [DbmlColumn, ...]}."""
    cache: dict[tuple[str, str], list[DbmlColumn]] = {}
    if data_dir is None or not data_dir.is_dir():
        return cache
    for dbml in sorted(data_dir.rglob("*.dbml")):
        rel = "data/" + dbml.relative_to(data_dir).as_posix()
        text = dbml.read_text(encoding="utf-8")
        for tname, cols in _parse_dbml_tables(text).items():
            cache[(rel, tname)] = cols
    return cache


def _is_not_null(col: DbmlColumn) -> bool:
    # `[pk]` columns are implicitly NOT NULL even without an explicit `[not null]`.
    return col.has("pk") or col.has("not null")


def _first_exemption_match(col: DbmlColumn) -> ExemptionRule | None:
    return next((rule for rule in _AGGREGATE_GIVEN_EXEMPTIONS if rule.matches(col)), None)


def _required_not_null_columns(cols: list[DbmlColumn]) -> set[str]:
    return {c.name for c in cols if _is_not_null(c) and _first_exemption_match(c) is None}


def _bound_data_columns(l4: dict[str, Any], target_dbml_file: str, target_table: str) -> set[str]:
    bound: set[str] = set()
    for group_name in ("param_bindings", "datatable_bindings", "default_bindings"):
        group = l4.get(group_name)
        if not isinstance(group, dict):
            continue
        for binding in group.values():
            tgt = binding_target(binding)
            if not tgt.startswith(target_dbml_file + "#"):
                continue
            anchor = tgt.split("#", 1)[1]
            if "." not in anchor:
                continue
            tbl, col = anchor.split(".", 1)
            if tbl == target_table:
                bound.add(col)
    return bound


def check_aggregate_given_coverage(
    entry_id: str,
    l4: dict[str, Any],
    dbml_tables: dict[tuple[str, str], list[DbmlColumn]],
    path: Path,
) -> list[dict[str, Any]]:
    preset = l4.get("preset")
    if not isinstance(preset, dict) or preset.get("handler") != "aggregate-given":
        return []
    refs = l4.get("source_refs") or {}
    data_ref = str((refs or {}).get("data") or "")
    if not data_ref.startswith("data/") or "#" not in data_ref:
        return [violation(
            "DSL_AGG_GIVEN_DATA_REF_MISSING",
            str(path),
            f"{entry_id} aggregate-given entry needs L4.source_refs.data shape data/<file>.dbml#<table>",
        )]
    rel_file, anchor = data_ref.split("#", 1)
    table_name = anchor.split(".", 1)[0]
    cols = dbml_tables.get((rel_file, table_name))
    if cols is None:
        return [violation(
            "DSL_AGG_GIVEN_TABLE_NOT_FOUND",
            str(path),
            f"{entry_id} aggregate-given target table {data_ref} not found in DBML",
        )]
    required = _required_not_null_columns(cols)
    bound = _bound_data_columns(l4, rel_file, table_name)
    missing = sorted(required - bound)
    if not missing:
        return []
    return [violation(
        "DSL_AGG_GIVEN_NOT_NULL_UNCOVERED",
        str(path),
        f"{entry_id} aggregate-given builder for table {table_name} missing NOT-NULL bindings {missing}",
    )]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_dsl_entries.py <.aibdd/arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    violations: list[dict[str, Any]] = []

    allowed_target_prefixes = _resolve_allowed_target_prefixes(args_path, args, violations)
    if allowed_target_prefixes is None:
        return emit(False, "dsl entry check", violations)

    sdk = str(args.get("BOUNDARY_SHARED_DSL", "")).lower()
    pkd = str(args.get("BOUNDARY_PACKAGE_DSL", "")).lower()
    if "dsl.md" in sdk or "dsl.md" in pkd:
        violations.append(
            violation(
                "DSL_REGISTRY_PATH_LEGACY_MD",
                str(args_path),
                "BOUNDARY_SHARED_DSL / BOUNDARY_PACKAGE_DSL must use dsl.yml, not dsl.md",
            )
        )

    dsl_paths: list[Path] = []
    for key in ("BOUNDARY_PACKAGE_DSL", "BOUNDARY_SHARED_DSL"):
        pth = resolve_arg_path(args_path, args, key)
        if pth and pth.is_file():
            dsl_paths.append(pth)
            if str(pth).endswith(".md"):
                violations.append(violation("DSL_FILE_WRONG_EXT", str(pth), "DSL registry must be .yml"))

    contracts_dir = resolve_arg_path(args_path, args, "CONTRACTS_DIR")
    data_dir = resolve_arg_path(args_path, args, "DATA_DIR")
    op_index = load_operations_index(contracts_dir)
    dbml_tables = _load_dbml_table_cache(data_dir)

    all_entries: list[tuple[Path, dict[str, Any]]] = []
    for pth in dsl_paths:
        all_entries.extend((pth, entry) for entry in entries_from(pth))

    for path, entry in all_entries:
        entry_id = str(entry.get("id", "<missing-id>"))
        for layer in ("L1", "L2", "L3", "L4"):
            if layer not in entry:
                violations.append(violation("DSL_LAYER_MISSING", str(path), f"{entry_id} missing {layer}"))

        l1 = entry.get("L1") or {}
        l4 = entry.get("L4") or {}
        src_block: dict[str, Any] = {}
        if isinstance(l4, dict) and isinstance(l4.get("source_refs"), dict):
            src_block = l4["source_refs"]
        elif isinstance(entry.get("source_refs"), dict):
            src_block = entry["source_refs"]

        l1_texts: list[str] = []
        if isinstance(l1, dict):
            for k in ("given", "when"):
                if l1.get(k):
                    l1_texts.append(str(l1[k]))
            then = l1.get("then") or []
            if isinstance(then, list):
                l1_texts.extend(str(x) for x in then)
            elif then:
                l1_texts.append(str(then))
        ph: set[str] = set()
        for text in l1_texts:
            ph.update(placeholders(text))

        param_bindings = l4.get("param_bindings") if isinstance(l4, dict) else None
        datatable_bindings = l4.get("datatable_bindings") if isinstance(l4, dict) else None
        default_bindings = l4.get("default_bindings") if isinstance(l4, dict) else None
        assertion_bindings = l4.get("assertion_bindings") if isinstance(l4, dict) else None

        if ph and not isinstance(param_bindings, dict) and not isinstance(assertion_bindings, dict):
            violations.append(violation("DSL_BINDINGS_MISSING", str(path), f"{entry_id} has placeholders but no bindings"))

        surface_kind = str((l4 or {}).get("surface_kind", "") or "")
        cf, op_anchor_id = parse_contract_ref(src_block.get("contract"))
        op_doc: dict[str, Any] | None = (
            op_index.get((cf, op_anchor_id), None)
            if contracts_dir is not None and cf and op_anchor_id and cf.startswith("contracts/")
            else None
        )

        allowed_response_specs: set[str] = set()
        if isinstance(op_doc, dict) and isinstance(op_doc.get("response"), dict):
            allowed_response_specs = collect_response_specs(op_doc["response"])

        for name in ph:
            in_param = isinstance(param_bindings, dict) and name in param_bindings
            in_assert = isinstance(assertion_bindings, dict) and name in assertion_bindings
            if not in_param and not in_assert:
                violations.append(violation("DSL_PLACEHOLDER_UNBOUND", str(path), f"{entry_id} placeholder {{{name}}} is unbound"))
            if in_param and in_assert:
                violations.append(violation("DSL_PLACEHOLDER_AMBIGUOUS", str(path), f"{entry_id} placeholder {{{name}}} appears in both param and assertion bindings"))

        def check_contract_data_target(where: str, bname: str, tgt: str) -> None:
            if tgt.startswith("contracts/"):
                if "#" not in tgt:
                    violations.append(violation("DSL_CONTRACT_TARGET_SHAPE", str(path), f"{entry_id}.{where}.{bname} missing #: {tgt}"))
                    return
                lf_raw, anchor_tail = tgt.split("#", 1)
                lf = lf_raw.replace("\\", "/")
                if contracts_dir:
                    slug = lf[len("contracts/") :].lstrip("/") if lf.startswith("contracts/") else lf
                    abs_c = contracts_dir / slug
                    if not abs_c.is_file():
                        violations.append(violation("DSL_CONTRACT_PATH_MISSING", str(path), f"{entry_id}.{where}.{bname}: {lf}"))
                if cf and lf != cf:
                    violations.append(
                        violation(
                            "DSL_CONTRACT_REF_FILE_MISMATCH",
                            str(path),
                            f"{entry_id}.{where}.{bname} file {lf} != source_refs.contract file {cf}",
                        )
                    )
                if op_doc is not None and op_anchor_id:
                    ok, err = verify_contract_anchor_tail(anchor_tail, op_doc)
                    if not ok:
                        violations.append(
                            violation("DSL_CONTRACT_ANCHOR_INVALID", str(path), f"{entry_id}.{where}.{bname}: {err} (#{anchor_tail})")
                        )
            if tgt.startswith("data/"):
                tail = tgt[len("data/") :]
                if "#" not in tail:
                    violations.append(violation("DSL_DATA_TARGET_SHAPE", str(path), f"{entry_id}.{where}.{bname} missing #: {tgt}"))
                elif data_dir is not None:
                    rel_file, ank = tail.split("#", 1)
                    if not yaml_anchor_under_data_root(data_dir, rel_file.strip(), ank.strip()):
                        violations.append(violation("DSL_DATA_ANCHOR_MISSING", str(path), f"{entry_id}.{where}.{bname}: {tgt}"))
            if tgt.startswith("response:"):
                suf = tgt[len("response:") :]
                if "__http." in suf or suf.startswith("$.__http"):
                    return
                top = response_probe_top(suf)
                if top and top == "error":
                    return
                if allowed_response_specs and top and top not in allowed_response_specs:
                    violations.append(
                        violation(
                            "DSL_ASSERTION_RESPONSE_TOP_UNKNOWN",
                            str(path),
                            f"{entry_id}.{where}.{bname}: top `{top}` not in operation response.fields for {cf}#{op_anchor_id}",
                        )
                    )

        for group_name, group in (
            ("param_bindings", param_bindings),
            ("datatable_bindings", datatable_bindings),
            ("default_bindings", default_bindings),
            ("assertion_bindings", assertion_bindings),
        ):
            if isinstance(group, dict):
                for bname, binding in group.items():
                    tgt = binding_target(binding)
                    if not tgt.startswith(allowed_target_prefixes):
                        violations.append(violation("DSL_BINDING_TARGET_INVALID", str(path), f"{entry_id}.{group_name}.{bname}: {tgt}"))
                    check_contract_data_target(group_name, str(bname), tgt)
                    if is_id_like_target(tgt) and not has_id_word(str(bname)):
                        violations.append(
                            violation(
                                "DSL_ID_KEY_OPAQUE",
                                str(path),
                                f"{entry_id}.{group_name}.{bname} targets ID-like field but key does not say ID ({tgt})",
                            )
                        )
                    if group_name == "datatable_bindings":
                        if raw_payload_smell(str(bname)):
                            violations.append(
                                violation(
                                    "DSL_DATATABLE_RAW_PAYLOAD_SMELL",
                                    str(path),
                                    f"{entry_id}.{group_name}.{bname} looks like raw technical payload, not business projection",
                                )
                            )
                        if isinstance(binding, dict):
                            has_group = bool(binding.get("group"))
                            has_item = bool(binding.get("item_field"))
                            if has_group != has_item:
                                violations.append(
                                    violation(
                                        "DSL_DATATABLE_GROUP_ITEM_FIELD_INCOMPLETE",
                                        str(path),
                                        f"{entry_id}.{group_name}.{bname} must use group and item_field together",
                                    )
                                )
                    if group_name == "default_bindings":
                        if not isinstance(binding, dict):
                            violations.append(
                                violation("DSL_DEFAULT_BINDING_SHAPE", str(path), f"{entry_id}.{group_name}.{bname} must be a mapping")
                            )
                            continue
                        for req_key in ("target", "value", "reason", "override_via"):
                            if req_key not in binding:
                                violations.append(
                                    violation(
                                        "DSL_DEFAULT_BINDING_FIELD_MISSING",
                                        str(path),
                                        f"{entry_id}.{group_name}.{bname} missing {req_key}",
                                    )
                                )

        if isinstance(l4, dict):
            for reqf in ("surface_id", "surface_kind", "callable_via", "source_refs"):
                if reqf not in l4:
                    violations.append(violation("DSL_L4_FIELD_MISSING", str(path), f"{entry_id} missing L4.{reqf}"))

        if surface_kind == "operation":
            if isinstance(assertion_bindings, dict) and assertion_bindings:
                violations.append(
                    violation("DSL_OPERATION_HAS_ASSERTIONS", str(path), f"{entry_id} operation entry must not own assertion_bindings")
                )
            if not cf or not op_anchor_id:
                violations.append(violation("DSL_OPERATION_NO_CONTRACT_REF", str(path), f"{entry_id} needs source_refs.contract"))
            elif op_doc is None:
                violations.append(
                    violation(
                        "DSL_CONTRACT_OP_LOOKUP_FAIL",
                        str(path),
                        f"{entry_id} contract {cf}#{op_anchor_id} not found",
                    )
                )
            elif isinstance(op_doc.get("request"), dict) and cf:
                req_set = required_input_binding_targets(cf, op_doc)
                got_set: set[str] = set()
                for group in (param_bindings, datatable_bindings, default_bindings):
                    if isinstance(group, dict):
                        for bv in group.values():
                            bt = binding_target(bv)
                            if bt.startswith("contracts/"):
                                got_set.add(bt)
                missing = req_set - got_set
                extra = got_set - req_set
                if missing:
                    violations.append(
                        violation(
                            "DSL_PARAM_MISSING_REQUIRED_CONTRACT_INPUT",
                            str(path),
                            f"{entry_id} missing bindings {sorted(missing)}",
                        )
                    )
                if extra:
                    violations.append(
                        violation(
                            "DSL_PARAM_EXTRA_CONTRACT_BINDING",
                            str(path),
                            f"{entry_id} extra or non-input contract bindings {sorted(extra)}",
                        )
                    )
        elif isinstance(assertion_bindings, dict):
            for bname, bv in assertion_bindings.items():
                bt = binding_target(bv)
                if ".request." in bt and bt.startswith("contracts/"):
                    violations.append(
                        violation(
                            "DSL_ASSERTION_BINDS_CONTRACT_REQUEST",
                            str(path),
                            f"{entry_id}.assertion_bindings.{bname} must not bind contract request input {bt}",
                        )
                    )

        if isinstance(l4, dict):
            violations.extend(check_aggregate_given_coverage(entry_id, l4, dbml_tables, path))

    return emit(not violations, "dsl entry check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
