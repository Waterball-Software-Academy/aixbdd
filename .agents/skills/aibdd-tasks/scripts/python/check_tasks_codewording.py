#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from _common import add_tasks_cli_arguments, emit, load_tasks_context, violation


CLASS_PHRASE_RE = re.compile(r"在\s+`(?P<class_name>[A-Za-z_][A-Za-z0-9_]*)`(?P<verb>補齊|實作|補上)")
METHOD_PHRASE_RE = re.compile(
    r"在\s+`(?P<class_name>[A-Za-z_][A-Za-z0-9_]*)`\s*(?P<verb>實作|補齊|補上)\s+`(?P<method_name>[A-Za-z_][A-Za-z0-9_]*)`"
)


def load_symbol_index(script_dir: Path, args_path: Path, plan_package: str | None) -> dict[str, object]:
    cmd = [sys.executable, str(script_dir / "build_code_symbol_index.py"), str(args_path)]
    if plan_package:
        cmd.extend(["--plan-package", plan_package])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stdout or proc.stderr or "build_code_symbol_index.py failed")
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check tasks.md code wording against symbol index")
    add_tasks_cli_arguments(parser)
    parser.add_argument("--tasks-md-basename", default="tasks.md")
    args = parser.parse_args()

    try:
        ctx = load_tasks_context(args)
    except SystemExit as exc:
        return emit(False, "tasks code wording check", [violation("TASKS_CONTEXT_INVALID", str(args.arguments_yml), str(exc))])

    tasks_md = Path(ctx["tasks_md"]).parent / args.tasks_md_basename
    if not tasks_md.exists():
        return emit(
            False,
            "tasks code wording check",
            [violation("TASKS_MD_MISSING", str(tasks_md), f"{args.tasks_md_basename} not found")],
        )

    script_dir = Path(__file__).resolve().parent
    symbol_index = load_symbol_index(script_dir, args.arguments_yml.resolve(), args.plan_package)
    files = symbol_index.get("files", {})
    class_methods: dict[str, set[str]] = {}
    existing_classes: set[str] = set()
    for record in files.values():
        classes = record.get("classes", {}) if isinstance(record, dict) else {}
        for cls, methods in classes.items():
            existing_classes.add(cls)
            class_methods[cls] = set(methods)

    violations: list[dict[str, object]] = []
    for lineno, raw in enumerate(tasks_md.read_text(encoding="utf-8").splitlines(), start=1):
        class_match = CLASS_PHRASE_RE.search(raw)
        if class_match:
            cls = class_match.group("class_name")
            if cls not in existing_classes:
                violations.append(
                    violation(
                        "WORDING_ASSUMES_EXISTING_CLASS",
                        str(tasks_md),
                        f"line implies existing class `{cls}` with `{class_match.group('verb')}`, but class is absent from current code index",
                        lineno,
                    )
                )

        method_match = METHOD_PHRASE_RE.search(raw)
        if method_match:
            cls = method_match.group("class_name")
            method = method_match.group("method_name")
            if cls in class_methods and method in class_methods[cls] and "檢查既有" not in raw and "必要時" not in raw:
                violations.append(
                    violation(
                        "WORDING_REINTRODUCES_EXISTING_METHOD",
                        str(tasks_md),
                        f"line describes `{cls}.{method}` as missing work even though the method already exists",
                        lineno,
                    )
                )

    return emit(not violations, "tasks code wording check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
