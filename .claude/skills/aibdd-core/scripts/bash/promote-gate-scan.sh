#!/usr/bin/env bash
# Called from speckit-aibdd-bdd-analyze Step 5 DSL Promotion Gate.
# Scans boundary dsl.md entries across spec packages and prints candidates ≥ threshold.
# Usage: promote-gate-scan.sh --specs-root <specs/> [--threshold N]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/promote-dsl.sh" scan "$@"
