"""behave hooks for expand_isa lint suite。

把 scripts/（tests/ 的 sibling）加進 sys.path，讓 steps 可以直接跑 cli/expand_isa.py；
lint 是 SOP 步驟 d 的機械 gate，住在 scripts/ 而非 tests/。
"""

from __future__ import annotations

from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent


def before_scenario(context, scenario):
    context.tests_dir = _TESTS_DIR
    context.scripts_dir = _TESTS_DIR.parent
    context.fixtures_dir = _TESTS_DIR / "fixtures"
    context.fixture = None
    context.result = None
