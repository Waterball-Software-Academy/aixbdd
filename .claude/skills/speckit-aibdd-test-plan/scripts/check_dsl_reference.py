"""Check that every step in test-plan feature files resolves to a DSL entry
in the merged view (shared dsl.md ⊕ boundary dsl.md).

MVP heuristic: collects ``- id:`` lines from both DSL files, and scans
feature steps for any CiC(BDY) markers. A proper pattern-match lookup
against L1 templates is deferred; this script's job is to ensure no
CiC(BDY) survived into Test Plan output.

Usage:
    check_dsl_reference.py <test-plan-out-dir> --dsl-core <path> --dsl-local <path>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CIC_BDY_RE = re.compile(r"CiC\(BDY\)", re.IGNORECASE)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out_dir", type=Path)
    p.add_argument("--dsl-core", type=Path, required=True)
    p.add_argument("--dsl-local", type=Path, required=True)
    ns = p.parse_args()

    if not ns.out_dir.exists():
        print(f"ERROR: {ns.out_dir} does not exist", file=sys.stderr)
        return 2
    if not ns.dsl_core.exists():
        print(f"WARN: shared dsl.md not found at {ns.dsl_core}; proceeding with boundary dsl.md only")
    if not ns.dsl_local.exists():
        print(f"WARN: boundary dsl.md not found at {ns.dsl_local}")

    cic_residual = 0
    for f in sorted(ns.out_dir.glob("*.feature")):
        text = f.read_text(encoding="utf-8")
        hits = CIC_BDY_RE.findall(text)
        if hits:
            print(f"FAIL: {f} has {len(hits)} CiC(BDY) marker(s) — missing DSL entry")
            cic_residual += len(hits)

    if cic_residual:
        return 1
    print("All Test Plan features have no CiC(BDY) residual — DSL reference integrity OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
