"""dsl-refine 掃描純邏輯：偵測「未完成定義 dsl step」、供 worklist 產出。

純函式、不碰 filesystem，供 cli 與測試共用。
- parameterize：引號值 / 日期 / 數字 → {pN}（與 feature 句子比對用）
- format_matcher：dsl_step.format（{name} 佔位 或 ^…$ regex）→ 比對具體 GWT 句的 regex
- done_formats：從 dsl.yml 文字抽出「標 `# done`」的 dsl_step 之 format
- iter_examples：feature 文字 → (example 標題, [GWT 原句])
- undone_in_example：該 example 中比不到任何 done format 的行 = 未完成
"""
from __future__ import annotations

import re

STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.*\S)\s*$")
# 左到右、date 在 number 之前：引號值 / 日期 / 數字（含小數）
TOKEN_RE = re.compile(r'("[^"]*")|(\d{4}-\d{2}-\d{2})|(\d+(?:\.\d+)?)')
_EXAMPLE_RE = re.compile(r"^\s*(?:Example|Scenario)(?:\s+Outline)?:\s*(.*?)\s*$")
_DONE_RE = re.compile(r"^\s*#\s*done\b")
_NAME_RE = re.compile(r"^\s*-\s*name:")
_NAME_VAL_RE = re.compile(r"^\s*-\s*name:\s*(.*\S)\s*$")
_FORMAT_RE = re.compile(r"^\s*format:\s*(.*\S)\s*$")
_PLACEHOLDER_RE = re.compile(r'"\{(\w+)\}"|\{(\w+)\}')
_BARE_VAL = r"(?P<%s>\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)?)"


def parameterize(text: str) -> str:
    counter = {"n": 0}

    def repl(m: "re.Match[str]") -> str:
        counter["n"] += 1
        ph = f'{{p{counter["n"]}}}'
        return f'"{ph}"' if m.group(1) is not None else ph

    return TOKEN_RE.sub(repl, text)


def format_matcher(fmt: str):
    """dsl_step.format → 比對具體 GWT 句的 compiled regex（具名群組擷取值）。"""
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


def _sq_unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def done_formats(dsl_text: str) -> "list[str]":
    """回傳 dsl.yml 中「name 上方標 `# done`」的 dsl_step 之 format 清單。"""
    lines = dsl_text.splitlines()
    out: "list[str]" = []
    pending = False
    for idx, ln in enumerate(lines):
        if _DONE_RE.match(ln):
            pending = True
            continue
        if _NAME_RE.match(ln):
            if pending:
                for j in range(idx + 1, len(lines)):
                    if _NAME_RE.match(lines[j]) or _DONE_RE.match(lines[j]):
                        break
                    fm = _FORMAT_RE.match(lines[j])
                    if fm:
                        out.append(_sq_unquote(fm.group(1)))
                        break
            pending = False
    return out


def all_step_formats(dsl_text: str) -> "list[tuple[str, str]]":
    """回傳 dsl.yml 中「所有」dsl_step 的 (name, format)（不論是否標 `# done`）。

    供「先找後建」與「FP 級去重」比對既有定義用。
    """
    lines = dsl_text.splitlines()
    out: "list[tuple[str, str]]" = []
    for idx, ln in enumerate(lines):
        nm = _NAME_VAL_RE.match(ln)
        if not nm:
            continue
        name = _sq_unquote(nm.group(1))
        for j in range(idx + 1, len(lines)):
            if _NAME_RE.match(lines[j]):
                break
            fm = _FORMAT_RE.match(lines[j])
            if fm:
                out.append((name, _sq_unquote(fm.group(1))))
                break
    return out


def iter_examples(feature_text: str):
    """yield (title, [raw_step_text, ...]) per Example/Scenario。"""
    title = None
    steps: "list[str]" = []
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
            steps.append(m.group(2))
    if started:
        yield title, steps


def undone_in_example(steps: "list[str]", done_matchers) -> "list[str]":
    """該 example 中，比不到任何 done dsl_step 的原句 = 未完成。"""
    return [t for t in steps if not any(rx and rx.match(t) for rx in done_matchers)]
