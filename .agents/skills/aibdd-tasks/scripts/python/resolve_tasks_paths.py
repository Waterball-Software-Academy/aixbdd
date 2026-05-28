#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import add_tasks_cli_arguments, resolve_tasks_paths_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve /aibdd-tasks path bundle")
    add_tasks_cli_arguments(parser)
    args = parser.parse_args()

    try:
        payload = resolve_tasks_paths_bundle(
            args_path=args.arguments_yml.resolve(),
            plan_package=args.plan_package,
        )
    except SystemExit as exc:
        print(
            json.dumps({"ok": False, "reason": str(exc)}, ensure_ascii=False, indent=2),
            file=sys.stdout,
        )
        return 1

    payload["ok"] = True
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
