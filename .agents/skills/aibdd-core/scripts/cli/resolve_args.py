#!/usr/bin/env python3
"""
resolve_args.py

Shared placeholder resolver for every aibdd-xxx skill.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_LIB_DIR = _SCRIPTS_DIR / "lib"
for path in (_LIB_DIR, _SCRIPTS_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from shared.project_args import resolve_text  # noqa: E402


def main() -> int:
    result = resolve_text(sys.stdin.read(), cwd=Path.cwd())
    if result.stderr:
        sys.stderr.write(result.stderr)
    if not result.ok:
        return result.exit_code
    sys.stdout.write(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
