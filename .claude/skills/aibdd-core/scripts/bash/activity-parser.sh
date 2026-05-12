#!/usr/bin/env bash
# Thin wrapper around .claude/skills/aibdd-core/lib/activity-parser/ Python package.
# Usage:
#   activity-parser.sh parse    <activity-file>
#   activity-parser.sh paths    --specs-root <feature-dir>
#   activity-parser.sh skeleton --specs-root <feature-dir> --out <test-plan-dir>
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="${SCRIPT_DIR}/../../lib/activity-parser"

# Prefer uv-managed venv if available (zero-dep install: auto-resolves click/pyyaml).
if command -v uv >/dev/null 2>&1; then
  exec uv run --project "${PKG_DIR}" --quiet python -m activity_parser.cli "$@"
fi

# Fallback: system python3 + PYTHONPATH (user must have click + pyyaml installed).
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: need python3 or uv on PATH" >&2
  exit 1
fi
PYEXE="$(command -v python3)"
if ! "$PYEXE" -c "import click, yaml" 2>/dev/null; then
  echo "ERROR: missing Python deps (click, pyyaml). Install either:" >&2
  echo "  (a) curl -LsSf https://astral.sh/uv/install.sh | sh  # preferred" >&2
  echo "  (b) python3 -m pip install --user click pyyaml  # fallback" >&2
  exit 1
fi
PYTHONPATH="${PKG_DIR}/src" exec "$PYEXE" -m activity_parser.cli "$@"
