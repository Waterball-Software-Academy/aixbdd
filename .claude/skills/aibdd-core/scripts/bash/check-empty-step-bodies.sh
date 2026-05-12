#!/usr/bin/env bash
# check-empty-step-bodies.sh — PF-EMPTY-BODY gate wrapper (log 260428-03)
#
# Wraps python/check_empty_step_bodies.py. Mirrors the contract style of
# gen-missing-steps.sh / check-archive-manifest.sh.
#
# Usage:
#   check-empty-step-bodies.sh <step_defs_glob> [--threshold N] [--out PATH]
#
# Exit codes mirror the python script (0 = PASS, 1 = FAIL, 2 = usage error).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="${SCRIPT_DIR}/../python/check_empty_step_bodies.py"

if [[ ! -f "${PY_SCRIPT}" ]]; then
  echo "error: python script missing at ${PY_SCRIPT}" >&2
  exit 2
fi

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <step_defs_glob> [--threshold N] [--out PATH]" >&2
  exit 2
fi

exec python3 "${PY_SCRIPT}" "$@"
