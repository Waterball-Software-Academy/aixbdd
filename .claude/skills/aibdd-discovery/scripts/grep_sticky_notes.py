#!/usr/bin/env python3
"""Grep CiC sticky-notes from clean Discovery artifacts.

Phase 4.A gate #1：scan target tree for unresolved `CiC(KIND: ...)` markers.
Clean artifacts must have zero residual sticky-notes; any hit is a violation.

Usage:
  python3 grep_sticky_notes.py <SPECS_ROOT_DIR>

Output: JSON `{ok, summary, violations[{rule_id, file, line, msg}]}` to stdout.
Exit code 0 iff `ok=true` (no violations); 1 if violations; 2 on bad args / IO.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# `CiC(KIND: ...)` 任一 KIND in {GAP, ASM, BDY, CON} 即視為 sticky-note
STICKY_RE = re.compile(r"CiC\((GAP|ASM|BDY|CON)\s*:")

# 只掃 clean artifact 副檔名；其他檔（reports/、log）不視為 clean artifact
CLEAN_EXTS = {".feature", ".activity", ".yml", ".yaml", ".md"}

# 但 reports/ 下的 sourcing 檔是中介報告，不算 clean artifact
EXCLUDED_DIRS = {".git", "node_modules", ".tests", "reports"}


def scan(root: Path) -> list[dict]:
    violations: list[dict] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix not in CLEAN_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = STICKY_RE.search(line)
            if not match:
                continue
            kind = match.group(1)
            violations.append(
                {
                    "rule_id": f"CIC_{kind}_RESIDUAL",
                    "file": str(path),
                    "line": lineno,
                    "msg": f"unresolved CiC({kind}: ...) sticky-note",
                }
            )
    return violations


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(json.dumps({"ok": False, "summary": f"not a directory: {root}", "violations": []}))
        return 2

    violations = scan(root)
    ok = len(violations) == 0
    summary = "no sticky-notes" if ok else f"{len(violations)} sticky-note residue(s)"
    report = {"ok": ok, "summary": summary, "violations": violations}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
