"""Step: capture .activity DSL text from feature docstring or benchmark fixture file."""

from __future__ import annotations

from pathlib import Path

from behave import given  # type: ignore[import-not-found]


_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "benchmark-fixtures"


@given("以下 activity 內容:")
def step_capture_activity_text(context):
    assert context.text is not None, "expected docstring (multi-line text) under Given"
    context.activity_text = context.text


@given('fixture 檔案 "{filename}"')
def step_capture_fixture_file(context, filename: str):
    fixture = _FIXTURES_DIR / filename
    assert fixture.is_file(), f"benchmark fixture not found: {fixture}"
    context.activity_text = fixture.read_text(encoding="utf-8")
