#!/usr/bin/env python3
"""
check_actor_legality.py — Discovery Quality Gate 7a

掃描 resolved `${ACTIVITIES_DIR}` 下 `*.{activity,mmd}`，偵測非法 Actor（內建系統 Actor）。
規則來源：aibdd-discovery/references/rules/actor-legality.md
  - 合法：外部使用者、第三方系統
  - 非法：@系統 / @System / @Backend / @內建系統 / @自有系統 / @Server / @Service

支援自訂 allow-list / block-list（`${SPECS_ROOT_DIR}/.actors.yml`），讓專案可宣告例外，避免硬碼 drift。

預設 activities 目錄由 `${AIBDD_ARGUMENTS_PATH}` + `${BOUNDARY_YML}` 機械展開
（`kickoff_path_resolve.py`）；亦可 `--activities-dir ABS_PATH` 覆寫。

Usage:
  python check_actor_legality.py <AIBDD_ARGUMENTS_PATH> [--activities-dir ABS_PATH]

Output: stdout JSON
  {
    "ok": <bool>,
    "summary": {"files_scanned": int, "actors_seen": int, "violations": int},
    "violations": [
      {"rule_id": "ACTOR_INTERNAL_SYSTEM",
       "file": "...", "line": int, "actor": "@系統",
       "msg": "Actor '@系統' is an internal-system marker; convert to upstream Rule."}
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

from kickoff_path_resolve import load_resolved_kickoff_state, resolve_kickoff_paths

DEFAULT_BLOCKLIST = (
    "系統", "內建系統", "自有系統",
    "System", "Backend", "Server", "Service",
)

ACTIVITY_GLOBS = ("*.activity", "*.mmd")
ACTOR_DECL_RE = re.compile(r"\[ACTOR\]\s+(?P<name>\S+)")
ACTOR_USE_RE = re.compile(r"@(?P<name>[\w\-\u4e00-\u9fff]+)")


def load_blocklist(specs_root: Path) -> tuple[set[str], set[str]]:
    """從 specs/.actors.yml 讀 allow / block override；回傳 (block, allow)。"""
    cfg = specs_root / ".actors.yml"
    block = set(DEFAULT_BLOCKLIST)
    allow: set[str] = set()
    if not cfg.exists():
        return block, allow
    try:
        import yaml  # type: ignore
    except ImportError:
        return block, allow
    try:
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return block, allow
    for x in data.get("block", []) or []:
        block.add(str(x))
    for x in data.get("allow", []) or []:
        allow.add(str(x))
    return block, allow


def scan_file(path: Path, block: set[str], allow: set[str]) -> tuple[set[str], list[dict]]:
    actors_seen: set[str] = set()
    violations: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return actors_seen, violations
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in ACTOR_USE_RE.finditer(line):
            name = m.group("name")
            actors_seen.add(name)
            if name in allow:
                continue
            if name in block:
                violations.append({
                    "rule_id": "ACTOR_INTERNAL_SYSTEM",
                    "file": str(path),
                    "line": lineno,
                    "actor": f"@{name}",
                    "msg": (
                        f"Actor '@{name}' is an internal-system marker; "
                        "convert to a Rule on the upstream external trigger "
                        "(see actor-legality.md)."
                    ),
                })
    return actors_seen, violations


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("arguments_path", help="${AIBDD_ARGUMENTS_PATH}")
    p.add_argument(
        "--activities-dir",
        help="Absolute path to activities directory (default: resolve from arguments.yml + boundary.yml)",
    )
    args = p.parse_args()

    args_path = Path(args.arguments_path)
    try:
        workspace_root, resolved, _ = load_resolved_kickoff_state(args_path)
        root = (workspace_root / str(resolved.get("SPECS_ROOT_DIR", "specs"))).resolve()
    except Exception:
        root = args_path.parent.parent / "specs"

    if args.activities_dir:
        activities = Path(args.activities_dir).resolve()
    else:
        try:
            _, activities, _ = resolve_kickoff_paths(args_path)
        except Exception as e:
            json.dump({
                "ok": False,
                "summary": {"files_scanned": 0, "actors_seen": 0, "violations": 1},
                "violations": [{
                    "rule_id": "KICKOFF_PATH_RESOLVE_FAILED",
                    "file": str(args_path), "line": 0,
                    "msg": str(e),
                }],
            }, sys.stdout, ensure_ascii=False, indent=2)
            print()
            return 1

    if activities is None:
        json.dump({
            "ok": True,
            "summary": {"files_scanned": 0, "actors_seen": 0, "violations": 0},
            "violations": [],
            "note": "ACTIVITIES_DIR not bound (kickoff-safe); skip Activity scan.",
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    if not activities.exists():
        json.dump({
            "ok": True,
            "summary": {"files_scanned": 0, "actors_seen": 0, "violations": 0},
            "violations": [],
            "note": f"activities dir not found: {activities} (greenfield = pass)",
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    block, allow = load_blocklist(root)

    files_scanned = 0
    all_actors: set[str] = set()
    violations: list[dict] = []
    for pat in ACTIVITY_GLOBS:
        for f in activities.rglob(pat):
            files_scanned += 1
            seen, vs = scan_file(f, block, allow)
            all_actors |= seen
            violations.extend(vs)

    result = {
        "ok": len(violations) == 0,
        "summary": {
            "files_scanned": files_scanned,
            "actors_seen": len(all_actors),
            "violations": len(violations),
        },
        "violations": violations,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
