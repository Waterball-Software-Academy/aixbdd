"""dsl-refine：把一個 dsl example 依 dsl_steps[] 展開成 isa example（.isa.feature 樣式）。

對應流程 step e 的「預期展開後的 ISA Example」。純函式、供 cli 與測試共用。
展開語意對齊 specformula-java DslExpander：
- format 比對該 GWT 句、擷取具名值（captures）。
- params：非 null 預設先以 captures 解析 {{...}}，再被 captures 覆蓋。
- isa_step：instruction / table / text 內的 {{name}} 內插；ISA 符號（$ > < & @）原樣保留。
- keyword 依 instruction 對到的 isa.yml instruction_type 推（無 isa 目錄則沿用原句 keyword）。
"""
from __future__ import annotations

import re

# 自足的比對基元（與 skill 根 scripts/lib/scan.py 同義；sub-SOP 自帶，避免反向依賴主流程腳本）
STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.*\S)\s*$")
_PLACEHOLDER_RE = re.compile(r'"\{(\w+)\}"|\{(\w+)\}')
_BARE_VAL = r"(?P<%s>\d{4}-\d{2}-\d{2}|-?\d+(?:\.\d+)?)"
_TT_RE = re.compile(r"\{\{(\w+)\}\}")


def format_matcher(fmt: str):
    """dsl_step.format（{name} 佔位 或 ^…$ regex）→ 比對具體 GWT 句的 compiled regex。"""
    if "(?P<" in fmt or "(?<" in fmt or (fmt.startswith("^") and fmt.endswith("$")):
        pat = fmt if fmt.startswith("^") else "^" + fmt
        pat = pat if pat.endswith("$") else pat + "$"
        try:
            return re.compile(pat)
        except re.error:
            return None
    parts = ["^"]
    i = 0
    for m in _PLACEHOLDER_RE.finditer(fmt):
        parts.append(re.escape(fmt[i : m.start()]))
        if m.group(1) is not None:
            parts.append('"(?P<%s>[^"]*)"' % m.group(1))
        else:
            parts.append(_BARE_VAL % m.group(2))
        i = m.end()
    parts.append(re.escape(fmt[i:]))
    parts.append("$")
    try:
        return re.compile("".join(parts))
    except re.error:
        return None

_KW = {
    "time_control": "Given",
    "entity_setup": "Given",
    "api_call": "When",
    "response_validate": "Then",
    "entity_validate": "Then",
    "entity_non_existence_validate": "Then",
}


def _subst(s, vmap) -> str:
    return _TT_RE.sub(lambda m: str(vmap.get(m.group(1), "{{" + m.group(1) + "}}")), str(s))


def extract_values(fmt: str, line_text: str, params=None) -> dict:
    """擷取 format 具名值，並疊上 params 預設（預設可用 {{capture}} 內插）。"""
    captures = {}
    rx = format_matcher(fmt)
    if rx:
        m = rx.match(line_text)
        if m:
            captures = {k: v for k, v in m.groupdict().items() if v is not None}
    params = params or {}
    if isinstance(params, list):  # [a, b] = 全必填、無預設（schema 允許的 list 形式）
        params = {k: None for k in params}
    vmap = {}
    for k, default in params.items():
        if default is not None:  # null 預設 = 必填，留給 captures
            vmap[k] = _subst(default, captures)
    vmap.update(captures)  # captures 覆蓋預設
    return vmap


def classify(instr_text: str, instructions):
    """instr 對 isa.yml instructions → (instruction_type, data_format)。"""
    for rx, itype, dfmt, *_ in instructions:
        if rx.match(instr_text):
            return itype, dfmt
    return None, None


def classify_full(instr_text: str, instructions):
    """instr 對 isa.yml instructions → (instruction_type, data_format, captures, export_vars)。

    captures 為該 instruction format 的具名群組（例：entity_setup 的 `entity`、
    api_call 的 `summary`），供 lint 判定「同一個 entity」等語意。
    export_vars 為該指令契約宣告的輸出符號 key（如 `{{alias}}.id`）——builtin 與 custom
    都可能宣告，是 `$var` 的合法來源之一，undefined-var lint 必須認得。
    """
    for rx, itype, dfmt, *rest in instructions:
        m = rx.match(instr_text)
        if m:
            exports = list((rest[1] if len(rest) > 1 else None) or {})
            return itype, dfmt, {k: v for k, v in m.groupdict().items() if v is not None}, exports
    return None, None, {}, []


def _param_keys(params) -> set:
    """dsl_step.params（list 或 dict）→ 宣告的參數 key 集合。"""
    if isinstance(params, dict):
        return set(params.keys())
    if isinstance(params, list):
        return set(params)
    return set()


def lint_datatable(dsl_steps, instructions) -> "list[str]":
    """檢查：dsl_step 對上 data_table 指令（isa.yml 有 datatable_parameters）時，
    其 required 欄位是否都帶進了 isa_step.table，且 dsl_step.params 是否宣告。

    回傳警告字串清單（空＝通過）。instructions 須為 (rx, itype, dfmt, datatable_parameters)。
    """
    warns: "list[str]" = []
    for d in dsl_steps or []:
        declared = _param_keys(d.get("params"))
        for isa_step in d.get("isa_steps") or []:
            instr = str(isa_step.get("instruction", ""))
            dt_params = None
            for rx, _itype, dfmt, *rest in instructions:
                if rx.match(instr) and dfmt == "data_table":
                    dt_params = rest[0] if rest else None
                    break
            if not dt_params:
                continue
            required = [k for k, v in dt_params.items() if (v or {}).get("required")]
            table_keys = set((isa_step.get("table") or {}).keys())
            miss_table = [k for k in required if k not in table_keys]
            miss_param = [k for k in required if k not in declared]
            if miss_table:
                warns.append(
                    f"dsl_step「{d.get('name')}」對上 data_table 指令「{instr}」，"
                    f"isa_step.table 缺必填欄位：{', '.join(miss_table)}"
                )
            if miss_param:
                warns.append(
                    f"dsl_step「{d.get('name')}」params 未宣告 datatable 欄位：{', '.join(miss_param)}"
                )
    return warns


def _render_isa_step(isa_step: dict, vmap: dict, source_kw, instructions, out: list) -> None:
    instr = _subst(isa_step.get("instruction", ""), vmap)
    itype, dfmt = classify(instr, instructions)
    kw = _KW.get(itype, source_kw or "And")
    out.append(f"    {kw} {instr}")

    text = isa_step.get("text")
    table = isa_step.get("table")
    if text:
        out.append('      """')
        for ln in _subst(text, vmap).splitlines():
            out.append("      " + ln)
        out.append('      """')
    elif table:
        keys = [_subst(k, vmap) for k in table.keys()]
        vals = [_subst(v, vmap) for v in table.values()]
        if dfmt == "json":
            out.append('      """json')
            out.append("      {")
            for k, v in zip(keys, vals):
                out.append(f"        {k}: {v}")
            out.append("      }")
            out.append('      """')
        else:
            out.append("      | " + " | ".join(keys) + " |")
            out.append("      | " + " | ".join(vals) + " |")


def expand_example_records(gwt_steps, dsl_steps, instructions=None) -> list:
    """與 expand_example 同一套比對／內插，但回傳結構化紀錄供 lint 消費。

    每筆：{keyword, text, dsl_step, captures, vmap, isa_steps:[{instruction, itype,
    dfmt, isa_captures, table:{k:v}, raw_table:{k:v}, text}]}。
    `raw_table` 保留內插前的模板值，用來判斷某格的值是否源自 format 捕獲。
    """
    instructions = instructions or []
    matchers = [(format_matcher(d.get("format", "") or ""), d) for d in dsl_steps or []]
    records: list = []
    for kw, text in gwt_steps:
        step = next((d for rx, d in matchers if rx and rx.match(text)), None)
        rec = {
            "keyword": kw,
            "text": text,
            "dsl_step": step,
            "captures": {},
            "vmap": {},
            "isa_steps": [],
        }
        records.append(rec)
        if step is None:
            continue
        fmt = step.get("format", "") or ""
        rx = format_matcher(fmt)
        m = rx.match(text) if rx else None
        rec["captures"] = {k: v for k, v in (m.groupdict() if m else {}).items() if v is not None}
        rec["vmap"] = extract_values(fmt, text, step.get("params"))
        for isa_step in step.get("isa_steps") or []:
            instr = _subst(isa_step.get("instruction", ""), rec["vmap"])
            itype, dfmt, isa_caps, exports = classify_full(instr, instructions)
            raw_table = isa_step.get("table") or {}
            table = {
                _subst(k, rec["vmap"]): _subst(v, rec["vmap"]) for k, v in raw_table.items()
            }
            rec["isa_steps"].append(
                {
                    "instruction": instr,
                    "itype": itype,
                    "dfmt": dfmt,
                    "isa_captures": isa_caps,
                    "export_vars": [_subst(k, rec["vmap"]) for k in exports],
                    "table": table,
                    "raw_table": {_subst(k, rec["vmap"]): v for k, v in raw_table.items()},
                    "text": _subst(isa_step.get("text") or "", rec["vmap"]),
                }
            )
    return records


def expand_example(gwt_steps, dsl_steps, instructions=None) -> list:
    """gwt_steps: [(keyword, text)]；dsl_steps: [{name,format,params,isa_steps}]。

    回傳 .isa.feature 樣式行清單（每行 GWT 原句以註解標出，下接其展開的 isa step）。
    """
    instructions = instructions or []
    matchers = [(format_matcher(d.get("format", "")), d) for d in dsl_steps]
    out: list = []
    for kw, text in gwt_steps:
        out.append(f"\n  # {kw} {text}")
        step = None
        for rx, d in matchers:
            if rx and rx.match(text):
                step = d
                break
        if step is None:
            out.append("    （無對應 dsl_step）")
            continue
        if not step.get("isa_steps"):
            out.append("    （isa_steps 未定義）")
            continue
        vmap = extract_values(step.get("format", ""), text, step.get("params"))
        for isa_step in step["isa_steps"]:
            _render_isa_step(isa_step, vmap, kw, instructions, out)
    return out
