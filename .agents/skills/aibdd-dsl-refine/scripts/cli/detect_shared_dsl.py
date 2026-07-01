"""dsl-refine：FP 級去重 / name 唯一性偵測（read-only，決定性 gate）。

掃一個 FP 內各 {feature}.dsl.yml，找出尚未上移到 {FP}/dsl.yml、卻跨 ≥2 個 feature 重複的 dsl_step：

- **name 重複（阻斷級）**：同一 `name` 出現在 ≥2 個 sibling feature。dsl.yml 規則：`name` 在其解析範圍
  （祖先鏈）內必須唯一，否則展開時 `DSL_DEFINITION_DUPLICATE_NAME`、阻斷整個 FP、連 dry-run
  都掃不到。**必須**上移到 {FP}/dsl.yml 共用。
- **format 重複（收斂級）**：同一 `format` 跨 feature 重複 → 應上移以收斂、避免 `DSL_STEP_AMBIGUOUS_MATCH`。

本腳本只偵測並回報、不改檔；實際 hoist／刪重複由 SOP 主流程的 AI 編輯（保留 `# done`）執行。

**exit code（決定性 gate）**：發現任何重複 → exit 3；FP 級已收斂 → exit 0。
主 SOP 須重跑到 exit 0 才得宣告完成（不可只憑自我回報）。

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


def _fp_pairs(pkg: Path) -> "tuple[set, set]":
    """回傳 {FP}/dsl.yml 已有的 (name 集合, format 集合)。"""
    fp_dsl = pkg / "dsl.yml"
    if not fp_dsl.exists():
        return set(), set()
    pairs = all_step_formats(fp_dsl.read_text(encoding="utf-8"))
    return {n for n, _ in pairs}, {f for _, f in pairs}


def detect(pkg: Path) -> "tuple[list, list]":
    """回傳 (name_dups, format_dups)。各為 [{...,'features':[...]}, ...]，跨 ≥2 feature 且不在 {FP}/dsl.yml。"""
    fp_names, fp_formats = _fp_pairs(pkg)
    by_name: "dict[str, dict]" = {}
    by_format: "dict[str, dict]" = {}
    for fd in sorted(pkg.glob("features/*.dsl.yml")):
        for name, fmt in all_step_formats(fd.read_text(encoding="utf-8")):
            if name not in fp_names:  # name 維度（dsl.yml 規則：祖先鏈內唯一）
                slot = by_name.setdefault(name, {"name": name, "features": [], "formats": []})
                if fd.name not in slot["features"]:
                    slot["features"].append(fd.name)
                if fmt not in slot["formats"]:
                    slot["formats"].append(fmt)
            if fmt not in fp_formats:  # format 維度（收斂）
                fslot = by_format.setdefault(fmt, {"format": fmt, "dsl_step": name, "features": []})
                if fd.name not in fslot["features"]:
                    fslot["features"].append(fd.name)
    name_dups = [s for s in by_name.values() if len(s["features"]) >= 2]
    # format_dups 只列「name 維度沒抓到」的（同 format 但 name 不同 → ambiguous），避免與上面重複刷屏
    dup_names = {s["name"] for s in name_dups}
    format_dups = [
        s for s in by_format.values()
        if len(s["features"]) >= 2 and s["dsl_step"] not in dup_names
    ]
    return name_dups, format_dups


def main() -> int:
    ap = argparse.ArgumentParser(description="FP 級去重 / name 唯一性偵測（read-only gate）")
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
        name_dups, format_dups = detect(pkg)
        if not name_dups and not format_dups:
            continue
        found = True
        if name_dups:
            print(f"🔴 FP {pkg.name}：{len(name_dups)} 條 name 跨 feature 重複（阻斷級，**必須**上移 → {pkg.name}/dsl.yml）")
            for d in name_dups:
                amb = "  ⚠ 同名不同 format（請先對齊）" if len(d["formats"]) > 1 else ""
                print(f"  - {d['name']}{amb}")
                print(f"      重複於：{', '.join(d['features'])}")
        if format_dups:
            print(f"FP {pkg.name}：另有 {len(format_dups)} 條 format 跨 feature 重複（建議上移收斂）")
            for d in format_dups:
                print(f"  - {d['dsl_step']}  format={d['format']}")
                print(f"      重複於：{', '.join(d['features'])}")
    if not found:
        print("無跨 feature 重複的 dsl_step（FP 級已收斂；name 唯一）。")
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
