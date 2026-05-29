"""behave hooks for activity-decode BDD suite.

Adds scripts/ (sibling of tests/) to sys.path so steps can `import decoder`.
decoder.py is the production validator (also invoked by SKILL.md Phase 4) — it
lives in scripts/, not in tests/.
"""

from __future__ import annotations
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _TESTS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def before_scenario(context, scenario):
    context.activity_text = None
    context.parse_result = None
    context.parse_exception = None
