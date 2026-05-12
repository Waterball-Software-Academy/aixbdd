#!/usr/bin/env bash
# PF-15 Archive Gate — thin wrapper around check_archive_manifest.py.
# Called by preset/commands/speckit.implement.md before declaring Phase 7 complete.
#
# Usage: check-archive-manifest.sh <feature-dir>
#   exit 0 → manifest complete
#   exit 1 → unarchived files remain
#   exit 2 → manifest missing / malformed / wrong usage
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../../.." && pwd)"
PY_SCRIPT="${REPO_ROOT}/.claude/skills/speckit-aibdd-test-plan/scripts/check_archive_manifest.py"
if [ ! -f "$PY_SCRIPT" ]; then
  echo "ERROR: check_archive_manifest.py not found at $PY_SCRIPT" >&2
  exit 2
fi
exec python3 "$PY_SCRIPT" "$@"
