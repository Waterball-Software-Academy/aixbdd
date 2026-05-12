#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from _common import load_json, render_record


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_reconcile_record.py <session_json_path> <output_md_path>", file=sys.stderr)
        return 2

    session_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()
    session = load_json(session_path)
    if not isinstance(session, dict):
        print(f"session json not found or malformed: {session_path}", file=sys.stderr)
        return 1
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_record(session), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
