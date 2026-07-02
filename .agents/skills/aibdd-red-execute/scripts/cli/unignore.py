"""拿掉指定 feature 檔上的 `@ignore`（RED 範疇控制）。

歸檔後的 feature 預設帶 `@ignore`（cucumber 會濾掉、不跑）。red-execute 在生成 StepDefinition 後、
跑 cucumber 前，由使用者挑選「這輪要轉紅、下一階段 green 優先實作」的 feature，對選中者跑本腳本拿掉
`@ignore`（未選中者維持 @ignore、不進本輪 RED）。移除該檔開頭的 `@ignore` tag 與其上方 `# @ignore …`
說明註解行；其餘 tag（如 `@dsl`）保留。

用法：
    python3 unignore.py --features <feature1> <feature2> ...
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_IGNORE_TAG = re.compile(r"^\s*@ignore\s*$")
_IGNORE_COMMENT = re.compile(r"^\s*#\s*@ignore\b")


def unignore(path: Path) -> str:
    if not path.is_file():
        return "檔案不存在"
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [ln for ln in lines if not _IGNORE_TAG.match(ln) and not _IGNORE_COMMENT.match(ln)]
    removed = len(lines) - len(kept)
    if removed == 0:
        return "無 @ignore（略過）"
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return f"移除 {removed} 行 @ignore"


def main() -> int:
    ap = argparse.ArgumentParser(description="拿掉 feature 檔的 @ignore（RED 範疇）")
    ap.add_argument("--features", nargs="+", required=True, help="要 un-ignore 的 feature 檔路徑（可多個）")
    args = ap.parse_args()

    any_err = False
    for f in args.features:
        p = Path(f)
        r = unignore(p)
        if r == "檔案不存在":
            any_err = True
        print(f"  {p}：{r}")
    print("完成。未列出的 feature 維持 @ignore、不進本輪 RED。")
    return 1 if any_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
