#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from _common import derive_cascade_chain


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: derive_cascade_chain.py <earliest_planner>", file=sys.stderr)
        return 2
    earliest = sys.argv[1].strip()
    chain = derive_cascade_chain(earliest)
    payload = {
        "ok": True,
        "earliest": earliest,
        "chain": chain,
        "stdout_csv": ",".join(chain),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
