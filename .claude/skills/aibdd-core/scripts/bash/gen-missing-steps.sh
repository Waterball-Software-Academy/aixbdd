#!/usr/bin/env bash
# PF-18 step-def gap scanner — thin wrapper around gen_missing_steps.py.
# Usage: gen-missing-steps.sh <features-dir> <step-defs-file-or-dir> [--out <path>]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../../.." && pwd)"
PY_SCRIPT="${REPO_ROOT}/.claude/skills/speckit-aibdd-bdd-analyze/scripts/gen_missing_steps.py"
if [ ! -f "$PY_SCRIPT" ]; then
  echo "ERROR: gen_missing_steps.py not found at $PY_SCRIPT" >&2
  exit 2
fi
exec python3 "$PY_SCRIPT" "$@"
