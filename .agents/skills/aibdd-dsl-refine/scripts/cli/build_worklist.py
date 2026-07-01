"""dsl-refine：掃 packages → 產出 worklist 暫存檔（DSL_REFINE_PLAN.yml）。

read-only 對 specs（只寫 worklist 本身）。每次 skill 啟動先刪舊檔再重建。
「未完成」= example 某行 GWT 比不到任何標 `# done` 的 dsl_step（含「尚未建立」）。

用法：
    python3 build_worklist.py --packages-dir <specs/packages> [--out DSL_REFINE_PLAN.yml]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_CLI_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _CLI_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.scan import (  # noqa: E402
    all_step_formats,
    done_formats,
    format_matcher,
    iter_examples,
    undone_in_example,
)


def _fp_definitions(pkg: Path) -> "list[tuple]":
    """蒐集該 FP 內所有 dsl_step 定義（{FP}/dsl.yml ＋ 每個 {feature}.dsl.yml）。

    回傳 [(matcher, location, dsl_step_name), ...]，供「先找後建」標註既有定義。
    """
    defs: "list[tuple]" = []
    sources = []
    fp_dsl = pkg / "dsl.yml"
    if fp_dsl.exists():
        sources.append(("dsl.yml", fp_dsl))
    for fd in sorted(pkg.glob("features/*.dsl.yml")):
        sources.append((f"features/{fd.name}", fd))
    for location, path in sources:
        for name, fmt in all_step_formats(path.read_text(encoding="utf-8")):
            rx = format_matcher(fmt)
            if rx:
                defs.append((rx, location, name))
    return defs


def _reuse_hint(step_text: str, fp_defs, self_location: str):
    """該未完成步驟若已有定義（在 FP 其它位置）→ 回傳 reuse 提示，否則 None。"""
    for rx, location, name in fp_defs:
        if location == self_location:
            continue  # 同檔已存在不算「待重建」，交由 # done 流程
        if rx.match(step_text):
            return {"step": step_text, "defined_in": location, "dsl_step": name}
    return None


def build(packages_dir: Path) -> dict:
    """掃 packages → worklist 結構（只含有待處理 example 的 FP/feature/example）。"""
    fps = []
    for pkg in sorted(p for p in packages_dir.glob("*") if (p / "features").is_dir()):
        fp = {"slug": pkg.name, "pending_examples": 0, "features": []}
        # FP 層共用 dsl.yml（跨 feature 共用的 dsl_step）；對該 FP 全 feature 生效
        fp_dsl = pkg / "dsl.yml"
        fp_done_matchers = (
            [format_matcher(f) for f in done_formats(fp_dsl.read_text(encoding="utf-8"))]
            if fp_dsl.exists()
            else []
        )
        fp_defs = _fp_definitions(pkg)  # 先找後建：FP 內既有定義索引
        for ff in sorted(pkg.glob("features/*.feature")):
            feat_dsl = ff.with_suffix(".dsl.yml")
            self_location = f"features/{feat_dsl.name}"
            done_matchers = list(fp_done_matchers)
            if feat_dsl.exists():
                done_matchers += [
                    format_matcher(f) for f in done_formats(feat_dsl.read_text(encoding="utf-8"))
                ]
            examples = []
            for title, steps in iter_examples(ff.read_text(encoding="utf-8")):
                undone = undone_in_example(steps, done_matchers)
                if undone:
                    ex = {"title": title, "status": "pending", "undone_steps": undone}
                    reuse = [
                        h for h in (_reuse_hint(s, fp_defs, self_location) for s in undone) if h
                    ]
                    if reuse:
                        ex["reuse"] = reuse  # 已有定義 → c 步引用/hoist，勿重建
                    examples.append(ex)
            if examples:
                fp["pending_examples"] += len(examples)
                fp["features"].append({"name": ff.stem, "examples": examples})
        if fp["features"]:
            fps.append(fp)
    return {"fps": fps}


def main() -> int:
    ap = argparse.ArgumentParser(description="產出 dsl-refine worklist（DSL_REFINE_PLAN.yml）")
    ap.add_argument("--packages-dir", required=True, help="specs/packages 目錄")
    ap.add_argument("--out", default="DSL_REFINE_PLAN.yml", help="worklist 落點（預設專案根）")
    args = ap.parse_args()

    packages_dir = Path(args.packages_dir).resolve()
    if not packages_dir.is_dir():
        print(f"Error: packages 目錄不存在：{packages_dir}", file=sys.stderr)
        return 1

    worklist = build(packages_dir)
    out_path = Path(args.out)
    out_path.write_text(
        yaml.safe_dump(worklist, allow_unicode=True, sort_keys=False, width=10000),
        encoding="utf-8",
    )

    total = sum(f["pending_examples"] for f in worklist["fps"])
    print(f"worklist 寫出：{out_path}（待 refine FP {len(worklist['fps'])}，待處理 example {total}）")
    for f in worklist["fps"]:
        print(f"  {f['slug']}：example {f['pending_examples']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
