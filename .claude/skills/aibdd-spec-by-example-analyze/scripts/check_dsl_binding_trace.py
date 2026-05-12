#!/usr/bin/env python3
"""
check_dsl_binding_trace.py — BDD Analysis Quality Gate 5a

Validates that BDD examples consume /aibdd-plan DSL bindings instead of
inventing physical mappings locally.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCENARIO_RE = re.compile(r"^\s*(Scenario Outline|Scenario|Example)\s*:", re.IGNORECASE | re.MULTILINE)
DSL_ENTRY_RE = re.compile(r"#\s*@dsl_entry\s+([A-Za-z0-9_.:-]+)")
BINDING_KEYS_RE = re.compile(r"#\s*@binding_keys\s+(.+)")
CONTRACT_TARGET_RE = re.compile(r"^contracts/([^#]+)#([^.\s]+)")


def _violation(rule_id: str, file: str, line: int, msg: str) -> dict:
    return {"rule_id": rule_id, "file": file, "line": line, "msg": msg}


def _workspace_root() -> Path:
    skill_dir = Path(__file__).resolve().parent.parent
    return skill_dir.parents[2]


def _load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(f"PyYAML required: {exc}")
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _resolve_plan_paths(args_path: Path) -> dict:
    resolver = (
        _workspace_root()
        / ".claude"
        / "skills"
        / "aibdd-plan"
        / "scripts"
        / "python"
        / "resolve_plan_paths.py"
    )
    proc = subprocess.run(
        [sys.executable, str(resolver), str(args_path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise SystemExit(
            json.dumps(
                {
                    "ok": False,
                    "summary": {"violations": 1},
                    "violations": [
                        _violation("PLAN_RESOLVER_FAILED", str(args_path), 0, proc.stderr.strip() or proc.stdout.strip())
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return json.loads(proc.stdout)


def _openapi_operations(contracts_dir: Path) -> set[str]:
    ops: set[str] = set()
    if not contracts_dir.exists():
        return ops
    for path in sorted(list(contracts_dir.rglob("*.yml")) + list(contracts_dir.rglob("*.yaml"))):
        raw = _load_yaml(path) or {}
        paths = raw.get("paths") if isinstance(raw, dict) else {}
        if not isinstance(paths, dict):
            continue
        for item in paths.values():
            if not isinstance(item, dict):
                continue
            for op in item.values():
                if isinstance(op, dict) and op.get("operationId"):
                    ops.add(str(op["operationId"]))
    return ops


def _dbml_targets(data_dir: Path) -> set[str]:
    targets: set[str] = set()
    if not data_dir.exists():
        return targets
    table = None
    table_re = re.compile(r"^\s*Table\s+([A-Za-z0-9_]+)")
    field_re = re.compile(r"^\s*([A-Za-z0-9_]+)\s+")
    for path in data_dir.rglob("*.dbml"):
        for raw in path.read_text(encoding="utf-8").splitlines():
            mt = table_re.match(raw)
            if mt:
                table = mt.group(1)
                continue
            if table and raw.strip().startswith("}"):
                table = None
                continue
            mf = field_re.match(raw)
            if table and mf:
                targets.add(f"data/{path.name}#{table}.{mf.group(1)}")
    return targets


def _collect_dsl(paths: dict) -> tuple[dict[str, dict], list[dict]]:
    entries: dict[str, dict] = {}
    violations: list[dict] = []
    for raw_path in [paths["boundary_package_dsl"], paths.get("boundary_shared_dsl")]:
        if not raw_path:
            continue
        path = Path(raw_path)
        if not path.exists():
            continue
        raw = _load_yaml(path) or {}
        dsl_entries = raw.get("entries") if isinstance(raw, dict) else None
        if not isinstance(dsl_entries, list):
            continue
        for entry in dsl_entries:
            if not isinstance(entry, dict):
                continue
            entry_id = str(entry.get("id") or "")
            if not entry_id:
                violations.append(_violation("DSL_ENTRY_ID_MISSING", str(path), 0, "DSL entry missing id"))
                continue
            entries[entry_id] = entry
    return entries, violations


def _binding_targets(entry: dict) -> dict[str, str]:
    l4 = entry.get("L4") if isinstance(entry.get("L4"), dict) else {}
    out: dict[str, str] = {}
    for section in ("param_bindings", "datatable_bindings", "default_bindings", "assertion_bindings"):
        section_value = l4.get(section) if isinstance(l4, dict) else None
        if not isinstance(section_value, dict):
            continue
        for key, spec in section_value.items():
            if isinstance(spec, dict) and spec.get("target"):
                out[str(key)] = str(spec["target"])
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Validate Scenario/Examples trace to /aibdd-plan DSL bindings")
    p.add_argument("--args", dest="args_path", required=True, help="arguments.yml")
    args = p.parse_args()

    paths = _resolve_plan_paths(Path(args.args_path).resolve())
    features_dir = Path(paths["features_dir"])
    contracts_dir = Path(paths["truth_boundary_root"]) / "contracts"
    data_dir = Path(paths["truth_boundary_root"]) / "data"
    operations = _openapi_operations(contracts_dir)
    dbml_targets = _dbml_targets(data_dir)
    dsl_entries, violations = _collect_dsl(paths)

    summary = {
        "features_dir": str(features_dir),
        "dsl_entries": len(dsl_entries),
        "features_scanned": 0,
        "scenarios_with_trace": 0,
        "violations": 0,
    }

    for entry_id, entry in dsl_entries.items():
        l4 = entry.get("L4") if isinstance(entry.get("L4"), dict) else {}
        if not isinstance(l4.get("preset"), dict) or not l4["preset"].get("name"):
            violations.append(_violation("DSL_PRESET_MISSING", entry_id, 0, "DSL entry missing L4.preset.name"))
        for key, target in _binding_targets(entry).items():
            if target.startswith("contracts/"):
                match = CONTRACT_TARGET_RE.match(target)
                if not match or match.group(2) not in operations:
                    violations.append(_violation("DSL_CONTRACT_TARGET_MISSING", entry_id, 0, f"binding {key} target not found in OpenAPI operations: {target}"))
            elif target.startswith("data/"):
                if target not in dbml_targets:
                    violations.append(_violation("DSL_DATA_TARGET_MISSING", entry_id, 0, f"binding {key} target not found in DBML: {target}"))
            elif not (
                target.startswith("response:")
                or target.startswith("fixture:")
                or target.startswith("stub_payload:")
                or target.startswith("literal:")
            ):
                violations.append(_violation("DSL_TARGET_PREFIX_INVALID", entry_id, 0, f"binding {key} has invalid target prefix: {target}"))

    if features_dir.exists():
        for feature in sorted(features_dir.rglob("*.feature")):
            summary["features_scanned"] += 1
            text = feature.read_text(encoding="utf-8")
            if not SCENARIO_RE.search(text):
                continue
            entry_refs = DSL_ENTRY_RE.findall(text)
            if not entry_refs:
                violations.append(_violation("SCENARIO_DSL_TRACE_MISSING", str(feature), 0, "feature has scenarios but no # @dsl_entry trace"))
                continue
            for entry_id in entry_refs:
                if entry_id not in dsl_entries:
                    violations.append(_violation("SCENARIO_DSL_ENTRY_UNKNOWN", str(feature), 0, f"# @dsl_entry references unknown DSL entry: {entry_id}"))
                else:
                    summary["scenarios_with_trace"] += 1
            for keys_line in BINDING_KEYS_RE.findall(text):
                keys = [k.strip() for k in re.split(r"[, ]+", keys_line) if k.strip()]
                valid_keys = set()
                for entry_id in entry_refs:
                    if entry_id in dsl_entries:
                        valid_keys.update(_binding_targets(dsl_entries[entry_id]).keys())
                for key in keys:
                    if key not in valid_keys:
                        violations.append(_violation("SCENARIO_BINDING_KEY_UNKNOWN", str(feature), 0, f"# @binding_keys references unknown key: {key}"))

    summary["violations"] = len(violations)
    result = {"ok": len(violations) == 0, "summary": summary, "violations": violations}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
