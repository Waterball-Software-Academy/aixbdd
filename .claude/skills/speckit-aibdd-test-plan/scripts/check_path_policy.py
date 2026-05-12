"""Check that a TEST_PLAN_OUT_DIR honours the path coverage policy.

MVP: counts Scenarios per file; real node-coverage verification would need
the Activity AST and is deferred to sub-proposal #3 integration.

Usage:
    check_path_policy.py <test-plan-out-dir> [--policy node-once]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def count_scenarios(feature_path: Path) -> int:
    return sum(1 for ln in feature_path.read_text(encoding="utf-8").splitlines()
               if ln.strip().startswith("Scenario:") or ln.strip().startswith("Scenario Outline:"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out_dir", type=Path)
    p.add_argument("--policy", default="node-once", choices=["node-once"])
    ns = p.parse_args()

    if not ns.out_dir.exists():
        print(f"ERROR: {ns.out_dir} does not exist", file=sys.stderr)
        return 2

    missing = []
    for f in sorted(ns.out_dir.glob("*.feature")):
        n = count_scenarios(f)
        if n == 0:
            missing.append(f)
            print(f"FAIL: {f} has no Scenario blocks")
        else:
            print(f"OK  : {f} ({n} Scenario(s))")

    if missing:
        return 1
    print(f"policy={ns.policy}: all feature files have ≥1 Scenario")
    return 0


if __name__ == "__main__":
    sys.exit(main())
