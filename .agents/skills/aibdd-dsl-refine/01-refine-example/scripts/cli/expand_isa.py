"""dsl-refine：把一個 dsl example 依 dsl_steps 展開成 isa example（read-only）。

輸入：dsl example（feature + example）＋ dsl_steps（dsl.yml）；輸出：展開後的 .isa.feature 樣式。
keyword 依 isa.yml 的 instruction_type 推（可選；預設 <packages-dir>/../isa.yml）。

用法：
    python3 expand_isa.py --feature <f.feature> --example "<標題子字串>" --dsl <f.dsl.yml> [--isa <isa.yml>]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

_CLI_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _CLI_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.expand import STEP_RE, expand_example, format_matcher, lint_datatable  # noqa: E402
from lib.lints import has_blocking, run_lints  # noqa: E402

_EXAMPLE_RE = re.compile(r"^\s*(?:Example|Scenario)(?:\s+Outline)?:\s*(.*?)\s*$")
_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")


def iter_steps_with_tables(feature_text: str):
    """yield (keyword, text, header_columns 或 None) —— header 為該 step 下 DataTable 的表頭欄位。"""
    out = []
    cur = None
    for line in feature_text.splitlines():
        m = STEP_RE.match(line)
        if m:
            cur = [m.group(1), m.group(2), None]
            out.append(cur)
            continue
        t = _TABLE_ROW_RE.match(line)
        if t and cur is not None and cur[2] is None:  # 第一列 = 表頭
            cur[2] = [c.strip() for c in t.group(1).split("|")]
    return [(kw, text, hdr) for kw, text, hdr in out]


def lint_feature_datatable_params(feature_text: str, dsl_steps) -> "list[str]":
    """feature 句掛了 DataTable 但比對到的 dsl_step 的 params 沒宣告表頭欄位 → 展開會 DSL_EXPAND_PARAM_UNKNOWN。"""
    matchers = [(format_matcher(d.get("format", "") or ""), d) for d in dsl_steps or []]
    warns: "list[str]" = []
    for _kw, text, headers in iter_steps_with_tables(feature_text):
        if not headers:
            continue
        step = next((d for rx, d in matchers if rx and rx.match(text)), None)
        if step is None:  # 無對應 dsl_step（pass-through）→ 非本 lint 範圍
            continue
        p = step.get("params")
        declared = set(p) if isinstance(p, list) else set(p.keys()) if isinstance(p, dict) else set()
        missing = [h for h in headers if h not in declared]
        if missing:
            warns.append(
                f"feature 句「{text}」掛 DataTable，但 dsl_step「{step.get('name')}」params 未宣告：{', '.join(missing)}"
            )
    return warns


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
        out.append(
            (rx, ins.get("instruction_type"), ins.get("data_format"), ins.get("datatable_parameters") or {})
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="dsl example → isa example 展開")
    ap.add_argument("--feature", required=True, help="含該 example 的 .feature")
    ap.add_argument("--example", help="只展開標題含此子字串的 example（省略＝全部）")
    ap.add_argument(
        "--dsl",
        required=True,
        action="append",
        help="dsl_steps 來源（{feature}.dsl.yml；可重複指定，例如再加上 {FP}/dsl.yml）。"
        "每個路徑的同名 `.draft`（推導中、尚未經 batch review 核可的定義）存在時自動一併載入。",
    )
    ap.add_argument("--isa", help="isa.yml（推 keyword 用；預設 <feature>/../../../isa.yml 找不到就略過）")
    ap.add_argument(
        "--framework-verify",
        metavar="CMD",
        help="選填：本腳本的展開是近似展開；給一條指令（例：專案的 red-refresh + preprocess）"
        "即在 lint 之後跑框架真展開，非 0 退出視為阻斷級。INSTALL_SPECTRUM=true 時建議帶上。",
    )
    args = ap.parse_args()

    feature_path = Path(args.feature)
    if not feature_path.is_file():
        print(f"feature 不存在：{feature_path}", file=sys.stderr)
        return 1

    # 每個 --dsl 都連帶載入其 `.draft`（SKILL-GAPS #46：推導中的定義住草稿檔，
    # 核可後才 merge 回本尊；沒有 draft 就只讀本尊）。draft 後載入 → 同名覆蓋本尊。
    dsl_paths: "list[Path]" = []
    for raw in args.dsl:
        p = Path(raw)
        draft = p.with_name(p.name + ".draft")
        if not p.is_file() and not draft.is_file():
            print(f"dsl.yml 不存在（本尊與 .draft 皆無）：{p}", file=sys.stderr)
            return 1
        if p.is_file():
            dsl_paths.append(p)
        if draft.is_file():
            dsl_paths.append(draft)

    by_name: "dict[str, dict]" = {}
    dsl_steps: "list[dict]" = []
    for p in dsl_paths:
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for d in doc.get("dsl_steps") or []:
            key = str(d.get("name"))
            if key in by_name:
                dsl_steps[dsl_steps.index(by_name[key])] = d
            else:
                dsl_steps.append(d)
            by_name[key] = d

    instructions = []
    if args.isa:
        instructions = load_instructions(Path(args.isa))

    feature_text = feature_path.read_text(encoding="utf-8")

    out = [f"# 展開 isa example — {feature_path.stem}"]
    for title, gwts in iter_examples_kw(feature_text):
        if args.example and args.example not in title:
            continue
        out.append(f"\n## Example: {title}")
        out.extend(expand_example(gwts, dsl_steps, instructions))
    print("\n".join(out))

    # lint：custom data_table 指令的 datatable_parameters 必須鏡射進 dsl_step 的 params/table
    warns = lint_datatable(dsl_steps, instructions)
    # lint：feature 句掛 DataTable 但 dsl_step params 未宣告表頭欄位（會 DSL_EXPAND_PARAM_UNKNOWN）
    warns += lint_feature_datatable_params(feature_text, dsl_steps)
    if warns:
        print("\n⚠ datatable lint：", file=sys.stderr)
        for w in warns:
            print(f"  - {w}", file=sys.stderr)

    # lint：#24 重複佈建／#40 seed-斷言對賬／#35 未捕獲 VAR／#23 預設蓋 DataTable／#52 預設格式漂移
    if not instructions:
        print(
            "\n⚠ 未提供 --isa，指令型別無從判定，語意 lint（重複佈建／seed 對賬／未捕獲 VAR）已略過。",
            file=sys.stderr,
        )
    findings = run_lints(feature_text, dsl_steps, instructions, example_filter=args.example)
    if findings:
        print("\n⚠ 展開 lint：", file=sys.stderr)
        for f in findings:
            print(f"  {f.render()}", file=sys.stderr)
    if has_blocking(findings):
        print(
            "\n展開 lint 有阻斷級違規（✗）——回 sub-SOP c 修正該 dsl_step 或 .feature 後重跑，"
            "不得帶著違規進 batch review。",
            file=sys.stderr,
        )
        return 3

    if args.framework_verify:
        print(f"\n▶ 框架真展開驗證：{args.framework_verify}", file=sys.stderr)
        proc = subprocess.run(args.framework_verify, shell=True)
        if proc.returncode != 0:
            print(
                f"\n框架真展開驗證失敗（exit {proc.returncode}）——本腳本的展開只是近似展開，"
                "框架擋下的 DSL_FORMAT_PARAM_COLLIDE_CAPTURE／DSL_DEFINITION_DUPLICATE_NAME／"
                "DSL_EXPAND_PARAM_UNKNOWN 一律在此收斂，不得留到 red 才炸。",
                file=sys.stderr,
            )
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
