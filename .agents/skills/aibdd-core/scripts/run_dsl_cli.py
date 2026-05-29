#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ruamel.yaml>=0.18,<0.19",
#   "prance>=25.4.8,<26",
#   "openapi-spec-validator>=0.7.1",
# ]
# ///
"""Compat shim — delegates to ``cli/dsl_cli.py``."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_LIB_DIR = _SCRIPTS_DIR / "lib"
for path in (_LIB_DIR, _SCRIPTS_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

_ENTRY = _SCRIPTS_DIR / "cli" / "dsl_cli.py"
_spec = importlib.util.spec_from_file_location("aibdd_dsl_cli_entry", _ENTRY)
if _spec is None or _spec.loader is None:
    raise SystemExit(f"failed to load dsl cli entry: {_ENTRY}")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

if __name__ == "__main__":
    raise SystemExit(_mod.main(sys.argv[1:]))
