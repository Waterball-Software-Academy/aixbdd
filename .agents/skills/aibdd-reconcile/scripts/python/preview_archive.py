#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import derive_paths, list_entries_to_archive, normalize_plan_package, relative_to_workspace


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: preview_archive.py <arguments.yml> <plan_package_path> <session_id>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    target_plan_package = normalize_plan_package(args_path, sys.argv[2])
    session_id = sys.argv[3].strip()
    paths = derive_paths(target_plan_package)
    archive_path = paths["archive_dir"] / session_id
    entries = [relative_to_workspace(args_path, entry) for entry in list_entries_to_archive(target_plan_package)]
    payload = {
        "ok": True,
        "target_plan_package": relative_to_workspace(args_path, target_plan_package),
        "archived_to": relative_to_workspace(args_path, archive_path),
        "entries_to_move": entries,
        "entry_count": len(entries),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
