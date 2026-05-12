#!/usr/bin/env bash
# Thin wrapper around .claude/skills/clarify-loop/scripts/grep_sticky_notes.py
# Usage: grep-sticky-notes.sh <specs-root>
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../../.." && pwd)"
PY_SCRIPT="${REPO_ROOT}/.claude/skills/clarify-loop/scripts/grep_sticky_notes.py"
if [ ! -f "$PY_SCRIPT" ]; then
  echo "ERROR: grep_sticky_notes.py not found at $PY_SCRIPT" >&2
  exit 1
fi
exec python3 "$PY_SCRIPT" "$@"
