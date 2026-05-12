# Intake Questions — Phase 1 訪談題庫

> 本 reference 提供 Phase 1 各 step 要問 user 的具體題目。**純 declarative**
> — 不含 step flow（per 規章 §4.7 SOP SSOT 原則）。
>
> 使用方式：SKILL.md `#1.1` ~ `#1.6` 各 step LOAD 對應 § 取題目文字。

---

## §1 Skill Name

**問**：你想建立的 skill 叫什麼名字？（kebab-case, ≤64 字元）

**驗收條件**：
- 全小寫 + 數字 + dash
- 不可 `--` / 不可起末 hyphen
- 與 `~/.claude/skills/` 內既有 skill 不衝突（或 user 同意 overwrite）

**範例**：`my-feature-spec` / `pdf-anonymizer` / `weekly-summary`

---

## §2 Skill Description

**問**：這支 skill 做什麼？什麼時候該被觸發？什麼情況下該 skip？

**驗收條件**：
- ≤1024 字元（hard cap，per quick_validate.py）；建議 ≤500 字元
- 不含尖括號
- 必含 WHAT + TRIGGER when... + SKIP when...

**範例**：
```
Author X. TRIGGER when user says A / B / C, or context Y. SKIP when artifact already populated, or wrong stack.
```

---

## §3 Skill Prose Language

**問**：這支 skill 的步驟描述（prose）要用哪個語言撰寫？（譬如 `zh-TW`、`en`、`ja`、`zh-CN`）

**驗收條件**：
- 必須回單一 BCP-47-like tag 或常見語言名稱（`zh-TW` / `en` / `Traditional Chinese` / `English` 等都接受）
- 影響範圍：`### Phase N — <imperative-name>` 的 imperative-name 可雙語（verb 部分英文，名詞可在地化）；step body 描述與 SOP 內的失敗分支都用該語言
- **不影響**：verb whitelist（永遠英文 capital）、reference path、`#phase.step` literal、frontmatter `name`/`description` schema 鍵名

**範例**：
- `zh-TW`：`1. READ .specify/memory/bdd-constitution.md 抽 axes`
- `en`：`1. READ .specify/memory/bdd-constitution.md to extract axes`
- `ja`：`1. READ .specify/memory/bdd-constitution.md から axes を抽出`

**default**：若 user 未明示，沿用 user 上次與 AI 對話的主要語言；仍無從判斷則 `en`。

---

## §4 Phase Outline

**問**：這支 skill 內部要分幾個 Phase？每個 Phase 完成什麼？（imperative form 命名，譬如 `LOAD constitution` / `VALIDATE intake` / `EMIT REPORT`）

**驗收條件**：
- 至少 1 phase
- 每個 phase 名稱以動詞開頭（imperative form）
- 最後一個 phase 通常是 `REPORT`

**範例**：
```
Phase 1 — LOAD inputs
Phase 2 — VALIDATE schema
Phase 3 — TRANSFORM data
Phase 4 — EMIT REPORT
```

---

## §5 Per-Phase Rough Steps

**問**：每個 Phase 內部要做哪些 step？每個 step 一個動詞（READ / WRITE / LOAD / DELEGATE / ASSERT / IF / LOOP / GOTO ...）。

**驗收條件**：
- 每 step 開頭是 verb-whitelist 動詞（見 [`verb-whitelist.md`](verb-whitelist.md)）
- 一行一動詞，禁 compound（無 "A and B"）
- branching 必拆 IF/ELSE sub-step
- LOOP 必標 budget + exit condition

**逐 phase 收集**。允許 user 給粗略 prose，本 skill Phase 2 會 classify 並回頭重問。

---

## §6 References / Scripts / Assets / Reasoning

**問**：這支 skill 需要哪些：
1. **全局 references**（整個 skill 都會用的規範 / schema / lookup table）— 寫在 SKILL.md 第一個 §1 REFERENCES YAML 內
2. **step-local references**（特定 step 才用的細部規範）— 在該 step inline cite，不入 §1 表
3. **scripts**（python / bash / node — deterministic logic）
4. **assets**（template / boilerplate / 圖片 — 被 output 引用的檔）
5. **reasoning artifacts**（RP-local semantic micro-protocol）— 放 `reasoning/`，不列入 §1 REFERENCES

**驗收條件**：
- references 數量 ≥0（即使 0 也要在 §1 REFERENCES 留 `references: []`，per 規章 §3.6）
- 每個 reference 標 path + purpose（一句話）
- scripts 標 lang（python / bash / node）+ 用途
- assets 標 path + 用途
- reasoning artifacts 標 context + RP name + consumes / produces

---

## §7 Reasoning Pipeline

**問**：這支 skill 是否需要 `reasoning/` pipeline？
若需要，請描述：

1. reasoning contexts（例如 `skill-creation` / `bdd-analysis`）
2. RP list（每個 RP 一句話說明它做的 semantic transformation）
3. 每個 RP 的 `consumes` / `produces`
4. 是否有 polymorphic slot（同一 slot 多種推理策略）
5. polymorphic slot 的 variant selector 由哪個 SKILL.md input / config 決定
6. 哪些 RP output 是 terminal output，哪些只餵給下游 RP
7. RP 途中若遇到 information gap，是否允許 ASK；若允許，ASK 結果要如何進 reducer output

**驗收條件**：
- 若 user 說「不需要」，`$$reasoning_plan.enabled = false`
- 若需要，每個 RP 至少有 `id` / `context` / `slot` / `name` / `consumes` / `produces`
- polymorphic slot 必有 selector + variants
- terminal RP output 必可追蹤到 final REPORT 或 generated artifact

**範例**：
```yaml
enabled: true
contexts:
  - id: skill-creation
    rps:
      - id: skill-creation.00-source-intake-material
        consumes: [user_intake]
        produces: [source_material_bundle]
      - id: skill-creation.01-design-reasoning-pipeline
        consumes: [source_material_bundle]
        produces: [reasoning_plan]
polymorphism:
  - slot: "02"
    selector: reasoning_complexity
    variants: [simple-skill, reasoning-heavy-skill]
```

---

## §8 確認 step

**問**：以上回答 OK 嗎？確認後進入 Phase 2 驗證。

**驗收條件**：user 明示 confirm（"OK" / "確認" / "go" / 同義詞）。
