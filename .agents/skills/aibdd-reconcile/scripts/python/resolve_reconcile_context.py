#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import derive_paths, normalize_plan_package, read_args, relative_to_workspace, specs_root, workspace_root


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: resolve_reconcile_context.py <arguments.yml> <plan_package_path>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    target_plan_package = normalize_plan_package(args_path, sys.argv[2])
    args = read_args(args_path)
    paths = derive_paths(target_plan_package)
    payload = {
        "ok": True,
        "arguments_path": str(args_path),
        "workspace_root": str(workspace_root(args_path)),
        "specs_root": str(specs_root(args_path, args)),
        "target_plan_package": str(target_plan_package),
        "target_plan_package_rel": relative_to_workspace(args_path, target_plan_package),
        "archive_dir": str(paths["archive_dir"]),
        "active_session_path": str(paths["active_session_path"]),
        "record_path": str(paths["record_path"]),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
