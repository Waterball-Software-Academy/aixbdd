#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit(f"PyYAML is required to parse {path}: {exc}")

    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return None
    return yaml.safe_load(text)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def emit(ok: bool, summary: str, violations: list[dict[str, Any]]) -> int:
    print(json.dumps({"ok": ok, "summary": summary, "violations": violations}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def violation(rule_id: str, file: str, msg: str, line: int | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"rule_id": rule_id, "file": file, "msg": msg}
    if line is not None:
        item["line"] = line
    return item


def read_args(path: Path) -> dict[str, str]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit(f"PyYAML is required to parse {path}: {exc}")

    if not path.exists():
        raise SystemExit(f"arguments file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"arguments file empty: {path}")

    try:
        data = yaml.safe_load(text)
    except yaml.composer.ComposerError:
        # Multi-document YAML: safe_load refuses; use the *first* mapping document
        # (convention: document 1 = flat path bindings for resolver).
        data = None
        for doc in yaml.safe_load_all(text):
            if isinstance(doc, dict):
                data = doc
                break
        if not isinstance(data, dict):
            raise SystemExit(
                f"arguments file must start with a mapping (multi-doc stream): {path}"
            )

    if not isinstance(data, dict):
        raise SystemExit(f"arguments file must be a mapping: {path}")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


VAR_RE = re.compile(r"\$\{([^}]+)\}")


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
    """Load boundary id from BOUNDARY_YML when present (kickoff convention)."""
    boundary_rel = expand_vars(args.get("BOUNDARY_YML", ""), args)
    if not boundary_rel:
        return None
    p = Path(boundary_rel)
    if not p.is_absolute():
        p = specs_root(args_path, args).parent / p
    p = p.resolve()
    if not p.is_file():
        return None
    raw = load_yaml(p) or {}
    boundaries = raw.get("boundaries") if isinstance(raw, dict) else None
    if not boundaries:
        return None
    bid = str(boundaries[0].get("id") or "").strip()
    return bid or None


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


def collect_yaml_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    return sorted([p for p in path.rglob("*") if p.suffix in {".yml", ".yaml"}])


def collect_markdown_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    return sorted([p for p in path.rglob("*.md")])


def placeholders(text: str) -> set[str]:
    return set(re.findall(r"\{([^{}]+)\}", text or ""))


def main_guard(fn):
    try:
        raise SystemExit(fn())
    except SystemExit:
        raise
    except Exception as exc:
        print(json.dumps({"ok": False, "summary": str(exc), "violations": [violation("SCRIPT_ERROR", "<script>", str(exc))]}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
