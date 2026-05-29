#!/usr/bin/env python3
"""
grep_sticky_notes.py — 跨 Planner 共用便條紙掃描器

從 specs_root 完整遞迴掃描所有 `CiC(KIND): ...` 標記。
Plugin 採 flat project-wide layout（PF-13）— artifact 直接位於 spec package 根
（`${SPECS_ROOT_DIR}/<subdir>/`），預設一律從 root 起遞迴。給 Planner Quality
Gate 與 Clarify Loop Mini-plan 的「歸零」檢查使用。

Usage:
  python grep_sticky_notes.py <SPECS_ROOT_DIR>
  python grep_sticky_notes.py <SPECS_ROOT_DIR> --paths activities features
  python grep_sticky_notes.py <SPECS_ROOT_DIR> --kinds ASM GAP BDY CON

Output: stdout JSON
  {
    "ok": <bool>,                 # true 若 violations == 0
    "summary": {
      "files_scanned": int,
      "sticky_notes": int,
      "by_kind": {"ASM": n, "GAP": n, "BDY": n, "CON": n}
    },
    "violations": [
      {"rule_id": "STICKY_NOTE_PRESENT",
       "file": "...", "line": int, "kind": "ASM",
       "msg": "假設優惠碼在確認頁輸入..."}
    ]
  }

Exit: 0 if ok=true, 1 if ok=false.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CIC_RE = re.compile(r"CiC\((?P<kind>[A-Z]+)\)\s*:\s*(?P<msg>.+?)(?:$|\s*#\s*$)")
DEFAULT_PATHS = (".",)  # flat project-wide layout (PF-13): artifact 直接位於 specs_root/<subdir>/ → 預設從 specs_root 完整遞迴
DEFAULT_GLOBS = ("*.activity", "*.mmd", "*.feature", "*.md", "*.dbml", "*.yml")


def scan_file(path: Path) -> list[dict]:
    out = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return out
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in CIC_RE.finditer(line):
            out.append({
                "rule_id": "STICKY_NOTE_PRESENT",
                "file": str(path),
                "line": lineno,
                "kind": m.group("kind"),
                "msg": m.group("msg").strip(),
            })
    return out


def iter_files(root: Path, subpaths: list[str], globs: list[str]):
    for sub in subpaths:
        base = root if sub in (".", "") else root / sub
        if not base.exists():
            continue
        for pat in globs:
            yield from base.rglob(pat)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("specs_root", help="${SPECS_ROOT_DIR}")
    p.add_argument("--paths", nargs="+", default=list(DEFAULT_PATHS),
                   help="subpaths under specs_root to scan")
    p.add_argument("--globs", nargs="+", default=list(DEFAULT_GLOBS),
                   help="filename globs to include")
    p.add_argument("--kinds", nargs="+", default=None,
                   help="filter by sticky-note kinds (ASM GAP BDY CON ...)")
    args = p.parse_args()

    root = Path(args.specs_root)
    if not root.exists():
        json.dump({
            "ok": False,
            "summary": {"files_scanned": 0, "sticky_notes": 0, "by_kind": {}},
            "violations": [{
                "rule_id": "SPECS_ROOT_MISSING",
                "file": str(root), "line": 0, "kind": "",
                "msg": f"specs_root not found: {root}",
            }],
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 1

    files_scanned = 0
    violations: list[dict] = []
    by_kind: dict[str, int] = {}
    kind_filter = set(args.kinds) if args.kinds else None

    for f in iter_files(root, args.paths, args.globs):
        files_scanned += 1
        for v in scan_file(f):
            if kind_filter and v["kind"] not in kind_filter:
                continue
            violations.append(v)
            by_kind[v["kind"]] = by_kind.get(v["kind"], 0) + 1

    result = {
        "ok": len(violations) == 0,
        "summary": {
            "files_scanned": files_scanned,
            "sticky_notes": len(violations),
            "by_kind": by_kind,
        },
        "violations": violations,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
