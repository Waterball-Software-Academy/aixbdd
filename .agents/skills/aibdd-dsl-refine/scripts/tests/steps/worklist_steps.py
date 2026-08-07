"""build_worklist 的 fixture 級紅綠測試 steps。"""

from __future__ import annotations

import subprocess
import sys

import yaml


@given('packages fixture "{name}"')
def step_given_packages(context, name):
    d = context.fixtures_dir / name
    assert d.is_dir(), f"fixture 不存在：{d}"
    context.packages_dir = d


@when("執行 build_worklist")
def step_when_build(context):
    cli = context.scripts_dir / "cli" / "build_worklist.py"
    out = context.tmp_dir / "DSL_REFINE_PLAN.yml"
    context.result = subprocess.run(
        [sys.executable, str(cli), "--packages-dir", str(context.packages_dir), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert context.result.returncode == 0, context.result.stderr
    context.worklist = yaml.safe_load(out.read_text(encoding="utf-8")) or {}


@then("worklist 沒有任何待處理 FP")
def step_then_empty(context):
    fps = context.worklist.get("fps") or []
    assert not fps, f"預期 worklist 為空，實際：{yaml.safe_dump(context.worklist, allow_unicode=True)}"


@then("worklist 的 FP「{slug}」有 {n:d} 個待處理 example")
def step_then_fp_count(context, slug, n):
    fps = {f["slug"]: f for f in (context.worklist.get("fps") or [])}
    assert slug in fps, f"worklist 沒有 FP {slug}；實際：{list(fps)}"
    got = fps[slug]["pending_examples"]
    assert got == n, f"FP {slug} 的 pending_examples={got}，預期 {n}"


@then("worklist 各層的鍵為:")
def step_then_keys(context):
    expected = {row["層級"]: [k.strip() for k in row["鍵"].split("、")] for row in context.table}
    fps = context.worklist.get("fps") or []
    assert fps, "worklist 為空，無法檢查 schema"
    layers = {
        "fps[]": fps[0],
        "features[]": fps[0]["features"][0],
        "examples[]": fps[0]["features"][0]["examples"][0],
    }
    for layer, keys in expected.items():
        got = set(layers[layer])
        missing = [k for k in keys if k not in got]
        assert not missing, f"{layer} 缺鍵 {missing}；實際鍵：{sorted(got)}"
