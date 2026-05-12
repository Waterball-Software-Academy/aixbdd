#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from _common import read_args, resolve_arg_path


def parse_python_symbols(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    classes: dict[str, list[str]] = {}
    functions: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes[node.name] = methods
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
    return {
        "classes": classes,
        "functions": functions,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: build_code_symbol_index.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    boundary_map = resolve_arg_path(args_path, args, "TRUTH_BOUNDARY_ROOT")
    if boundary_map is None:
        print(json.dumps({"ok": False, "reason": "missing TRUTH_BOUNDARY_ROOT"}, ensure_ascii=False, indent=2))
        return 1

    boundary_map_path = boundary_map / "boundary-map.yml"
    workspace_root = args_path.parent.parent if args_path.parent.name == ".aibdd" else args_path.parent
    if not boundary_map_path.exists():
        print(json.dumps({"ok": False, "reason": f"boundary-map not found: {boundary_map_path}"}, ensure_ascii=False, indent=2))
        return 1

    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"PyYAML is required to parse {boundary_map_path}: {exc}")

    raw = yaml.safe_load(boundary_map_path.read_text(encoding="utf-8")) or {}
    modules = (((raw.get("topology") or {}).get("modules")) or []) if isinstance(raw, dict) else []

    files: dict[str, object] = {}
    for item in modules:
        rel = str(item.get("file_or_symbol") or "").strip()
        if not rel or not rel.endswith(".py"):
            continue
        abs_path = (workspace_root / rel).resolve()
        record: dict[str, object] = {
            "exists": abs_path.exists(),
            "repo_relative_path": rel,
            "classes": {},
            "functions": [],
        }
        if abs_path.exists():
            record.update(parse_python_symbols(abs_path))
        files[rel] = record

    payload = {
        "ok": True,
        "summary": "code symbol index",
        "files": files,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
