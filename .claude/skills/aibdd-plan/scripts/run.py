# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "rapidfuzz"]
# ///
"""DSL registry harness CLI (boundary truth dsl.yml scan / search / verify).

TRUTH_BOUNDARY_ROOT is either ``--root <PATH>`` or ``--boundary <NAME>`` with
optional ``--specs-root`` (default: ./specs relative to cwd).

Usage (from repo root, default specs/backend):
    uv run scripts/dsl-cli/run.py list --boundary backend
    uv run scripts/dsl-cli/run.py search <query> --boundary backend
    uv run scripts/dsl-cli/run.py search <query> --fuzzy --boundary backend
    uv run scripts/dsl-cli/run.py search <operationId> --contracts-root specs/backend/contracts --boundary backend
    uv run scripts/dsl-cli/run.py verify [--strict] --boundary backend

Alternate explicit root:
    uv run scripts/dsl-cli/run.py verify --root path/to/TRUTH_BOUNDARY_ROOT
"""

from dsl_cli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
