#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def emit(ok: bool, summary: str, violations: list[dict[str, Any]]) -> int:
    print(json.dumps({"ok": ok, "summary": summary, "violations": violations}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def violation(rule_id: str, file: str, msg: str, line: int | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"rule_id": rule_id, "file": file, "msg": msg}
    if line is not None:
        item["line"] = line
    return item


VAR_RE = re.compile(r"\$\{([^}]+)\}")
SECTION_RE = re.compile(
    r"^## Impacted Feature Files\s*$\n(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
FEATURE_TITLE_RE = re.compile(r"^\s*Feature:\s*(?P<title>.+?)\s*$", re.MULTILINE)


def read_args(path: Path) -> dict[str, str]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"PyYAML is required to parse {path}: {exc}")

    if not path.exists():
        raise SystemExit(f"arguments file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"arguments file empty: {path}")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit(f"arguments file must be a mapping: {path}")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def expand_vars(value: str, mapping: dict[str, str], limit: int = 10) -> str:
    result = value
    for _ in range(limit):
        changed = False

        def repl(match: re.Match[str]) -> str:
            nonlocal changed
            key = match.group(1)
            if key in mapping:
                changed = True
                return mapping[key]
            return match.group(0)

        result = VAR_RE.sub(repl, result)
        if not changed:
            break
    return result


def load_boundary_id(args_path: Path, args: dict[str, str]) -> str | None:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"PyYAML is required to parse boundary.yml: {exc}")

    boundary_rel = expand_vars(args.get("BOUNDARY_YML", ""), args)
    if not boundary_rel:
        return None
    p = Path(boundary_rel)
    if not p.is_absolute():
        p = specs_root(args_path, args).parent / p
    p = p.resolve()
    if not p.is_file():
        return None
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    boundaries = raw.get("boundaries") if isinstance(raw, dict) else None
    if not boundaries:
        return None
    return str(boundaries[0].get("id") or "").strip() or None


def apply_boundary(value: str, boundary_id: str | None) -> str:
    if not boundary_id:
        return value
    return value.replace("<boundary>", boundary_id)


def specs_root(args_path: Path, args: dict[str, str]) -> Path:
    root = expand_vars(args.get("SPECS_ROOT_DIR", "specs"), args)
    p = Path(root)
    if not p.is_absolute():
        backend_root = args_path.parent.parent if args_path.parent.name == ".aibdd" else args_path.parent
        p = backend_root / p
    return p.resolve()


def resolve_arg_path(args_path: Path, args: dict[str, str], key: str) -> Path | None:
    value = args.get(key)
    if not value:
        return None
    expanded = expand_vars(value, args)
    expanded = apply_boundary(expanded, load_boundary_id(args_path, args))
    p = Path(expanded)
    if not p.is_absolute():
        p = specs_root(args_path, args).parent / p
    return p.resolve()


def extract_impacted_feature_paths(plan_md: str) -> list[str]:
    match = SECTION_RE.search(plan_md)
    if not match:
        return []
    items: list[str] = []
    for raw in match.group("body").splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        path_match = re.search(r"`([^`]+\.feature)`|([^\s`]+\.feature)", line)
        if not path_match:
            continue
        items.append((path_match.group(1) or path_match.group(2) or "").strip())
    return items


def feature_title(text: str) -> str:
    match = FEATURE_TITLE_RE.search(text)
    if match:
        return match.group("title").strip()
    return ""


def basename_no_suffix(path: str) -> str:
    return Path(path).stem
