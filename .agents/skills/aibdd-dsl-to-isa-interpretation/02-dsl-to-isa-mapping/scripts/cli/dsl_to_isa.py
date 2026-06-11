#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ruamel.yaml>=0.18,<0.19",
#   "prance>=25.4.8,<26",
#   "openapi-spec-validator>=0.7.1",
# ]
# ///
"""Entry point for the dsl_to_isa translator (skill-resident).

Preferred invocation:

    uv run .claude/skills/aibdd-dsl-to-isa-interpretation/02-dsl-to-isa-mapping/scripts/cli/dsl_to_isa.py

Environment variables:
    CONTRACTS_DIR               Path to contracts/ dir (isa.yml prerequisite lives here)
    DATA_DIR                    Path to data/ dir (entity_to_table_mapping.yml lives here)
    BOUNDARY_SHARED_DSL         (optional) Path to a single dsl.yml to translate
    TRUTH_BOUNDARY_PACKAGES_DIR (optional) Path to packages root; all */dsl.yml are translated

The translator requires contracts/isa.yml (the ISA instruction set it renders
against) and loads data/entity_to_table_mapping.yml when a state-* handler is
used. Both are project-authored artifacts; the translator STOPs with a pointer
when a required one is absent. The shared Spec Parser + YAML infra are reused
from aibdd-core (wired by the dsl_to_isa package on import).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_LIB_DIR = _SCRIPTS_DIR / "lib"
for _p in (_LIB_DIR, _SCRIPTS_DIR):
    _ps = str(_p)
    if _ps not in sys.path:
        sys.path.insert(0, _ps)

from dsl_to_isa.orchestrator import run_translate  # noqa: E402


def main() -> int:
    contracts_dir = os.environ.get("CONTRACTS_DIR", "contracts")
    data_dir = os.environ.get("DATA_DIR", "data")
    boundary_shared_dsl = os.environ.get("BOUNDARY_SHARED_DSL")
    truth_packages_dir = os.environ.get("TRUTH_BOUNDARY_PACKAGES_DIR")

    return run_translate(
        contracts_dir=contracts_dir,
        data_dir=data_dir,
        boundary_shared_dsl=boundary_shared_dsl,
        truth_packages_dir=truth_packages_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
