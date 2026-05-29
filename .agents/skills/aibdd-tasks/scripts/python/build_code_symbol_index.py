#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

from _common import add_tasks_cli_arguments, resolve_boundary_map, resolve_truth_boundary_root, workspace_root_from_args_path


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
    parser = argparse.ArgumentParser(description="Build code symbol index from boundary-map.yml")
    add_tasks_cli_arguments(parser)
    args = parser.parse_args()

    args_path = args.arguments_yml.resolve()
    workspace_root = workspace_root_from_args_path(args_path)
    boundary_map_path = resolve_boundary_map(args_path=args_path)
    if not boundary_map_path.exists():
        print(
            json.dumps(
                {"ok": False, "reason": f"boundary-map not found: {boundary_map_path}"},
                ensure_ascii=False,
                indent=2,
            )
        )
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
        "truth_boundary_root": str(resolve_truth_boundary_root(args_path=args_path)),
        "files": files,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
