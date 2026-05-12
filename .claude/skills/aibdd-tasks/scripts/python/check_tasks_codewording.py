#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from _common import emit, read_args, resolve_arg_path, violation


CLASS_PHRASE_RE = re.compile(r"在\s+`(?P<class_name>[A-Za-z_][A-Za-z0-9_]*)`(?P<verb>補齊|實作|補上)")
METHOD_PHRASE_RE = re.compile(
    r"在\s+`(?P<class_name>[A-Za-z_][A-Za-z0-9_]*)`\s*(?P<verb>實作|補齊|補上)\s+`(?P<method_name>[A-Za-z_][A-Za-z0-9_]*)`"
)


def load_symbol_index(script_dir: Path, args_path: Path) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(script_dir / "build_code_symbol_index.py"), str(args_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stdout or proc.stderr or "build_code_symbol_index.py failed")
    return json.loads(proc.stdout)


def main() -> int:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: check_tasks_codewording.py <arguments.yml> [tasks_md_basename]", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    tasks_basename = Path(sys.argv[2]).name if len(sys.argv) == 3 else "tasks.md"
    args = read_args(args_path)
    plan_md = resolve_arg_path(args_path, args, "PLAN_MD")
    if plan_md is None:
        return emit(False, "tasks code wording check", [violation("MISSING_PLAN_MD", str(args_path), "missing PLAN_MD")])

    tasks_md = plan_md.parent / tasks_basename
    if not tasks_md.exists():
        return emit(False, "tasks code wording check", [violation("TASKS_MD_MISSING", str(tasks_md), f"{tasks_basename} not found")])

    script_dir = Path(__file__).resolve().parent
    symbol_index = load_symbol_index(script_dir, args_path)
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
