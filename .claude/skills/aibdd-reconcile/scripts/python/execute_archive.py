#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import execute_archive, normalize_plan_package, relative_to_workspace


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: execute_archive.py <arguments.yml> <plan_package_path> <session_id>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    target_plan_package = normalize_plan_package(args_path, sys.argv[2])
    session_id = sys.argv[3].strip()
    archive_path, moved_entries = execute_archive(target_plan_package, session_id)
    payload = {
        "ok": True,
        "target_plan_package": relative_to_workspace(args_path, target_plan_package),
        "archived_to": relative_to_workspace(args_path, archive_path),
        "moved_entries": [relative_to_workspace(args_path, Path(item)) for item in moved_entries],
        "entry_count": len(moved_entries),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
