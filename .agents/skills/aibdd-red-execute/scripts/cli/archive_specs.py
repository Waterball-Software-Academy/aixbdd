"""feature 歸檔（Model B：已安裝 specformula 框架 / preprocess）—— 從 specs mirror 到 test resources。

【嚴禁手動複製；歸檔一律跑本腳本】。resources 下述 4 個 target 皆為 specs 的**衍生產物**，
每次歸檔「清空再複製」（clean-then-copy，mirror 語意）：**來源刪掉的檔／資料夾，下游一併移除**；
禁止手改這些 target。

4 個 target（來源 → 目標）：
  specs/packages/            → <resources>/dsl-features/          （preprocess sourceDirectory：feature+dsl+package isa）
  specs/isa.yml              → <resources>/isa.yml                （dslResourceRoot root isa ＋ runtime glue）
  specs/data/               → <resources>/specs/data/            （isa config data.project_path）
  specs/contracts/ ＋ api/   → <resources>/specs/api/            （isa config api.project_path；兩來源合併，api 後蓋 contracts 同名）

用法：
  python3 archive_specs.py --specs-dir <specs> --resources-dir <src/test/resources>
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def mirror_dir(src: Path, dst: Path) -> str:
    """clean-then-copy：先刪 dst，再把 src 整個複製過去。src 不存在 → dst 保持刪除。"""
    if dst.exists() or dst.is_symlink():
        shutil.rmtree(dst)
    if src.is_dir():
        shutil.copytree(src, dst)
        n = sum(1 for _ in dst.rglob("*") if _.is_file())
        return f"copied dir ({n} files)"
    return "source missing → removed downstream"


def mirror_file(src: Path, dst: Path) -> str:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return "copied file"
    if dst.exists():
        dst.unlink()
        return "source missing → removed downstream"
    return "source missing (nothing to remove)"


def drop_unrefined_features(dsl_features_root: Path) -> int:
    """A2：還沒完成 dsl-refine 的 feature 不搬 —— 移除 dsl-features 下「無同名 `.dsl.yml`」的 `.feature`。

    （specs 不動；只清衍生的 dsl-features。有 `.dsl.yml` 者保留，內部仍未定義的 dsl step 交給
    preprocess pass-through 忽略。）回傳移除數。
    """
    removed = 0
    for feat in dsl_features_root.rglob("*.feature"):
        if not feat.with_suffix(".dsl.yml").is_file():
            feat.unlink()
            removed += 1
    return removed


def mirror_merge(srcs: "list[Path]", dst: Path, pattern: str) -> str:
    """多來源合併到單一 dst：先清空 dst，再依序把各來源符合 pattern 的檔複製進去（後者蓋同名）。"""
    if dst.exists() or dst.is_symlink():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    n = 0
    for s in srcs:
        if s.is_dir():
            for f in sorted(s.glob(pattern)):
                shutil.copy2(f, dst / f.name)
                n += 1
    return f"merged {n} file(s) from {sum(1 for s in srcs if s.is_dir())} source(s)"


def main() -> int:
    ap = argparse.ArgumentParser(description="feature 歸檔（specs → test resources，mirror）")
    ap.add_argument("--specs-dir", required=True, help="specs root（含 packages/ isa.yml data/ contracts/ api/）")
    ap.add_argument("--resources-dir", required=True, help="src/test/resources")
    args = ap.parse_args()

    specs = Path(args.specs_dir).resolve()
    res = Path(args.resources_dir).resolve()
    if not specs.is_dir():
        print(f"Error: specs 目錄不存在：{specs}", file=sys.stderr)
        return 1
    res.mkdir(parents=True, exist_ok=True)

    dsl_features = res / "dsl-features"
    steps = [
        ("packages → dsl-features", lambda: mirror_dir(specs / "packages", dsl_features)),
        ("isa.yml → isa.yml", lambda: mirror_file(specs / "isa.yml", res / "isa.yml")),
        ("data → specs/data", lambda: mirror_dir(specs / "data", res / "specs" / "data")),
        ("contracts+api → specs/api",
         lambda: mirror_merge([specs / "contracts", specs / "api"], res / "specs" / "api", "*.api.yml")),
    ]
    print(f"歸檔（mirror，clean-then-copy）：{specs} → {res}")
    for label, fn in steps:
        print(f"  {label:28s} {fn()}")
    # A2：還沒完成 dsl-refine（無 .dsl.yml）的 feature 不搬
    dropped = drop_unrefined_features(dsl_features)
    print(f"  {'A2 略過未 refine 的 feature':28s} 移除 {dropped} 個無 .dsl.yml 的 .feature")
    print("完成。resources 為衍生產物，禁手改；下次歸檔重跑本腳本即可。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
