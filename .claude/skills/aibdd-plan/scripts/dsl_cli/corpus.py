from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


def discover_dsl_paths(truth_boundary_root: Path) -> list[Path]:
    root = truth_boundary_root.resolve()
    out: list[Path] = []
    shared = root / "shared" / "dsl.yml"
    if shared.is_file():
        out.append(shared)
    packages = root / "packages"
    if packages.is_dir():
        for pkg in sorted(packages.iterdir(), key=lambda p: p.name):
            if pkg.is_dir():
                candidate = pkg / "dsl.yml"
                if candidate.is_file():
                    out.append(candidate)
    return out


def load_dsl_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not data:
        return []
    entries = data.get("entries")
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise ValueError(f"{path}: entries must be a list, got {type(entries)}")
    return [e for e in entries if isinstance(e, dict)]


def l1_to_text(l1: Any) -> str:
    if l1 is None:
        return ""
    if isinstance(l1, str):
        return l1.strip()
    if isinstance(l1, dict):
        parts: list[str] = []
        for key in ("when", "then", "given"):
            block = l1.get(key)
            if isinstance(block, list):
                parts.extend(str(x) for x in block)
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return str(l1)


def normalize_l1_for_compare(l1_text: str) -> str:
    s = l1_text.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def flatten_entry_haystack(entry: dict[str, Any]) -> str:
    parts: list[str] = []
    eid = entry.get("id")
    if eid is not None:
        parts.append(str(eid))
    parts.append(l1_to_text(entry.get("L1")))
    l4 = entry.get("L4")
    if isinstance(l4, dict):
        sid = l4.get("surface_id")
        if sid is not None:
            parts.append(str(sid))
        parts.append(yaml.safe_dump(l4.get("source_refs"), allow_unicode=True, default_flow_style=True))
        for key in ("param_bindings", "assertion_bindings"):
            b = l4.get(key)
            if isinstance(b, dict):
                for v in b.values():
                    if isinstance(v, dict) and "target" in v:
                        parts.append(str(v.get("target")))
                    else:
                        parts.append(str(v))
        db = l4.get("datatable_bindings")
        if isinstance(db, dict):
            parts.append(yaml.safe_dump(db, allow_unicode=True))
        defaults = l4.get("default_bindings")
        if isinstance(defaults, list):
            for row in defaults:
                if isinstance(row, dict) and "target" in row:
                    parts.append(str(row.get("target")))
    return "\n".join(parts)


def preset_handler(entry: dict[str, Any]) -> str:
    l4 = entry.get("L4")
    if not isinstance(l4, dict):
        return ""
    preset = l4.get("preset")
    if isinstance(preset, dict):
        h = preset.get("handler")
        return str(h) if h is not None else ""
    return ""


def collect_operation_ids_in_openapi(data: Any, out: set[str]) -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "operationId" and isinstance(v, str):
                out.add(v)
            else:
                collect_operation_ids_in_openapi(v, out)
    elif isinstance(data, list):
        for item in data:
            collect_operation_ids_in_openapi(item, out)


def index_contract_operation_ids(contracts_root: Path) -> dict[str, set[str]]:
    """Map relative posix path (from contracts_root) to set of operationId strings."""
    root = contracts_root.resolve()
    index: dict[str, set[str]] = {}
    if not root.is_dir():
        return index
    for path in sorted(root.rglob("*.yml")):
        if not path.is_file():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        opids: set[str] = set()
        collect_operation_ids_in_openapi(data, opids)
        if opids:
            rel = path.relative_to(root).as_posix()
            index[rel] = opids
    return index
