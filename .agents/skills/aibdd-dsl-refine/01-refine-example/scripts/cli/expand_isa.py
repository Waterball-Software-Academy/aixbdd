"""dsl-refine：把一個 dsl example 依 dsl_steps 展開成 isa example（read-only）。

輸入：dsl example（feature + example）＋ dsl_steps（dsl.yml）；輸出：展開後的 .isa.feature 樣式。
keyword 依 isa.yml 的 instruction_type 推（可選；預設 <packages-dir>/../isa.yml）。

用法：
    python3 expand_isa.py --feature <f.feature> --example "<標題子字串>" --dsl <f.dsl.yml> [--isa <isa.yml>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

_CLI_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _CLI_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.expand import STEP_RE, expand_example  # noqa: E402

_EXAMPLE_RE = re.compile(r"^\s*(?:Example|Scenario)(?:\s+Outline)?:\s*(.*?)\s*$")


def iter_examples_kw(feature_text: str):
    """yield (title, [(keyword, text), ...])。"""
    title = None
    steps = []
    started = False
    for line in feature_text.splitlines():
        ex = _EXAMPLE_RE.match(line)
        if ex:
            if started:
                yield title, steps
            title = ex.group(1) or "(無標題)"
            steps = []
            started = True
            continue
        m = STEP_RE.match(line)
        if m and started:
            steps.append((m.group(1), m.group(2)))
    if started:
        yield title, steps


def load_instructions(isa_path: Path):
    out = []
    if not isa_path.exists():
        return out
    doc = yaml.safe_load(isa_path.read_text(encoding="utf-8")) or {}
    for ins in doc.get("instructions", []) or []:
        fmt = ins.get("format")
        if not fmt:
            continue
        try:
            rx = re.compile(fmt)
        except re.error:
            continue
        out.append((rx, ins.get("instruction_type"), ins.get("data_format")))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="dsl example → isa example 展開")
    ap.add_argument("--feature", required=True, help="含該 example 的 .feature")
    ap.add_argument("--example", help="只展開標題含此子字串的 example（省略＝全部）")
    ap.add_argument("--dsl", required=True, help="dsl_steps 來源（{feature}.dsl.yml）")
    ap.add_argument("--isa", help="isa.yml（推 keyword 用；預設 <feature>/../../../isa.yml 找不到就略過）")
    args = ap.parse_args()

    feature_path = Path(args.feature)
    dsl_path = Path(args.dsl)
    if not feature_path.is_file():
        print(f"feature 不存在：{feature_path}", file=sys.stderr)
        return 1
    if not dsl_path.is_file():
        print(f"dsl.yml 不存在：{dsl_path}", file=sys.stderr)
        return 1

    dsl_doc = yaml.safe_load(dsl_path.read_text(encoding="utf-8")) or {}
    dsl_steps = dsl_doc.get("dsl_steps") or []

    instructions = []
    if args.isa:
        instructions = load_instructions(Path(args.isa))

    out = [f"# 展開 isa example — {feature_path.stem}"]
    for title, gwts in iter_examples_kw(feature_path.read_text(encoding="utf-8")):
        if args.example and args.example not in title:
            continue
        out.append(f"\n## Example: {title}")
        out.extend(expand_example(gwts, dsl_steps, instructions))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
