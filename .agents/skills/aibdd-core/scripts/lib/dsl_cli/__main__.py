"""Compat entry for ``python -m dsl_cli`` when ``scripts/lib`` is on ``PYTHONPATH``."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
_TARGET = _SCRIPTS_DIR / "cli" / "dsl_cli.py"
sys.argv[0] = str(_TARGET)
runpy.run_path(str(_TARGET), run_name="__main__")
