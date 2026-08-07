"""dsl-refine：`.dsl.yml` 展開期的機械 lint（SKILL-GAPS #24／#40／#35／#23／#52）。

本模組只做**決定性檢查**，不做語意猜測；每條規則對應一次 benchmark 事故：

| code | 事故 | severity |
|------|------|----------|
| `duplicate-entity-setup` | B-71：同 example 對同一 entity 佈建兩次，唯一鍵相撞 | fail |
| `seed-assertion-consistency` | B-66：Given 佈建值與 Then 斷言值互相矛盾／恆真 | fail |
| `undefined-var` | SYMBOL_VAR_KEY_NOT_FOUND：`$alias.x` 引用了本 example 未捕獲的變數 | fail |
| `default-vs-datatable` | #23：param 有預設又被 feature DataTable 供值，預設靜默蓋掉 PM 的值 | warn |
| `param-default-pm-literal` | #52：param 預設寫成需衍生區轉換的 PM 字面值，格式靜默漂移 | fail |

純函式、不碰 filesystem，供 cli 與測試共用。
"""
from __future__ import annotations

import re

from lib.expand import expand_example_records, format_matcher

# ── 通用基元 ──────────────────────────────────────────────────────────────
_EXAMPLE_RE = re.compile(r"^\s*(?:Example|Scenario)(?:\s+Outline)?:\s*(.*?)\s*$")
_STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.*\S)\s*$")
_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")

# ISA 符號開頭的值不是字面值，不參與比對
_ISA_SYMBOL_PREFIX = ("$", "&", "@", "<", ">", "{{")
# `>alias.path` 捕獲宣告（DataTable 標頭）
_CAPTURE_RE = re.compile(r"^>\s*([\w一-鿿]+)((?:\.[\w一-鿿\[\]0-9]+)*)$")
# `$alias.path` / `${alias.path}` 引用
_VAR_REF_RE = re.compile(r"\$\{([\w一-鿿][\w一-鿿.\[\]]*)\}|\$([\w一-鿿][\w一-鿿.\[\]]*)")
# 「維持」型（不變斷言）與「變更」型（狀態改變斷言）的句面關鍵詞
_INVARIANT_KW = ("維持", "不變", "仍是", "仍為", "依然是", "還是")
_CHANGED_KW = ("變成", "改為", "轉為", "更新為", "調整為", "變更為")
# 「標題數值語意」比對：<中文標籤><數字>
_TITLE_NUM_RE = re.compile(r"([一-鿿]{2,10})\s*[為是]?\s*(\d+(?:\.\d+)?)")
# #52：需衍生區轉換的 PM 字面樣式
_PM_ANNOTATION_RE = re.compile(r"[（(][^（()）]*[一-鿿][^（()）]*[)）]")
# 空白分隔、無 T、無時區的日期時間；本身未必違規（專案 ISA 值域可能就吃這格式），
# 只有當同一支 feature 另以 ISO-8601 供值時才是 #52 的「兩套格式靜默漂移」。
_SPACE_DATETIME_RE = re.compile(r"^\s*\d{4}-\d{2}-\d{2}[ ]\d{2}:\d{2}(:\d{2})?\s*$")
_ISO_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")


class Finding:
    """一筆 lint 結果。severity：'fail' 阻斷、'warn' 提醒。"""

    __slots__ = ("severity", "code", "scope", "message")

    def __init__(self, severity: str, code: str, scope: str, message: str):
        self.severity = severity
        self.code = code
        self.scope = scope
        self.message = message

    def __repr__(self) -> str:  # pragma: no cover - debug 用
        return f"Finding({self.severity}, {self.code}, {self.scope!r}, {self.message!r})"

    def render(self) -> str:
        mark = "✗" if self.severity == "fail" else "⚠"
        return f"{mark} [{self.code}] {self.scope}：{self.message}"


def iter_examples_full(feature_text: str):
    """yield (title, [{keyword, text, headers, rows}])——保留每句底下的 DataTable。"""
    title = None
    steps: list = []
    started = False
    cur = None
    for line in feature_text.splitlines():
        ex = _EXAMPLE_RE.match(line)
        if ex:
            if started:
                yield title, steps
            title = ex.group(1) or "(無標題)"
            steps, cur = [], None
            started = True
            continue
        m = _STEP_RE.match(line)
        if m and started:
            cur = {"keyword": m.group(1), "text": m.group(2), "headers": None, "rows": []}
            steps.append(cur)
            continue
        t = _TABLE_ROW_RE.match(line)
        if t and cur is not None:
            cells = [c.strip() for c in t.group(1).split("|")]
            if cur["headers"] is None:
                cur["headers"] = cells
            else:
                cur["rows"].append(cells)
    if started:
        yield title, steps


def _is_literal(v) -> bool:
    s = str(v).strip()
    return bool(s) and not s.startswith(_ISA_SYMBOL_PREFIX)


def _param_items(params):
    """dsl_step.params → [(key, default_or_None)]。"""
    if isinstance(params, dict):
        return list(params.items())
    if isinstance(params, list):
        return [(k, None) for k in params]
    return []


# ── #24 duplicate-entity-setup ────────────────────────────────────────────
def _entity_of(isa_step) -> str:
    return isa_step["isa_captures"].get("entity") or isa_step["instruction"]


def _identity_cells(isa_step, captures) -> dict:
    """該 entity_setup 的「識別欄位」＝值源自 feature 句 format 捕獲的格。

    依 symbol-system-usage.md 的慣例：與情境無關的 NOT NULL 欄位放 params 預設，
    PM 在句子裡指名的值才是識別語意，故只以捕獲來源的格判定「同一筆資料」。
    """
    out = {}
    cap_keys = set(captures or {})
    for k, raw in isa_step["raw_table"].items():
        raw_s = str(raw)
        used = {m.group(1) for m in re.finditer(r"\{\{(\w+)\}\}", raw_s)}
        if used & cap_keys:
            rendered = isa_step["table"].get(k)
            if _is_literal(rendered):
                out[k] = str(rendered).strip()
    return out


def _alias_of(isa_step) -> "str | None":
    for k in isa_step["table"]:
        m = _CAPTURE_RE.match(str(k).strip())
        if m:
            return m.group(1)
    return None


def lint_duplicate_entity_setup(title: str, records) -> "list[Finding]":
    seen: list = []  # [(entity, alias, identity_cells, gwt_text)]
    out: "list[Finding]" = []
    for rec in records:
        for isa_step in rec["isa_steps"]:
            if isa_step["itype"] != "entity_setup":
                continue
            entity = _entity_of(isa_step)
            alias = _alias_of(isa_step)
            ident = _identity_cells(isa_step, rec["captures"])
            for p_entity, p_alias, p_ident, p_text in seen:
                if p_entity != entity:
                    continue
                if alias and p_alias and alias == p_alias:
                    out.append(
                        Finding(
                            "fail",
                            "duplicate-entity-setup",
                            f"Example「{title}」",
                            f"同一個 {entity} 被佈建兩次（alias 皆為 {alias}）："
                            f"「{p_text}」與「{rec['text']}」；同 example 同 entity 的 "
                            f"entity_setup 只准出現一次，後者應改為引用既有 ${alias} 的捕獲值",
                        )
                    )
                    break
                overlap = [
                    k for k in ident if k in p_ident and ident[k] == p_ident[k]
                ]
                if overlap:
                    cols = "、".join(f"{k}={ident[k]}" for k in overlap)
                    out.append(
                        Finding(
                            "fail",
                            "duplicate-entity-setup",
                            f"Example「{title}」",
                            f"同一個 {entity} 被佈建兩次且識別欄位重疊（{cols}）："
                            f"「{p_text}」與「{rec['text']}」；有唯一鍵會直接爆、沒唯一鍵會查到兩筆",
                        )
                    )
                    break
            seen.append((entity, alias, ident, rec["text"]))
    return out


# ── #35 undefined-VAR ─────────────────────────────────────────────────────
_EXPORT_PATH_RE = re.compile(r"^([\w一-鿿]+)((?:\.[\w一-鿿\[\]0-9]+)*)$")


def _captured_paths(isa_step) -> "set[str]":
    """該 isa_step 執行後可用的符號：DataTable 的 `>alias.path` 捕獲 ∪ 指令契約的 export_vars。

    export_vars 是 isa.yml 指令（builtin 與 custom 皆可）明文宣告的輸出契約——
    例如「是一個操作員」宣告 export `{{alias}}.id`，之後 `$業務阿宏.id` 就是合法引用。
    漏收它會讓 undefined-var 對完全合法的推導發阻斷級誤報（驗收實跑發現）。
    """
    out: "set[str]" = set()
    for k in isa_step["table"]:
        m = _CAPTURE_RE.match(str(k).strip())
        if m:
            root, path = m.group(1), m.group(2)
            out.add(root)
            if path:
                out.add(root + path)
    for k in isa_step.get("export_vars") or []:
        m = _EXPORT_PATH_RE.match(str(k).strip())
        if m:
            root, path = m.group(1), m.group(2)
            out.add(root)
            if path:
                out.add(root + path)
    return out


def _var_refs(value: str) -> "list[str]":
    return [m.group(1) or m.group(2) for m in _VAR_REF_RE.finditer(str(value))]


def lint_undefined_var(title: str, records) -> "list[Finding]":
    defined: "set[str]" = set()
    out: "list[Finding]" = []
    for rec in records:
        for isa_step in rec["isa_steps"]:
            for k, v in list(isa_step["table"].items()) + [("", isa_step["instruction"])]:
                key = str(k).strip()
                if _CAPTURE_RE.match(key):
                    continue  # 標頭本身是宣告、非引用
                val = str(v).strip()
                if key and val.startswith('"') and val.endswith('"'):
                    continue  # `"$var"` 為純字串、不解析（symbol-system-usage.md）
                for ref in _var_refs(v):
                    root = ref.split(".")[0]
                    if ref in defined or root in defined:
                        continue
                    out.append(
                        Finding(
                            "fail",
                            "undefined-var",
                            f"Example「{title}」",
                            f"isa_step「{isa_step['instruction']}」引用 ${ref}，"
                            f"但本 example 在該句之前沒有任何 >{ref} 捕獲"
                            f"（展開後執行期會 SYMBOL_VAR_KEY_NOT_FOUND）；"
                            f"若本情境刻意不佈建該筆資料，改送保證不存在的字面值",
                        )
                    )
            defined |= _captured_paths(isa_step)
    return out


# ── #23 default-vs-DataTable ──────────────────────────────────────────────
def lint_default_vs_datatable(title: str, steps, dsl_steps) -> "list[Finding]":
    matchers = [(format_matcher(d.get("format", "") or ""), d) for d in dsl_steps or []]
    out: "list[Finding]" = []
    for st in steps:
        if not st["headers"]:
            continue
        step = next((d for rx, d in matchers if rx and rx.match(st["text"])), None)
        if step is None:
            continue
        defaults = {k: v for k, v in _param_items(step.get("params")) if v is not None}
        clash = [h for h in st["headers"] if h in defaults]
        if clash:
            cols = "、".join(f"{h}（預設 {defaults[h]!r}）" for h in clash)
            out.append(
                Finding(
                    "warn",
                    "default-vs-datatable",
                    f"Example「{title}」",
                    f"句子「{st['text']}」掛了 DataTable，但 dsl_step「{step.get('name')}」"
                    f"的 params 對同名欄位有預設值：{cols}；展開會套預設、"
                    f"靜默蓋掉 PM 在表裡給的值，應把這些欄位改宣告成 required（無預設）",
                )
            )
    return out


# ── #52 param 預設格式漂移 ────────────────────────────────────────────────
def lint_param_default_pm_literal(dsl_steps, feature_text: str = "") -> "list[Finding]":
    """params 預設值不得寫「需要衍生區轉換」的 PM 字面。

    兩種樣式，嚴重度不同：
    - 中文括號註記（如「（台北時間）」）：一定要經衍生區正規化才能進 ISA → fail。
    - 空白分隔、無時區的日期時間：本身未必違規（專案的 ISA 值域可能就吃這格式）。
      只有當**同一支 feature 另有 ISO-8601 供值**時，才是 #52 的「feature 供值與 param
      預設走兩套格式」靜默漂移 → fail；否則只 warn，提醒作者確認與 feature 供值同格式。
    """
    feature_has_iso = bool(_ISO_DATETIME_RE.search(feature_text or ""))
    out: "list[Finding]" = []
    for d in dsl_steps or []:
        for k, default in _param_items(d.get("params")):
            if default is None or not isinstance(default, str):
                continue
            scope = f"dsl_step「{d.get('name')}」"
            if _PM_ANNOTATION_RE.search(default):
                out.append(
                    Finding(
                        "fail",
                        "param-default-pm-literal",
                        scope,
                        f"params.{k} 的預設值 {default!r} 含中文括號註記（如「（台北時間）」）；"
                        f"params 預設不會經過衍生區的字面正規化，"
                        f"必須直接寫 ISA 值域的最終字面（例：2026-03-02T10:00:00+08:00）",
                    )
                )
                continue
            if _SPACE_DATETIME_RE.match(default):
                if feature_has_iso:
                    out.append(
                        Finding(
                            "fail",
                            "param-default-pm-literal",
                            scope,
                            f"params.{k} 的預設值 {default!r} 是空白分隔且無時區的日期時間，"
                            f"但同一支 feature 另以 ISO-8601 供值；同一個 dsl_step 的 feature 供值"
                            f"與 param 預設走兩套格式會靜默漂移，預設須改寫成同一格式",
                        )
                    )
                else:
                    out.append(
                        Finding(
                            "warn",
                            "param-default-pm-literal",
                            scope,
                            f"params.{k} 的預設值 {default!r} 是空白分隔且無時區的日期時間；"
                            f"params 預設不經衍生區正規化，請確認它已是 ISA 值域的最終字面、"
                            f"且與 feature 供值同格式",
                        )
                    )
    return out


# ── #40 seed／斷言一致性 ──────────────────────────────────────────────────
def _seed_index(records) -> dict:
    """entity → {欄位: 值}（只收字面值）。"""
    seeds: dict = {}
    for rec in records:
        for isa_step in rec["isa_steps"]:
            if isa_step["itype"] != "entity_setup":
                continue
            bag = seeds.setdefault(_entity_of(isa_step), {})
            for k, v in isa_step["table"].items():
                if _CAPTURE_RE.match(str(k).strip()):
                    continue
                if _is_literal(v):
                    bag[str(k).strip()] = str(v).strip()
    return seeds


def _sent_index(records) -> dict:
    """api_call 送出的欄位 → 值（只收字面值）。"""
    sent: dict = {}
    for rec in records:
        for isa_step in rec["isa_steps"]:
            if isa_step["itype"] != "api_call":
                continue
            for k, v in isa_step["table"].items():
                if _CAPTURE_RE.match(str(k).strip()):
                    continue
                if _is_literal(v):
                    sent[str(k).strip()] = str(v).strip()
    return sent


_ASSERT_TYPES = ("entity_validate", "response_validate", "entity_non_existence_validate")
# 句子裡 PM 明寫的字面值（引號值或裸數字）——只有這些值才是該句「宣稱」的斷言值
_LITERAL_IN_SENTENCE_RE = re.compile(r'"([^"]*)"|(?<![\w.-])(-?\d+(?:\.\d+)?)(?![\w.])')


def _claimed_after(text: str, keywords) -> "set[str]":
    """取「維持／變成」等關鍵詞之後 PM 明寫的字面值。

    只比對句子明講的那個值，避免把 entity 定位欄位（如 member_name）誤判成斷言標的。
    """
    out: "set[str]" = set()
    for kw in keywords:
        start = 0
        while True:
            i = text.find(kw, start)
            if i < 0:
                break
            start = i + len(kw)
            m = _LITERAL_IN_SENTENCE_RE.search(text, start)
            if m:
                out.add(m.group(1) if m.group(1) is not None else m.group(2))
    return out - {""}


def lint_seed_assertion_consistency(title: str, records) -> "list[Finding]":
    seeds = _seed_index(records)
    sent = _sent_index(records)
    flat_seed: dict = {}
    for bag in seeds.values():
        flat_seed.update(bag)
    out: "list[Finding]" = []

    for rec in records:
        text = rec["text"]
        claimed_invariant = _claimed_after(text, _INVARIANT_KW)
        claimed_changed = _claimed_after(text, _CHANGED_KW)
        claimed_all = {a or b for a, b in _LITERAL_IN_SENTENCE_RE.findall(text)} - {""}
        for isa_step in rec["isa_steps"]:
            if isa_step["itype"] not in _ASSERT_TYPES:
                continue
            entity = isa_step["isa_captures"].get("entity")
            bag = seeds.get(entity, flat_seed) if entity else flat_seed
            for k, v in isa_step["table"].items():
                key = str(k).strip()
                if _CAPTURE_RE.match(key) or not _is_literal(v):
                    continue
                val = str(v).strip()
                seeded = bag.get(key)
                if val in claimed_invariant and seeded is not None and seeded != val:
                    out.append(
                        Finding(
                            "fail",
                            "seed-assertion-consistency",
                            f"Example「{title}」",
                            f"「{text}」是不變斷言，斷言 {key}={val}，"
                            f"但同 example 的 Given 佈建值是 {key}={seeded}；"
                            f"seed 與斷言互相矛盾，任何符合契約的實作都過不了",
                        )
                    )
                    continue
                if val in claimed_changed and seeded is not None and seeded == val:
                    out.append(
                        Finding(
                            "fail",
                            "seed-assertion-consistency",
                            f"Example「{title}」",
                            f"「{text}」是變更斷言，斷言 {key}={val}，"
                            f"但同 example 的 Given 佈建值本來就是 {key}={seeded}；"
                            f"該斷言恆真、證明不了任何狀態轉移",
                        )
                    )
                    continue
                posted = sent.get(key)
                if val in claimed_all and not claimed_invariant and posted is not None and posted != val:
                    out.append(
                        Finding(
                            "fail",
                            "seed-assertion-consistency",
                            f"Example「{title}」",
                            f"「{text}」斷言 {key}={val}，但同 example 的 When "
                            f"送出的是 {key}={posted}；三方對賬不一致",
                        )
                    )
                    continue
    out += _lint_title_numbers(title, records, flat_seed)
    return out


def _lint_title_numbers(title: str, records, flat_seed) -> "list[Finding]":
    """標題數值語意 vs seed 值：標題寫「累計凍結次數 1」而 seed 佈成 0 即矛盾。

    只在標籤能對上「本 example 某個 dsl_step 的 params 鍵或 DataTable 欄位」時比對，
    避免對任意數字亂報。
    """
    label_to_field: dict = {}
    for rec in records:
        step = rec["dsl_step"]
        if not step:
            continue
        for key, _default in _param_items(step.get("params")):
            for isa_step in rec["isa_steps"]:
                for col, raw in isa_step["raw_table"].items():
                    if "{{%s}}" % key == str(raw).strip():
                        label_to_field.setdefault(str(key), str(col).strip())
    out: "list[Finding]" = []
    for label, num in _TITLE_NUM_RE.findall(title):
        field = label_to_field.get(label)
        if field is None:
            continue
        seeded = flat_seed.get(field)
        if seeded is not None and str(seeded).strip() != num:
            out.append(
                Finding(
                    "fail",
                    "seed-assertion-consistency",
                    f"Example「{title}」",
                    f"標題寫「{label} {num}」，但展開後 {field} 的 seed 值是 {seeded}；"
                    f"標題的數值語意與佈建值不一致",
                )
            )
    return out


# ── 對外入口 ──────────────────────────────────────────────────────────────
def run_lints(feature_text: str, dsl_steps, instructions=None, example_filter=None):
    """跑齊五條 lint，回傳 [Finding]（依 example 出現順序）。"""
    findings: "list[Finding]" = []
    findings += lint_param_default_pm_literal(dsl_steps, feature_text)
    for title, steps in iter_examples_full(feature_text):
        if example_filter and example_filter not in title:
            continue
        records = expand_example_records(
            [(s["keyword"], s["text"]) for s in steps], dsl_steps, instructions
        )
        findings += lint_duplicate_entity_setup(title, records)
        findings += lint_seed_assertion_consistency(title, records)
        findings += lint_undefined_var(title, records)
        findings += lint_default_vs_datatable(title, steps, dsl_steps)
    return findings


def has_blocking(findings) -> bool:
    return any(f.severity == "fail" for f in findings)
