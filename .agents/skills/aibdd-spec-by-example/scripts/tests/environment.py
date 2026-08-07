"""behave hooks for lint_examples suite。"""

from __future__ import annotations

from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent


def before_scenario(context, scenario):
    context.tests_dir = _TESTS_DIR
    context.scripts_dir = _TESTS_DIR.parent
    context.fixtures_dir = _TESTS_DIR / "fixtures"
    context.fixture = None
    context.result = None
