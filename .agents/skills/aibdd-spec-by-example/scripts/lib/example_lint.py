"""spec-by-example：Example 草稿的機械檢核（SKILL-GAPS #43／#36／#14）。

只做決定性掃描，語意判斷仍屬 rules/ 與稽核者。三條規則：

| code | 規則來源 | severity |
|------|----------|----------|
| `step-arity` | cucumber-literal-format 不變式 6（>4 參數必改 DataTable） | 4 個＝warn、>4＝fail |
| `unspecified-target` | #36：path 參數的「沒指定」情境 HTTP 層不可觀測 | warn |
| `example-comment-blank-line` | formatter-rules 註解空行（#14 擴及所有 Example 上方註解） | warn |
"""
from __future__ import annotations

import re

_STEP_RE = re.compile(r"^(\s*)(Given|When|Then|And|But)\s+(.*\S)\s*$")
_EXAMPLE_RE = re.compile(r"^\s*(?:Example|Scenario)(?:\s+Outline)?:\s*(.*?)\s*$")
_RULE_RE = re.compile(r"^\s*Rule:\s*(.*?)\s*$")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_COMMENT_RE = re.compile(r"^\s*#")

# 可綁定參數＝ASCII 引號值 ＋ 裸寫數字（cucumber-literal-format 不變式 1／「可綁定參數計數」）
_QUOTED_RE = re.compile(r'"[^"]*"')
_BARE_NUM_RE = re.compile(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w.])")

# #36：「沒指定 <標的>」句面
_UNSPECIFIED_RE = re.compile(r"(?:但)?(?:沒|未|沒有)(?:指定|選擇|選)\s*([一-鿿]{2,8})")

ARITY_WARN = 4


class Finding:
    __slots__ = ("severity", "code", "scope", "message")

    def __init__(self, severity: str, code: str, scope: str, message: str):
        self.severity = severity
        self.code = code
        self.scope = scope
        self.message = message

    def render(self) -> str:
        mark = "✗" if self.severity == "fail" else "⚠"
        return f"{mark} [{self.code}] {self.scope}：{self.message}"


def count_bindable(step_text: str) -> int:
    """一行 step 的可綁定參數數：ASCII 引號值 ＋ 引號外的裸數字。"""
    quoted = _QUOTED_RE.findall(step_text)
    outside = _QUOTED_RE.sub(" ", step_text)
    return len(quoted) + len(_BARE_NUM_RE.findall(outside))


def parse(feature_text: str):
    """→ [{rule, title, line_no, steps:[{keyword, text, line_no, has_table}], comment_ok}]。"""
    lines = feature_text.splitlines()
    examples: list = []
    cur = None
    rule = None
    for i, raw in enumerate(lines):
        m_rule = _RULE_RE.match(raw)
        if m_rule:
            rule = m_rule.group(1)
            cur = None
            continue
        m_ex = _EXAMPLE_RE.match(raw)
        if m_ex:
            # 上方註解區塊：往上收連續的 `#` 行，其上必須是空行（或檔首）
            j = i - 1
            comment_lines = []
            while j >= 0 and _COMMENT_RE.match(lines[j]):
                comment_lines.append(j)
                j -= 1
            comment_ok = True
            if comment_lines:
                comment_ok = j < 0 or not lines[j].strip()
            cur = {
                "rule": rule,
                "title": m_ex.group(1) or "(無標題)",
                "line_no": i + 1,
                "steps": [],
                "comment_lines": [n + 1 for n in reversed(comment_lines)],
                "comment_ok": comment_ok,
            }
            examples.append(cur)
            continue
        m_step = _STEP_RE.match(raw)
        if m_step and cur is not None:
            cur["steps"].append(
                {
                    "keyword": m_step.group(2),
                    "text": m_step.group(3),
                    "line_no": i + 1,
                    "has_table": False,
                }
            )
            continue
        if _TABLE_ROW_RE.match(raw) and cur is not None and cur["steps"]:
            cur["steps"][-1]["has_table"] = True
    return examples


def lint_step_arity(examples) -> "list[Finding]":
    out: "list[Finding]" = []
    for ex in examples:
        for st in ex["steps"]:
            if st["has_table"]:
                continue  # 已改表，不變式 6 已滿足
            n = count_bindable(st["text"])
            if n > ARITY_WARN:
                out.append(
                    Finding(
                        "fail",
                        "step-arity",
                        f"L{st['line_no']} Example「{ex['title']}」",
                        f"{st['keyword']} 句承載 {n} 個可綁定參數，超過上限 4："
                        f"「{st['text']}」。依 cucumber-literal-format 不變式 6 必須改表——"
                        f"{_arity_advice(st['keyword'])}",
                    )
                )
            elif n == ARITY_WARN:
                out.append(
                    Finding(
                        "warn",
                        "step-arity",
                        f"L{st['line_no']} Example「{ex['title']}」",
                        f"{st['keyword']} 句剛好 4 個可綁定參數（表格已滿）："
                        f"「{st['text']}」。之後任何依可核對性補欄位的修改都會踩到上限，"
                        f"屆時 {_arity_advice(st['keyword'])}",
                    )
                )
    return out


def _arity_advice(keyword: str) -> str:
    if keyword == "Given":
        return "Given 是資料佈建句，改成「句尾冒號 + DataTable」無害，直接改表"
    return (
        "When／Then 先檢討是不是把非必要參數寫進句子了（pm-writing-rules 可核對性 1："
        "既沒被 Then 驗證、也沒驅動本例行為的資訊一律刪除）；刪不掉才改表"
    )


def lint_unspecified_target(examples, feature_text: str) -> "list[Finding]":
    """#36：「沒指定 <標的>」若 <標的> 是 URL path 參數，HTTP 層不可觀測。"""
    def is_identified(target: str) -> bool:
        """本 feature 別處是否以具體實例定位這個標的（`"值" 的<標的>` 或 `<標的> "值"`）。"""
        t = re.escape(target)
        return bool(
            re.search(r'"[^"]*"\s*的\s*' + t, feature_text)
            or re.search(t + r'\s*"[^"]*"', feature_text)
        )

    out: "list[Finding]" = []
    for ex in examples:
        for st in ex["steps"]:
            for target in _UNSPECIFIED_RE.findall(st["text"]):
                if not is_identified(target):
                    continue
                out.append(
                    Finding(
                        "warn",
                        "unspecified-target",
                        f"L{st['line_no']} Example「{ex['title']}」",
                        f"本例的失敗原因是「沒指定{target}」，而 {target} 在本 feature 其他句子"
                        f"是以具體實例定位的標的。若 {target} 在 API 契約上是 URL path 參數，"
                        f"「未提供」在 HTTP 層根本不可觀測（路由不匹配→404，不是規格要求的 400），"
                        f"此 Example 到 red 階段必然受阻。確認它是 body／query 參數才保留；"
                        f"是 path 就改寫成等價類「給了格式非法的{target}」或「給了不存在的{target}」",
                    )
                )
    return out


def lint_example_comment_blank_line(examples) -> "list[Finding]":
    """#14：Example 上方的註解（含 `# 取捨：` 與 `# 測試設計註記`）之前必為空行。"""
    return [
        Finding(
            "warn",
            "example-comment-blank-line",
            f"L{ex['comment_lines'][0]} Example「{ex['title']}」",
            "Example 上方的註解之前缺一行空行；formatter-rules 的註解空行規則"
            "適用於所有 Example 上方註解（不只 `# 取捨：`）",
        )
        for ex in examples
        if ex["comment_lines"] and not ex["comment_ok"]
    ]


def run_lints(feature_text: str) -> "list[Finding]":
    examples = parse(feature_text)
    return (
        lint_step_arity(examples)
        + lint_unspecified_target(examples, feature_text)
        + lint_example_comment_blank_line(examples)
    )


def has_blocking(findings) -> bool:
    return any(f.severity == "fail" for f in findings)
