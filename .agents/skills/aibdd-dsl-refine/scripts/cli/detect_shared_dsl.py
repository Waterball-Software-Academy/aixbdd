"""dsl-refine：FP 級去重偵測（read-only）。

掃一個 FP 內各 {feature}.dsl.yml，找出「同一條 dsl_step（format 相同）出現在 ≥2 個
feature」、且尚未上移到 {FP}/dsl.yml 的重複定義 —— 這些應 hoist 到 {FP}/dsl.yml 共用。

本腳本只「偵測並回報」，不改任何檔；實際 hoist／刪重複由 SOP 主流程的 AI 編輯
（保留 `# done` 註解）並經 /clarify-loop 同意後執行。

用法：
    python3 detect_shared_dsl.py --packages-dir <specs/packages> [--fp <slug>]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_CLI_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _CLI_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.scan import all_step_formats  # noqa: E402


def _fp_formats(pkg: Path) -> "set[str]":
    fp_dsl = pkg / "dsl.yml"
    if not fp_dsl.exists():
        return set()
    return {fmt for _, fmt in all_step_formats(fp_dsl.read_text(encoding="utf-8"))}


def detect(pkg: Path) -> list:
    """回傳 [{format, dsl_step, features:[...]}, ...]：format 跨 ≥2 feature 重複、且不在 {FP}/dsl.yml。"""
    already_fp = _fp_formats(pkg)
    by_format: "dict[str, dict]" = {}
    for fd in sorted(pkg.glob("features/*.dsl.yml")):
        for name, fmt in all_step_formats(fd.read_text(encoding="utf-8")):
            if fmt in already_fp:
                continue
            slot = by_format.setdefault(fmt, {"format": fmt, "dsl_step": name, "features": []})
            if fd.name not in slot["features"]:
                slot["features"].append(fd.name)
    return [s for s in by_format.values() if len(s["features"]) >= 2]


def main() -> int:
    ap = argparse.ArgumentParser(description="FP 級 dsl_step 去重偵測（read-only）")
    ap.add_argument("--packages-dir", required=True, help="specs/packages 目錄")
    ap.add_argument("--fp", help="只檢查此 FP slug（省略＝全部）")
    args = ap.parse_args()

    packages_dir = Path(args.packages_dir).resolve()
    if not packages_dir.is_dir():
        print(f"Error: packages 目錄不存在：{packages_dir}", file=sys.stderr)
        return 1

    pkgs = [p for p in sorted(packages_dir.glob("*")) if (p / "features").is_dir()]
    if args.fp:
        pkgs = [p for p in pkgs if p.name == args.fp]

    found = False
    for pkg in pkgs:
        dups = detect(pkg)
        if not dups:
            continue
        found = True
        print(f"FP {pkg.name}：可上移 {len(dups)} 條共用 dsl_step → {pkg.name}/dsl.yml")
        for d in dups:
            print(f"  - {d['dsl_step']}  format={d['format']}")
            print(f"      重複於：{', '.join(d['features'])}")
    if not found:
        print("無跨 feature 重複的 dsl_step（FP 級已收斂）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
