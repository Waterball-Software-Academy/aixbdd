"""expand_isa 展開 lint 的 fixture 級紅綠測試 steps。"""

from __future__ import annotations

import subprocess
import sys


@given('fixture "{name}"')
def step_given_fixture(context, name):
    d = context.fixtures_dir / name
    assert d.is_dir(), f"fixture 不存在：{d}"
    context.fixture = d


@when("執行 expand_isa")
def step_when_run(context):
    cli = context.scripts_dir / "cli" / "expand_isa.py"
    context.result = subprocess.run(
        [
            sys.executable,
            str(cli),
            "--feature",
            str(context.fixture / "sample.feature"),
            "--dsl",
            str(context.fixture / "sample.dsl.yml"),
            "--isa",
            str(context.fixtures_dir / "isa.yml"),
        ],
        capture_output=True,
        text=True,
    )


@then("退出碼為 {code:d}")
def step_then_exit(context, code):
    r = context.result
    assert r.returncode == code, f"退出碼 {r.returncode} != {code}\nstderr:\n{r.stderr}"


def _findings(stderr: str):
    out = []
    for line in stderr.splitlines():
        s = line.strip()
        if s.startswith("✗ [") or s.startswith("⚠ ["):
            sev = "fail" if s.startswith("✗") else "warn"
            code = s.split("[", 1)[1].split("]", 1)[0]
            out.append((sev, code, s))
    return out


@then("lint 回報:")
def step_then_findings(context):
    got = _findings(context.result.stderr)
    for row in context.table:
        want = (row["severity"], row["code"])
        hits = [f for f in got if (f[0], f[1]) == want]
        assert hits, f"沒有 {want} 的 finding；實際：{[(f[0], f[1]) for f in got]}"
        if "訊息含" in row.headings:
            needle = row["訊息含"]
            assert any(needle in f[2] for f in hits), f"{want} 的訊息不含「{needle}」：{hits}"


@then("lint 沒有任何回報")
def step_then_no_findings(context):
    got = _findings(context.result.stderr)
    assert not got, f"預期無 finding，實際：{got}"


@then("lint 只回報 {n:d} 筆")
def step_then_count(context, n):
    got = _findings(context.result.stderr)
    assert len(got) == n, f"預期 {n} 筆 finding，實際 {len(got)} 筆：{got}"
