"""lint_examples 的 fixture 級紅綠測試 steps。"""

from __future__ import annotations

import subprocess
import sys


@given('feature fixture "{name}"')
def step_given_fixture(context, name):
    p = context.fixtures_dir / f"{name}.feature"
    assert p.is_file(), f"fixture 不存在：{p}"
    context.fixture = p


@when("執行 lint_examples")
def step_when_run(context):
    cli = context.scripts_dir / "cli" / "lint_examples.py"
    context.result = subprocess.run(
        [sys.executable, str(cli), str(context.fixture)], capture_output=True, text=True
    )


@then("退出碼為 {code:d}")
def step_then_exit(context, code):
    r = context.result
    assert r.returncode == code, f"退出碼 {r.returncode} != {code}\n{r.stdout}\n{r.stderr}"


def _findings(stdout: str):
    out = []
    for line in stdout.splitlines():
        s = line.strip()
        if s.startswith("✗ [") or s.startswith("⚠ ["):
            sev = "fail" if s.startswith("✗") else "warn"
            code = s.split("[", 1)[1].split("]", 1)[0]
            out.append((sev, code, s))
    return out


@then("lint 回報:")
def step_then_findings(context):
    got = _findings(context.result.stdout)
    for row in context.table:
        want = (row["severity"], row["code"])
        hits = [f for f in got if (f[0], f[1]) == want]
        assert hits, f"沒有 {want}；實際：{[(f[0], f[1]) for f in got]}"
        if "訊息含" in row.headings:
            needle = row["訊息含"]
            assert any(needle in f[2] for f in hits), f"{want} 的訊息不含「{needle}」：{hits}"


@then("lint 沒有任何回報")
def step_then_none(context):
    got = _findings(context.result.stdout)
    assert not got, f"預期無 finding，實際：{got}"
