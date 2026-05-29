"""Compat re-export from ``shared.spec_parsers``."""
import sys
from pathlib import Path
_LIB = Path(__file__).resolve().parents[2]
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))
from shared.spec_parsers.openapi import *  # noqa: F403
