"""spec-by-example：對草稿／既有 `.feature` 跑機械檢核（read-only）。

用法：
    python3 lint_examples.py <path.feature> [<path.feature> ...]
    python3 lint_examples.py <dir>            # 掃該目錄下所有 *.feature

exit code：0＝無阻斷級違規（可能仍有 ⚠ warning）；3＝有 ✗ 違規；1＝參數錯誤。
"""
from __future__ import annotations

import sys
from pathlib import Path

_CLI_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _CLI_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.example_lint import has_blocking, run_lints  # noqa: E402


def _targets(args) -> "list[Path]":
    out: "list[Path]" = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.feature")))
        elif p.is_file():
            out.append(p)
        else:
            print(f"路徑不存在：{p}", file=sys.stderr)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1
    targets = _targets(sys.argv[1:])
    if not targets:
        print("沒有可檢核的 .feature", file=sys.stderr)
        return 1

    all_findings = []
    for f in targets:
        findings = run_lints(f.read_text(encoding="utf-8"))
        if findings:
            print(f"\n{f}")
            for x in findings:
                print(f"  {x.render()}")
        all_findings += findings

    fails = [x for x in all_findings if x.severity == "fail"]
    warns = [x for x in all_findings if x.severity == "warn"]
    print(f"\n掃描 {len(targets)} 支 feature：✗ {len(fails)} 筆、⚠ {len(warns)} 筆")
    if has_blocking(all_findings):
        print("有阻斷級違規（✗）——回 8.1 重擬對應 Example 後重跑，不得帶著違規進 8.4 稽核。")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
