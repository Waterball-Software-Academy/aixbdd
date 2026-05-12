# AIBDD Skill Family — Unified SKILL.md 規章

> **Status**: 草案 v0
> **適用**: 所有 `.claude/skills/` 與 `.specify/extensions/aibdd/skills/` 下的 skill
> **起源**: 使用者於 2026-04-28 提案 + `/skill-creator` best practices + dogfooding session 觀察
> **目標**: 讓另一個 AI agent 能以 `#phase#step` 形式 resume 任何 skill 的執行 — 規章嚴格度以「program counter 紀律」為核心

---

## §0 為什麼需要統一規章

### 0.1 觀察到的問題

不同 skill 寫法分歧：

- 有的把推理流程寫成 SOP（aibdd-discovery、aibdd-red v2）— 接近理想
- 有的把流程混在「角色 / 入口契約 / 執行 SOP / 完成條件 / 失敗處置」多 section 內，AI 讀完一遍才能組裝出順序（aibdd-form-feature-spec、speckit-aibdd-debug v1）
- 有的在 SKILL.md 內塞 Gherkin 語法、template、code block ≥10 行（教學 + 規格混雜）
- 有的把 Hard rules / Behaviour rules 寫死在 SKILL.md，跨 skill 重抄同一條紀律
- 有的 SOP 步驟動詞不固定，混雜 imperative 與 declarative 句型，AI 解讀步驟邊界時要重複猜

每一種分歧都讓 program counter 概念失效 — AI 無法精確指向「我現在在 Step X.Y.Z」。

### 0.2 解決方向

統一 SKILL.md 為 **「program-counter-friendly SOP」格式**：

- SKILL.md body 只放 phase + numbered list
- 全部「規範 / 要點 / template / few-shot」抽到 references/ 與 assets/
- 全部「腳本」抽到 scripts/
- 「全局」reference 在 SKILL.md 第一個 section 用表格列出
- 「step-local」reference 在該 step 內用 inline 路徑 cite

這樣每個 skill 都能像 CPU 在執行 instruction stream — pointer 永遠指向某個明確 `#phase.step` 編號，AI 能精準回報「我在 #2.3.1」。

---

## §1 SKILL.md 強制 Layout

每個 SKILL.md **僅得有**以下 top-level section（順序固定）：

```
---
<frontmatter>          ← §2 規範
---

# <skill-name>

<one-line skill role；imperative 句>

> **Program-like SKILL.md — self-contained notation**          ← §27 強制 blockquote
> **3 verb classes**: D = Deterministic / S = Semantic / I = Interactive
> **SSA**: `$x = VERB args`; `$x` phase-local; `$$x` crosses phases.
> **Side effect**: `VERB target ← $payload`. **Branch**: `BRANCH $check ? a : b`.
> **Jump**: `GOTO #N.M` = Phase N step M.
>
> | Verb | T | Meaning |
> |---|---|---|
> | ... |

## §1 REFERENCES        ← §3 規範，全局 reference YAML

```yaml
references:
  - path: references/<name>.md
    purpose: <一句說明 LOAD 此檔的目的>
```

## §2 SOP               ← §4 規範

### Phase 1 — <imperative-name>
1. ...

### Phase 2 — <imperative-name>
1. ...

## §3 CROSS-REFERENCES   ← optional，純導覽

- `/related-skill` — bla bla
```

**禁止任何其他 top-level section**。Failure handling 必寫在 `## §2 SOP` 對應 step 的 IF / BRANCH / LOOP 內；Hard rules / Behaviour rules / Examples / Anti-patterns 一律抽到 references/。

---

## §2 YAML Frontmatter 契約

### 2.1 允許欄位（per `quick_validate.py`）

僅得用以下 6 個 top-level key：

| Key | Type | Required | Notes |
|---|---|---|---|
| `name` | string | YES | kebab-case, ≤64 chars, 不可 `--` / 起末 hyphen |
| `description` | string | YES | ≤1024 chars, 不含尖括號 |
| `license` | string | NO | 罕用 |
| `allowed-tools` | list | NO | tool 限制（罕用） |
| `metadata` | dict | NO | 任意巢狀 dict（譬如 `source` / `user-invocable` / `disable-model-invocation`） |
| `compatibility` | string | NO | ≤500 chars |

### 2.2 description 寫法規範

- **WHAT**: 一句話說 skill 做什麼
- **WHEN to use**: trigger 條件（user 說什麼 / 情境）
- **WHEN not to use**: SKIP 條件
- **格式建議**: `<verb-phrase>. TRIGGER when ... . SKIP when ...`
- **長度建議**: ≤500 字元（hard cap 1024，留 buffer 給未來 trigger 擴充）
- **禁止**: 尖括號（會被 validator reject）

### 2.3 metadata 子欄位慣例

```yaml
metadata:
  user-invocable: true             # 是否可被 user 用 /skill-name 呼叫
  disable-model-invocation: false  # 是否禁止 model 自動觸發
  source: "<lineage>"              # plugin / preset / project-level dogfooding
  author: "<name>"                 # optional
  skill-type: planner              # 可選 enum：reference-hub / planner / formulation / utility
```

`skill-type: reference-hub` 是 §14.1 例外觸發鍵 — 純 reference hub skill 設此值後可省 §2 SOP。判定條件：
- frontmatter `metadata.user-invocable: false`
- 不執行流程，純供 sibling skill 透過 `<hub-name>::<filename>.md` LOAD references
- 至少有 1 個 `references/*.md` 檔

### 2.4 範例（合格 frontmatter）

```yaml
---
name: aibdd-red
description: 紅燈專家 sub-skill。讓某個 RED-UNIT 或 RED-ACCEPT task 進入合法紅燈狀態；step-def body 強制走 testability-plan named anchor。TRIGGER when user says 紅燈 / red / RED-UNIT，或被 /speckit.implement / /speckit.aibdd.debug DELEGATE。SKIP when feature 還沒 spec 化或無對應 DSL entry。
metadata:
  user-invocable: true
  source: project-level dogfooding
---
```

---

## §3 §1 REFERENCES Section（SKILL.md 第一個 section）

### 3.1 角色

宣告**全局 reference** — 整個 skill 任何 phase / step 都會 LOAD 的 reference。
**Step-local reference** 不放在這裡（在該 step 內 inline cite）。

### 3.2 YAML schema

```yaml
references:
  - path: references/<name>.md
    purpose: <一句說明 LOAD 此檔的目的>
  - path: <absolute-or-project-path>
    purpose: <如 `.specify/memory/bdd-constitution.md`>
  - path: aibdd-core::<reference>.md
    purpose: <跨 skill 共用的 stable hub reference>
```

### 3.3 欄位規則

- **path**: 相對於 skill dir 的路徑 / project-root 路徑 / `aibdd-core::*` stable hub reference 路徑
- **purpose**: 一句話，imperative form（"提供 X 的權威定義" / "定義 Y 的 schema"）
- 每筆 reference 只能有 `path` / `purpose` 兩個 key；不得新增 `id`、`kind`、`phase_scope`
- `path` 含 `::` 時視為 stable hub reference；否則 validator 以 skill dir 相對路徑驗證存在

### 3.4 Step-local reference 的 cite grammar

step body 內直接寫 inline path link：

```markdown
1. READ [`references/foo.md`](references/foo.md) §2 抽 ${VAR}
```

**禁止**在 SOP body 內提及 `R1` / `R2` 這類 ID — references 不再提供 ID 簡寫；所有 step-local / global reference cite 都用真實 path，避免誤把 step-local 升為全局。

### 3.5 Section 命名規範

第一個 section 的標題必須**字面**寫成 `## §1 REFERENCES`（含 §1 編號 + 大寫 REFERENCES）。AI parser 抓這個固定字面當 anchor。

### 3.6 空 references 處理

即使 skill 不 LOAD 任何全局 reference，仍須留下可 parse 的空 YAML：

````markdown
## §1 REFERENCES

```yaml
references: []
```
````

維持 layout 一致性，方便 lint。

---

## §4 §2 SOP Section — Phase + Numbered

### 4.1 Phase 命名

```markdown
### Phase 1 — <imperative-name>
```

- `Phase` 一律首字大寫
- N 是純數字 1, 2, 3, ...（無前綴 0；無小數）
- `<imperative-name>` 是動詞片語，描述本 Phase 完成什麼（「LOAD bdd-constitution」/「FORMULATE artifact」/「EMIT REPORT」）— 一律 imperative form
- Phase 之間嚴格串行；非 Phase N 完成不得開始 Phase N+1

### 4.2 編號系統

使用十進位編號樹：

```markdown
### Phase 1 — Setup
1. <step>
2. <step>
   2.1 <sub-step>
   2.2 <sub-step>
       2.2.1 <sub-sub-step>
       2.2.2 <sub-sub-step>
3. <step>
```

- 第一層 `1.` `2.` `3.`
- 第二層 `2.1` `2.2`（前置兩格縮排）
- 第三層 `2.2.1` `2.2.2`（前置四格縮排）
- 第四層 `2.2.1.1`（前置六格縮排）— **避免**；超過三層多半是該抽 reference

### 4.3 Program Counter 識別

執行中任何時刻，AI 必須能用 `#phase.step` 字串指出當前位置：

- `#1.2` = Phase 1 第 2 步
- `#3.2.1` = Phase 3 第 2 步第 1 子步
- `#3.2.1.3` = Phase 3 第 2 步第 1 子步第 3 子子步

### 4.4 Step body 微觀規範（**最關鍵**）

每個 step 必須符合：

- **One verb, one step**：每個 step 開頭是動詞，禁止「A and B」compound 句
- **Imperative form**：READ / WRITE / COMPUTE / DELEGATE / VALIDATE / EMIT / ASSERT / REPORT / STOP / TRIGGER / IF / ELSE / LOOP / END LOOP（見 §5 verb whitelist）
- **長度建議 ≤80 chars 一行**：能寫一行就寫一行；超過則拆 sub-step
- **禁止 prose 段落**：step 不是論述，是指令
- **inline cite reference**: 用 markdown link 形式
- **explicit guard for branching**: 任何 if/else 必拆兩個 sub-step + guard

### 4.5 GOOD 範例

```markdown
### Phase 1 — LOAD constitution
1. READ `.specify/memory/bdd-constitution.md`
2. EXTRACT axes per [`references/load-constitution.md`](references/load-constitution.md) §1
3. ASSERT axes 無 `TODO` / 空值
   3.1 IF assertion fails:
       3.1.1 STOP
       3.1.2 DELEGATE `/clarify-loop` 帶 topic=`bdd-infra-axes`
   3.2 ELSE:
       3.2.1 BIND axes as readonly dict
       3.2.2 GOTO #2.1

### Phase 2 — Build DSL Index
1. READ `.specify/memory/DSL-core.md`
2. READ `${FEATURE_DIR}/DSL-local.md`
3. JOIN entries by id (DSL-local overrides DSL-core)
4. CROSS-VALIDATE each entry's L4.ref against testability anchors
   4.1 IF any L4.ref unresolved:
       4.1.1 STOP
       4.1.2 RETURN to /speckit.aibdd.testability-analyze
```

### 4.6 BAD 範例（違反規章）

```markdown
### Phase 1 — Setup
1. 讀 bdd-constitution.md，抽 axes，並驗證所有 axes 無 TODO，若有 TODO 就 STOP 並 DELEGATE /clarify-loop，否則綁定為 readonly dict 並進入下一階段
```

違反：

- 一個 step 多 verb（讀 + 抽 + 驗 + STOP + DELEGATE + 綁定 + 進入）
- 長度爆炸（單行 80 字以上）
- branching 沒拆 sub-step
- 混雜 imperative + declarative 句型

修正方法：拆成第 4.5 範例的形式。

### 4.7 SOP SSOT 原則（**唯一一處寫步驟流程**）

**步驟流程的 single source of truth = SKILL.md `## §2 SOP` section**。

#### 4.7.1 強制：步驟流程只能寫在 SKILL.md

- references/ — **禁止**寫步驟流程；只寫 declarative 規範 / schema / 表格 / template / 範例
- assets/ — **禁止**寫步驟流程；只放被 output 引用的 binary / template 檔
- scripts/ — **禁止**用 README / docstring 描述「使用者該怎麼跑這個 skill」的流程；script 自己的內部邏輯（python control flow）不算流程，那是 implementation
- 任何 sibling skill / aibdd-core reference — **禁止**重抄這支 skill 的步驟流程

#### 4.7.2 為什麼

- 流程散開兩處 → AI 必須 cross-reference 拼湊執行順序 → program counter 失效
- 流程在 references/ → SKILL.md body 反而要描述「然後去看 ref X.md 第 N 條」 → 一個 step 變兩個檔，PC 無法精確指向
- references/ 一改流程 → SKILL.md 不一定同步 → drift 災難

#### 4.7.3 子流程怎麼放（永遠在 SKILL.md 內）

SKILL.md 可以**無限縮排**寫子流程：

```markdown
3. EXECUTE acceptance runner
   3.1 PARSE result
       3.1.1 IF Value Difference: GOTO #5.1
       3.1.2 IF compile error:
             3.1.2.1 LOAD failure-triage table
             3.1.2.2 CLASSIFY error per Class A/B/C/D
                     3.1.2.2.1 IF Class A: REMEDIATE step-def assertion
                     3.1.2.2.2 IF Class B: REMEDIATE stub body
```

子流程深度沒上限。但**第 4 層以上仍應檢查**「是不是該抽 reference 講 declarative 規範，把判斷邏輯留在 SKILL.md」。

#### 4.7.4 references 該寫什麼（vs 流程）

| 應寫在 references/ | 應寫在 SKILL.md |
|---|---|
| 規範 schema（譬如 DSL 4-layer schema 定義） | 「如何用 schema 推導下一步」的步驟 |
| anti-pattern token list | 「如何 detect token + remediation 步驟」 |
| BEFORE/AFTER 範例 | 「migration 步驟」 |
| 表格 / lookup matrix（跨多 step 反覆查） | 「如何在表格內查值 + 用值做下一步」 |
| 教學 / 動機 / why | （不在規章內 — 動機段不該在 skill 中）|
| **Quality gate rubric**（rule_id checklist / script→check 對照表 / pass criteria，由**單一** SOP step 之 TRIGGER / DELEGATE / ASSERT 消費） | **inline 於該 step 的 phase 內，禁止抽到 references/contracts/X.md** — 見 §4.7.6 |

#### 4.7.5 違反偵測

任何 reference / asset / script 內出現：

- `Step 1 / Step 2 / ...` 編號
- `Phase N` 字眼
- imperative 動詞列（READ / WRITE / DELEGATE 等 §5 verb whitelist）連續 ≥3 行
- 「如果 X 那麼 Y 否則 Z」decision tree
- **Quality gate rubric 跡象**：檔名含 `quality` / `contract` / `gate` 且 body 含 ≥3 列 `rule_id` 風格 table，或描述「subagent 評判依據」/「TRIGGER script 檢查項」/「pass criteria」

→ **是 SKILL.md 漏抓的步驟流程／rubric，必搬回 SKILL.md**。

#### 4.7.6 Quality gate rubric 必 inline 於 SOP

**規則**：當一張 rule_id checklist / script→check table 是某個 SOP step（TRIGGER script、DELEGATE subagent、ASSERT invariant）的**評判依據**時，rubric 必須 inline 於該 phase 內，禁止抽到 `references/contracts/quality.md` 或同類檔案。

**為什麼**：
- Quality gate **是** SOP — 是否通關決定流程是否前進（典型範例：BRANCH `$verdict.ok` ? next : redo）
- Rubric 與 gate step 共生 — 抽出後 SKILL.md 僅剩 `DELEGATE Subagent per references/contracts/X.md §Y`，PC 失去語意；reader 不 LOAD reference 不知道 gate 在驗什麼
- Rubric 不是「跨多 step 反覆查」的 lookup table，是**單一 step 的契約**

**正確做法**（範例：4 個 TRIGGER + 1 個 DELEGATE + verdict）：

```markdown
### Phase N — VALIDATE artifacts

#### N.A Script gates (deterministic)

| # | Script | Check |
|---|---|---|
| 1 | `check_X.py` | <one-line check> |
| 2 | `check_Y.py` | <one-line check> |

1. `$x_out` = TRIGGER `python ${$$skill_dir}/scripts/python/check_X.py`
2. `$y_out` = TRIGGER `python ${$$skill_dir}/scripts/python/check_Y.py`

#### N.B Semantic gate (subagent)

Planner 禁止 self-judge — DELEGATE 至獨立 subagent，依下表 rubric 評判：

| rule_id | Requirement |
|---|---|
| `RULE_A` | <one-line semantic invariant> |
| `RULE_B` | <one-line semantic invariant> |

3. `$semantic` = DELEGATE Subagent semantic validation with rubric=Phase N.B table, input=`$$artifact_set`

#### N.C Verdict

4. `$$verdict` = PARSE merged JSON of `$x_out` `$y_out` `$semantic`
5. BRANCH `$$verdict.ok` ? GOTO #M.1 : GOTO #(redo).1

**Failure contract**: violations 不得透過弱化 checklist 來 patch；fail 時返回 #(redo).1 並帶回原始 inputs。
```

**何時例外**：rubric 跨**多** skill 共用（aibdd-core SSOT）— 此時 rubric 進 `aibdd-core::*.md`，由各 caller skill 在 SOP step 內以 `aibdd-core::` 前綴 LOAD 並注入。 仍**不得**進該 caller skill 自己的 references/。

#### 4.7.7 Skill artifact 必須 self-contained

**規則**：產出的 skill 必須能只靠自身 skill directory 內的 `SKILL.md`、`references/`、`reasoning/`、`scripts/`、`assets/`，加上明確宣告的 stable hub reference（例如 `aibdd-core::*.md`）與 caller/runtime input，完成自己的 runtime decision。不得把 skill 的 runtime gate、rubric、contract、verdict shape、quality oracle、handoff criteria 指到臨時外部檔案。

**禁止**：
- `research/**`
- `.cursor/plans/**`
- 任意 `*-outcome-eval.md` / `eval.md` / `proposal.md` 作為 runtime rubric
- 絕對本機路徑中的 research / plan / course note，例如 `/Users/.../research/...`
- `DELEGATE ... rubric=research/...` 或 `PARSE ... quality gate from ../research/...`

**允許**：
- skill 自身目錄內的 `references/*.md`、`reasoning/**/*.md`、`scripts/**`、`assets/**`
- `aibdd-core::*.md` 這類穩定 shared reference hub
- `${RUNTIME_PATH}` / caller payload / workspace artifact 這類執行期 input，但它們只能是待處理材料，不得是 skill 自己的規章 / gate / rubric SSOT

**為什麼**：
- skill package 被複製、安裝、交給另一個 agent 時，外部 research/eval 草稿可能不存在
- runtime gate 若住在外部臨時檔，skill 實際公共契約不可審查
- self-contained 是 program-like skill 的封裝邊界：外部材料可以被處理，內部規章必須隨 skill 發佈

**正確做法**：若需要 semantic gate，rubric 要 inline 在該 SOP phase，或收進本 skill 的 `references/quality-gate-contract.md` 再由該 SOP phase PARSE。若該 rubric 是跨 skill 長期共用規章，才 promote 到 `aibdd-core::...`。

### 4.8 GOTO 與 step reference grammar

任何「跳到上面某一步」「回到某 phase」「reference 之前 step」的指令，**必用 `#phase.step` 字面格式**，不得用自然語言描述。

#### 4.8.1 GOTO target 格式

```markdown
3.1 IF Value Difference: GOTO #5.1
4.2 IF env error: REMEDIATE; GOTO #4.1     ← 回頭重 loop
5.3 IF user reject: GOTO #2.1               ← 回到 Phase 2 step 1
```

合法 target 格式：

- `#1` = Phase 1 開頭
- `#2.3` = Phase 2 第 3 步
- `#3.2.1` = Phase 3 第 2 步第 1 子步
- `#3.2.1.4` = 任意深度的 PC 編號

#### 4.8.2 禁止的 GOTO 寫法

```markdown
3.1 IF X: GOTO 上面那一步                  ← 禁止：自然語言
3.2 IF Y: 回到 Phase 2                     ← 禁止：未明示確切 step
3.3 IF Z: 重新從 step 3 開始                ← 禁止：未用 #N 格式
```

#### 4.8.3 為什麼強制 `#phase.step` literal

- AI parser 用 `\#\d+(\.\d+)*` regex 即可解析 GOTO target，無需 NLP
- session resume 時，PC 直接 jump 到 `#phase.step` 編號 — 確定性執行
- 改編號（譬如 Phase 3 加新 step） → grep 全 SKILL.md 找 `#3\.` 引用，全部要同步改 — 機械化 refactor 友善

#### 4.8.4 forward GOTO vs backward GOTO

兩者都允許：

- **Forward**: `GOTO #5.1`（跳過中間 step；常見於 fail-fast / early return）
- **Backward**: `GOTO #4.1`（loop 重頭；必伴隨 §7.2 LOOP budget + exit condition）

任何 backward GOTO **必在外層 LOOP 內**，否則 = silent 無限迴圈，違反 §7.2。

---

## §5 Verb Whitelist — 三閉集 cognitive-type taxonomy

每個 step 開頭必為以下三個閉集之一的 verb；**cognitive type 由 verb 自動推得**，作者不需要在 step 標 `[D]/[S]/[I]`。完整 verb 速查見 [`verb-whitelist.md`](verb-whitelist.md)。

### 5.1 D-verbs — Deterministic（無 LLM 判斷；future scripting candidate）

`READ` / `WRITE` / `CREATE` / `DELETE` / `COMPUTE` / `DERIVE` / `PARSE` / `RENDER` /
`ASSERT` / `MATCH` / `TRIGGER` / `DELEGATE` / `MARK` / `BRANCH` / `GOTO` /
`IF` / `ELSE` / `END IF` / `LOOP` / `END LOOP` / `RETURN` / `STOP` / `EMIT` / `WAIT`

D-step 給定相同 input 應產生相同 output；不依賴 LLM 推理。**未來**若連續 D-block 收益夠（per §26.2 SCRIPT-CANDIDATE audit）可考慮抽成 script —— 但分類為 D 不等於現在就必須是 script，只是「沒有 LLM-judgment 屏障」這個性質。

### 5.2 S-verbs — Semantic（LLM-only reasoning）

`THINK` / `CLASSIFY` / `JUDGE` / `DECIDE` / `DRAFT` / `EDIT` /
`PARAPHRASE` / `CRITIQUE` / `SUMMARIZE` / `EXPLAIN`

S-step **不可被 script 取代**：需要 LLM 解讀 fuzzy 輸入、生成 prose、做 regex 做不到的判斷。

### 5.3 I-verbs — Interactive

`ASK`（仍需配 `[USER INTERACTION]` tag，per §8.3）

### 5.4 紀律

- **One verb per step** —— 每個 step 開頭一個 verb
- **One cognitive type per step** —— 因為一個 verb，所以自動成立
- **禁止 verb**：模糊動詞如「處理」「調整」「考慮」「思考」「決定」「處置」 —— 這些是 prose 不是指令
- **被棄用 verb**：`LOAD` / `VALIDATE` / `REPORT` / `CAPTURE` / `STAGE` / `RECORD` / `FORMULATE` / `EXPAND` —— 改用更精確的新 verb（見 verb-whitelist.md「變更說明」）

---

## §6 Reference / Asset / Script Lazy Loading

### 6.1 Lazy load 原則

- SKILL.md 第一個 section（REFERENCES）只用 YAML 列**全局** ref 的 `path` / `purpose` 索引 — 不 inline 內容
- Step-local ref 在該 step inline cite — AI 才會在 program counter 走到該 step 時 LOAD
- **禁止** SKILL.md body 內 dump reference 全文（即使再短）

### 6.2 為什麼

- 全文 dump → context 爆炸 → 多 skill 互相 chain 時 context 容量耗盡
- Lazy load → 只在 PC 真的走到該 step 才付 token cost
- 對應 skill-creator 「Progressive Disclosure」原則

### 6.3 反例與正確寫法

❌ SKILL.md 內：

```markdown
1. EXTRACT axes per the following table:
   | Axis | Allowed values | Default |
   | ... | ... | ... |
```

✅ 正確：

```markdown
1. EXTRACT axes per [`references/axes-table.md`](references/axes-table.md) §1
```

---

## §7 PROGRAM COUNTER 紀律

### 7.1 Branching 強制拆 sub-step

任何 if/else 一律拆成兩個 sub-step：

```markdown
3. ASSERT axes 無 TODO
   3.1 IF assertion fails:
       3.1.1 STOP
       3.1.2 DELEGATE /clarify-loop
   3.2 ELSE:
       3.2.1 CONTINUE
```

**禁止**：在一個 step body 內寫「若 X 則 Y 否則 Z」 — 必拆。

### 7.2 Loop 強制標 budget + exit condition

```markdown
4. LOOP until VALID RED (max 3 iterations per [`references/loop-budgets.md`](references/loop-budgets.md))
   4.1 EXECUTE acceptance runner
   4.2 CLASSIFY result
       4.2.1 IF Value Difference: GOTO 5
       4.2.2 IF env error: REMEDIATE per failure-triage; CONTINUE LOOP
   4.3 IF iteration count >= 3: ESCALATE to user; STOP
   END LOOP
5. REPORT result
```

### 7.3 Resume from PC

任何 step 必須能在 session resume / compaction recovery 時被 AI 從 PC 讀回繼續：

- TodoWrite ingest = phase 級（每 phase 一個 todo）
- Step-level state 由 thinking + 文字訊息持有
- 跑到 #2.3.1 時 session crash → recovery 後讀 TodoWrite → in-progress phase = Phase 2 → 從 #2.3.1 重跑

---

## §8 USER INTERACTION 標示

### 8.1 預設規則

**整個 SOP 預設不對 user 開 turn 結尾**，連續 auto-advance 跑到底。

### 8.2 USER INTERACTION 例外

只有以下兩類 step 可被標為 `[USER INTERACTION]` 並產生獨立 turn 等 user 回應：

1. **Clarify** — 缺資訊需 user 補（DELEGATE /clarify-loop 是首選；自寫 Q 是次選）
2. **Approval gate** — 改前 / 高風險動作前需 user 明示同意

### 8.3 標示 grammar

```markdown
3. [USER INTERACTION] DELEGATE `/clarify-loop` with topic=`bdd-axes`
   WAIT for user response
4. [USER INTERACTION] ASK user "確認啟動 archive？"
   WAIT for `confirm` or `revise`
```

不標 `[USER INTERACTION]` 的 step 不得 yield turn 給 user（auto-advance 紀律）。

---

## §9 DELEGATE 契約

### 9.1 payload schema 必明示

```markdown
2. DELEGATE `/aibdd-red` with payload:
   - `phase`: `unit | accept`
   - `feature_file`: <abs path>
   - `scenario_name`: <verbatim from .feature>
   - `task_id`: <Tnnn or DBG-<bug-slug>>
```

### 9.2 REPORT contract 必明示（callee 端）

每個 user-invocable / DELEGATE-able skill 的 SOP **最後一個 phase** 必為 `REPORT`，且 payload schema 寫死：

```markdown
### Phase N — REPORT

1. EMIT to caller:
   - `status`: `completed | failed`
   - `task_id`: <echo>
   - `dsl_mapping`: list of {step_prose, dsl_entry_id, L3_type, L4_anchor}
   - `loop_iterations`: <int>
   - `test_output_summary`: <first failing message>
2. MARK skill completed
```

### 9.3 REPORT 對 user 的 plain language

REPORT phase 還可額外有：

```markdown
3. REPORT to user (plain language, ≤3 sentences):
   "Phase X 完成，產出 N 個 artifact。{若殘留問題列 1 條}"
```

避免對 user dump JSON。

---

## §10 Failure Handling Must Stay Inside SOP

### 10.1 原則

Failure handling 是控制流，不是附錄。每一個可能中斷、重試、rollback、詢問 user、或回到上游 skill 的情境，都必須寫在 `## §2 SOP` 的對應 phase / step 內。

### 10.2 正確形式

```markdown
### Phase 1 — LOAD constitution

1. `$cfg_exists` = MATCH path_exists(`.specify/memory/bdd-constitution.md`)
2. BRANCH `$cfg_exists` ? GOTO #1.3 : GOTO #1.2.1
   2.1 `$msg` = RENDER "missing constitution; run /speckit.constitution first"
   2.2 EMIT `$msg` to user
   2.3 STOP
3. `$cfg` = READ `.specify/memory/bdd-constitution.md`
4. `$$axes` = PARSE `$cfg`, schema=`axes`
```

Rollback 也一樣留在造成 side effect 的附近：

```markdown
### Phase 4 — WRITE artifact

1. WRITE `$$target_path` ← `$rendered`
   1.1 IF WRITE partially succeeds then fails:
       1.1.1 DELETE `$$target_path`
       1.1.2 `$msg` = RENDER "write failed and partial file was removed"
       1.1.3 EMIT `$msg` to user
       1.1.4 STOP
```

### 10.3 禁止形式

- 禁止新增獨立 top-level failure / fallback section。
- 禁止把 Phase 1 的失敗處理放在文件尾端，讓 reader 必須跳出 program counter 才知道下一步。
- 禁止用「某 phase fail handling」清單複寫 SOP 內已經存在的分支。

---

## §11 Cross-skill 共用紀律 — aibdd-core SSOT

### 11.1 不得重抄

跨 skill 共用的概念 — 譬如：

- DSL 4-layer schema
- bdd-constitution axes 抽取流程
- PF-23 prose binding 規則
- /clarify-loop payload schema
- physical-first principle
- atomic rule 定義

— **MUST live in `aibdd-core/references/`**，每支 skill 用 reference cite，**禁止重抄**。

### 11.2 共用 reference cite grammar

```markdown
1. EXTRACT axes per [`aibdd-core::load-constitution.md`](.specify/extensions/aibdd/skills/aibdd-core/references/load-constitution.md)
```

或在 §1 REFERENCES YAML 用 `path: aibdd-core::<name>.md` 簡寫表示。

### 11.3 違反偵測

任何 SKILL.md 出現 ≥2 個其他 skill 也有的「規則段 / schema 段 / template」 → 該段必抽 aibdd-core。

---

## §12 大小限制

### 12.1 SKILL.md body

- **目標**：≤300 行（不含 frontmatter）
- **建議**：≤200 行（保留 spare）
- **超出**：必檢查是否有「規範 / template / 教學」應抽 reference

### 12.2 references/

- 單一 reference ≤500 行（per skill-creator best practice）
- 超過 → 拆多個 references，依 phase scope 切

### 12.3 assets/

- 無大小限制（但避免 commit 大 binary；用 git-lfs 或外部 host）

### 12.4 scripts/

- 單一 script ≤300 行（規模大就拆 module）
- 必有 docstring + usage 範例

---

## §13 檔名 / 目錄 / 命名

### 13.1 必遵守

| 物件 | 規則 |
|---|---|
| `SKILL.md` | 大寫 `SKILL.md`（不可 `skill.md` / `Skill.md`）|
| `references/` | 全小寫 + dash 命名（`load-constitution.md` 而非 `LoadConstitution.md`） |
| `assets/` | 全小寫 |
| `scripts/<lang>/` | `bash/` / `python/` / `node/` / etc.；script name kebab-case |
| skill name (frontmatter) | kebab-case ≤64 chars |

### 13.2 Path placeholder 慣例

SKILL.md / references 內動態路徑用 `${VAR}` 樣式：

- `${SPECS_ROOT_DIR}` / `${FEATURE_DIR}` / `${BDD_CONSTITUTION_PATH}` / `${STEP_DEFS_PATH}` / etc.

固定 path 用 backtick literal：

- `` `.specify/memory/bdd-constitution.md` ``

---

## §14 SKILL.md 禁止內容（exhaustive）

### 14.1 Hard 禁止 — 違反即 invalid

- README / INSTALLATION_GUIDE / CHANGELOG / QUICK_REFERENCE 等 auxiliary file（只 SKILL.md + references/ + assets/ + scripts/）
- top-level section 不在 §1 layout 列表內
- 獨立的 failure / fallback top-level section（失敗分支必留在 §2 SOP）
- frontmatter top-level key 不在 §2.1 allow list
- 無 §1 REFERENCES section（即使 skill 不 LOAD 任何 reference 也要寫一個空表 + 註解）
- 無 §2 SOP section（**例外**：見 §14.1.1）
- description > 1024 chars
- description 含尖括號

### 14.1.1 Reference-hub skill §2 SOP 豁免

純 reference hub skill（`metadata.skill-type: reference-hub` + `metadata.user-invocable: false` + 無自身可執行流程，純供 sibling skill 透過 `<hub-name>::<filename>.md` LOAD）可省以下 section：

- `## §2 SOP`

豁免後 SKILL.md body 僅需：
- `## §1 REFERENCES` 表（列出 hub 內全部 references/ 檔）
- 一段「LOAD-only」聲明（≤3 行，說明此 hub 不執行流程）
- optional `## §3 CROSS-REFERENCES`

驗證 script 偵測 `metadata.skill-type == "reference-hub"` 後 skip C4 check；C15 仍禁止任何獨立 failure/fallback section。

### 14.2 Soft 禁止 — 違反需顯式正當化

- SKILL.md body > 300 行
- step body > 80 chars 一行（一般情況）
- 一個 step 包含多個 verb（compound）
- 整段 prose / 教學文 / 動機段（→ references）
- inline 表格 / template / few-shot（→ references / assets）
- inline code block ≥10 行（→ references / assets）
- step body 內含註解 hack（用 imperative 改寫，不用註解）
- 未標 `[USER INTERACTION]` 的 step 試圖 yield turn

---

## §15 自動驗證 checklist

未來可寫一個 `validate-skill-spec.py` 跑：

| Check | 如何 |
|---|---|
| C1 frontmatter 合 §2.1 | YAML parse + key whitelist |
| C2 description ≤1024 chars 無尖括號 | str check |
| C3 第一個 section 是 `## §1 REFERENCES` | regex |
| C4 第二個 section 是 `## §2 SOP` | regex（reference-hub skill 豁免，per §14.1.1）|
| C5 SOP 內 phase header 字面 `### Phase N — <name>` | regex |
| C6 step 動詞在 §5 verb whitelist | tokenize 第一個 word |
| C7 step body ≤80 chars 一行 | 一般情況 warn，不 hard fail |
| C8 frontmatter `description` 無尖括號 | str check |
| C9 SKILL.md body ≤300 行 | line count |
| C10 USER INTERACTION step 必標 `[USER INTERACTION]` | regex |
| C11 LOOP step 有 budget + exit condition | regex 找 `LOOP ... max N` |
| C12 IF 有對應 ELSE / END IF | structural check |
| C13 SOP SSOT — references / assets / scripts 內無 step 流程 | grep `Step \d+` / `Phase \d+` / 連續 ≥3 行 verb-whitelist 動詞 |
| C14 GOTO target 用 `#phase.step` literal | regex `GOTO\s+#\d+(\.\d+)*` |
| C15 禁止獨立 failure/fallback H2 section | top-level H2 whitelist + regex；failure branch 必留在 §2 SOP |
| C16 §1 REFERENCES YAML 可 parse 且 schema 合規 | extract fenced YAML + schema/path validation |
| C17 產出值的 step 必有 `$var =` SSA binding（per §23.1） | regex on step body |
| C18 引用 `$var` 必先有定義（use-before-def） | linear scan binding env |
| C19 跨 phase `$$var` 必由上游 phase `> produces:` 列出（per §24.2） | parse phase header blockquote |
| C20 health report：印 D/S/I 比例 + S-density + SCRIPT-CANDIDATE block 列表（per §26） | per-step verb-class derive |
| C21 §1 REFERENCES 之後、§2 SOP 之前必有 verb glossary blockquote（per §27） | regex `^>\s+\*\*Verb glossary` |
| C22 glossary 列出的 verb 與 SOP 內實際出現的 verb 一致（漏列 fail；多列 warn） | verb extraction + set diff |
| C23 health: report glossary-declared vs SOP-used verb diff | set comparison |
| C24 references/ 內無 quality gate rubric pattern（per §4.7.6） | filename `quality\|contract\|gate` ∧ body 含 ≥3 列 `\|\s*\w+_?\w*\s*\|` rule_id table → fail |
| C25 skill artifact self-contained（per §4.7.7） | scan `SKILL.md` / refs / reasoning for runtime gate/rubric/contract links to `research/`, `.cursor/plans/`, `*-outcome-eval.md`, external `eval.md` / `proposal.md`; stable hubs such as `aibdd-core::` allowed |

驗證 script 落 `.specify/extensions/aibdd/scripts/python/validate_skill_spec.py`。

### 嚴重度

- **HARD**：C1–C5, C8, C13–C17, C19
- **SOFT WARN**：C6, C7, C9–C12, C18
- **REPORT only**（無 fail，純資訊）：C20

---

## §16 遷移計畫

### 16.1 優先序

依「規章違反程度」排序，最違反的先遷：

| Tier | Skill 候選 | 主要違反 |
|---|---|---|
| T1（最違反） | aibdd-form-feature-spec / speckit-aibdd-debug | SOP 散在多 section、Hard rules 區塊不在規章 |
| T2 | speckit-implement / speckit-tasks | inline 大段 dispatch table（規範可能仍合理保留），但 SOP 散 |
| T3 | aibdd-discovery / aibdd-red v2 / aibdd-green / aibdd-refactor | 已接近規章；補 §1 REFERENCES YAML 即可 |
| T4 | aibdd-core / aibdd-form-* 其他 | 多為 rule SSOT；少 SOP，遷移成本低 |

### 16.2 每 skill 遷移步驟

1. READ 該 skill SKILL.md
2. CLASSIFY 每段 → SOP step / global ref / step-local ref / template / 動機 / 教學
3. EXTRACT 非 SOP 段 → references/ 或 assets/
4. REWRITE SKILL.md 為 §1 REFERENCES + §2 SOP，並把 failure branches 併入對應 SOP step
5. RUN `validate-skill-spec.py`
6. 跑該 skill 一次（dogfooding）— 驗證 program counter 真的能 resume

### 16.3 不必一次全遷

- 可逐 skill 漸進
- 但**新增 skill 一律必符規章**
- T1 / T2 應在 1 個 sprint 內遷完（避免長期分歧）

---

## §17 遷移範例 — `aibdd-form-feature-spec` BEFORE / AFTER 對照

### BEFORE（current SKILL.md 結構）

```
## §1 角色
Formulation skill。綁定 DSL = Gherkin (.feature)。被多個 Planner DELEGATE：
- aibdd-discovery：rule-only mode
- aibdd-form-bdd-analysis：example-fill mode

## §2 入口契約
| 項目 | 內容 |
| ... | ... |

## §3 Formulate SOP
1. 讀取 format reference
2. 檔名守門（兩層）
   ...
3. 依 mode 執行
   ...

## §4 DSL 最佳實踐
### Gherkin 關鍵字
一律使用英文：Feature / Rule / ...
### Rule 命名
- 前綴分類：前置（狀態）/ ...

## §5 匯報

## §6 參考
```

### AFTER（規章後）

```markdown
---
name: aibdd-form-feature-spec
description: Translate 推理包 to Gherkin .feature; binds DSL = Gherkin; called by planners with mode payload. TRIGGER when DELEGATEd by aibdd-discovery (rule-only) / aibdd-form-bdd-analysis (example-fill).
metadata:
  user-invocable: false
  source: plugin extension
---

# aibdd-form-feature-spec

Translate 推理包 to Gherkin .feature; binds DSL = Gherkin; called by planners with mode payload.

## §1 REFERENCES

```yaml
references:
  - path: references/format-reference.md
    purpose: Gherkin 標準語法權威 SSOT
  - path: references/patterns/rule-only-format.md
    purpose: rule-only mode pattern
  - path: references/patterns/bdd-examples.md
    purpose: example-fill mode pattern
  - path: references/role-and-contract.md
    purpose: 角色 + 入口契約定義（從原 §1+§2 抽出）
  - path: aibdd-core::feature-granularity.md
    purpose: anti-pattern token 偵測
  - path: ${BDD_CONSTITUTION_PATH}
    purpose: §5.1 filename axes
  - path: aibdd-core::authentication-binding.md
    purpose: actor key authentication 慣例
```

## §2 SOP

### Phase 1 — VALIDATE 入口

1. READ caller payload
2. ASSERT payload 含 `mode` ∈ {rule-only, example-fill}
3. ASSERT payload 含 `target_path`
4. VALIDATE target_path 經 [`references/filename-guard.md`](references/filename-guard.md) 兩層檢核
   4.1 IF anti-pattern token 命中: STOP, REPORT to caller, exit
   4.2 IF filename convention 違反: STOP, REPORT to caller, exit

### Phase 2 — FORMULATE per mode

1. IF mode == rule-only:
   1.1 EXPAND Feature header + Rule per [`references/patterns/rule-only-format.md`](references/patterns/rule-only-format.md)
   1.2 PRESERVE @ignore tag
   1.3 OMIT Background / Examples
2. ELSE IF mode == example-fill:
   2.1 FILL Examples per [`references/patterns/bdd-examples.md`](references/patterns/bdd-examples.md)
   2.2 REMOVE @ignore tag

### Phase 3 — INLINE CiC

1. INLINE 推理包便條紙至對應位置（`# CiC(<KIND>): ...`）

### Phase 4 — WRITE artifact

1. WRITE target_path

### Phase 5 — REPORT

1. EMIT to caller (plain language):
   "Form Feature Spec 完成。產出 N 個 .feature 檔案。{若有便條紙則加：尚有 N 張便條紙待釐清}"

## §3 CROSS-REFERENCES

- `aibdd-discovery` — 上游 caller (rule-only mode)
- `aibdd-form-bdd-analysis` — 上游 caller (example-fill mode)
- `aibdd-core::feature-granularity.md` — anti-pattern SSOT
```

差別：

- SKILL.md body ~60 行（vs BEFORE ~110 行）
- §4 DSL 最佳實踐整段抽到 R1 format-reference.md
- §1 角色 + §2 入口契約合併抽到 R4 role-and-contract.md
- 每個 step 一個 verb，imperative
- branching 拆 sub-step
- 失敗分支與 rollback 都在觸發它們的 SOP step 附近，program counter 不必跳到附錄
- 程式碼可從 #1.4 / #2.1.1 直接定位

---

## §18 Open Questions（待 user 拍板）

1. **Q1 verb whitelist 中英文**：採全英文 capital（READ / WRITE / ...）或中文（讀 / 寫 / ...）？建議全英文 — 降低中文歧義（「讀」可能是 "study"，「寫」可能是 "compose"）；step body 後續描述用中文無妨。
2. **Q2 §1 REFERENCES YAML 強制存在**：即使 skill 不 LOAD 任何 reference 也要留 `references: []`？建議：強制存在 — 維持 layout 一致性且可 script parse。
3. **Q3 verb 中 READ vs LOAD 區分**：建議 `READ` = 讀檔；`LOAD` = 把檔案 parsed → in-memory dict（譬如 LOAD axes as readonly dict）。兩者區別有意義 — 都加。
4. **Q4 failure handling 位置**：已拍板為「一律併入 §2 SOP」，不得另設 top-level failure/fallback section。
5. **Q5 自動驗證 script 何時開發**：可隨第一個 T1 遷移做為 PoC；不必先驗證所有 skill。
6. **Q6 規章演化**：本規章本身是否要寫進 `aibdd-core/references/skill-spec.md` 給所有 plugin maintainer 參考？建議：是，在 v1 發布時同步落地。
7. **Q7 description 字數**：1024 hard cap 是 plugin validator 限制；建議 v1 降到 ≤500 給未來 trigger 補充留 buffer。同意嗎？
8. **Q8 SKILL.md body 行數**：300 軟上限是估計值；T2 / T1 skill 改完看實際數字再 calibrate。

---

## §19 Migration Wave 0 — 立刻可做的 quick wins

不必等規章 v1 發布，這些可立即套：

1. 所有 SKILL.md 第一個 section 名 `## §1 REFERENCES`（5 分鐘 / skill）
2. SOP section 命名 `## §2 SOP`（同上）
3. Phase header 統一 `### Phase N — <name>`（10 分鐘 / skill）
4. step body 加 verb prefix（30 分鐘 / skill — 改寫量大）
5. branching 拆 sub-step（30 分鐘 / skill）
6. inline template / 大表 / code block ≥10 行 → 抽 references（最耗時，1-2 hr / skill）

T3 / T4 skill 在 wave 0 可能就 90% 規章合格；T1 / T2 需要 wave 1+ 完整重構。

---

## §20 與既有 SpecFormula 紀律的合流點

本規章與已存在的紀律必須**互不矛盾**：

| 既有紀律 | 規章 mapping |
|---|---|
| `spec-ssot-principle` | §11 Cross-skill 共用紀律的 SSOT 強制 = SSOT principle 在 SKILL.md 的具體化 |
| `aibdd-skill-rca` | 規章違反 → aibdd-skill-rca 的 input；可在 RCA references 加一條「先檢規章合規」 |
| `/aibdd-reinforce` work-mode §3.2 四準則 + 第 5 條 Test Effectiveness | 規章是 Just Necessary / High Cohesive 的具體化；違反規章 = 違反這兩條準則 |
| `/aibdd-reinforce` §10 PF-CHARTER-DS | 同精神 — 都是「結構強迫深度」 |
| `/aibdd-skill-test` L0 靜態完整性檢查 | §15 自動驗證 checklist 可整合進 L0 |

規章不是新增第六條紀律，而是把既有紀律**結構化到 SKILL.md layout**。

---

## §21 Changelog

| 版本 | 日期 | 變更 |
|---|---|---|
| v0 | 2026-04-28 | 初版草案。使用者提 3 條核心原則（SOP 直寫、抽 reference、巢狀編號），AI 草擬 18 條補充規範 |
| v1 | 2026-04-29 | 根據 [`DESIGN_PURPOSE.md`](../DESIGN_PURPOSE.md) 升級為 program-like SKILL.md：(a) §5 verb whitelist 重組為 D/S/I 三閉集；(b) 新增 §23 SSA binding grammar；(c) 新增 §24 `$` / `$$` scope sigils + phase `> produces:` 契約；(d) 新增 §25 BRANCH 顯式控制流 + `←` 寫入箭頭；(e) 新增 §26 cognitive-type 自動推導 + SCRIPT-CANDIDATE / S-density audit；(f) §15 加 C17–C20 |
| v1.1 | 2026-04-29 | 新增 §27 verb glossary blockquote 強制：每支 SKILL.md 在 §1 之後 §2 之前必含 self-contained verb cheatsheet（用到的 verb + 1 行語意 + notation reminder）。理由：reading AI 第一次接觸 SKILL.md 不需 round trip 到 verb-whitelist.md 才看懂 SOP。§15 加 C21–C23。 |

---

## §27 Notation Block — canonical, self-contained, script-injected

### 27.1 為什麼

打開任何一支 SKILL.md，第一眼看到 `$x = CLASSIFY $err` 就要懂 D/S/I、SSA、`←`、`BRANCH`、`GOTO #N.M`。
若 SKILL.md 只說「per AIBDD 規章 §5」這種 external pointer —— reading AI 不一定會去 LOAD，等於沒講。

正解：**SKILL.md 自帶完整 program 說明書**，且**內容跨所有 skill canonical 一致**（避免 N 份 hand-written copy drift）。

### 27.2 SSOT + 注入設計

- **SSOT**：[`verb-cheatsheet.md`](verb-cheatsheet.md)（slim 版，從 [`verb-whitelist.md`](verb-whitelist.md) 抽 1-line meaning + notation block）
- **注入工具**：[`scripts/python/render_verb_glossary.py`](../scripts/python/render_verb_glossary.py)
- **markers**：SKILL.md 內 `<!-- VERB-GLOSSARY:BEGIN ... -->` / `<!-- VERB-GLOSSARY:END -->` 兩行包夾注入區
- **更新流程**：edit `verb-cheatsheet.md` ONCE → 對每支 skill 重跑 `render_verb_glossary.py` → 全部 SKILL.md sync

### 27.3 強制位置

H1 title + 一行 role sentence 之後、`## §1 REFERENCES` 之前：

```
# /skill-name

<one-line imperative role>

<!-- VERB-GLOSSARY:BEGIN — auto-rendered ...; do not hand-edit -->
> [canonical notation + verb table]
<!-- VERB-GLOSSARY:END -->

## §1 REFERENCES
```

**為什麼放這裡**：reader 從上往下讀 → role（這 skill 做啥）→ notation（這份檔怎麼讀）→ refs / SOP。

### 27.4 強制內容（canonical SSOT；單一 cheatsheet 跨所有 skill identical）

cheatsheet 結構固定（per `verb-cheatsheet.md`）：

1. **Block 標題**：`**Program-like SKILL.md — self-contained notation**`
2. **3 個 cognitive type 定義**：D / S / I 各 1 行
3. **SSA 規則**：`$x = VERB args` / `$x` vs `$$x` / `> produces:` 契約
4. **Side-effect 箭頭**：`VERB target ← $payload`
5. **控制流**：`BRANCH $check ? then : else` / `GOTO #N.M`
6. **完整 canonical verb 表**：所有合法 verb（**不**只列本 skill 用到的；canonical = identical across all skills）

**Hard rules**：
- Block 內**不得**出現「per X §Y」「詳見 Z」這類 external pointer
- Block 內**不得 hand-edit** —— 改要改 cheatsheet 後重跑 script
- 不再做「本 skill 用到的 verb 子集」 —— canonical 全表注入，避免維護負擔與 drift

### 27.5 為什麼選 canonical 全表而非 per-skill 子集

| 維度 | per-skill 子集（舊 v1.1） | canonical 全表（v1.2） |
|---|---|---|
| skill author 維護 | 每次新增 verb 都要更新所有 SKILL.md | 改 cheatsheet 一處 + script |
| Drift 風險 | 高（30+ skill × 各自子集） | 零（單一 SSOT） |
| 子集的「視覺提示」 | 有（看了知道本 skill 用啥） | 失去 —— 但 validator C22 audit 會印「本 skill used vs canonical」diff |
| Block 大小 | 16 行 | ~50 行 |
| Reading AI 完整性 | 缺漏的 verb 看不懂 | 任何 verb 都有定義 |

### 27.6 驗證 (C21–C24)

- **C21 (HARD)**：H1 與 `## §1 REFERENCES` 之間必有 `<!-- VERB-GLOSSARY:BEGIN -->` / `<!-- VERB-GLOSSARY:END -->` markers
- **C22 (SOFT)**：SOP 內出現 verb 不在 canonical cheatsheet → warn（typo 或該加進 cheatsheet 的新 verb）
- **C23 (HARD)**：markers 之間出現 external pointer pattern → fail
- **C24 (HARD)**：markers 之間內容必 byte-match 對 cheatsheet 渲染後結果 → 偵測 hand-edit drift

驗證失敗時的修復：跑 `render_verb_glossary.py <skill_dir>` 重新注入。

### 27.7 為什麼是 blockquote 不是新 section

SKILL.md §1 layout 限制只有 4 個 top-level section。notation 屬於「program preamble」 —— blockquote 視覺上明顯是 metadata，不獨立成章。

---

## §28 Reasoning Artifacts — `reasoning/` first-class semantic micro-protocol

### 28.1 目的

`reasoning/` 是 semantic reasoning 的 first-class artifact layer。
它不取代 `SKILL.md`，也不取代 `references/`：

- `SKILL.md` 仍是 skill-level execution flow 的 SSOT。
- `reasoning/` 是 RP-local semantic micro-protocol 的 SSOT。
- `references/` 仍只放 declarative knowledge / schema / lookup / rule。
- `assets/` 仍只放 output template / boilerplate / binary。

換句話說，`SKILL.md` 說「何時跑哪個 reasoning phase、如何 pass materials」；
`reasoning/` 說「該 reasoning phase 內部如何取材、推理、分類、reduce」。

### 28.2 目錄結構

```text
<skill>/
  reasoning/
    <reasoning-context>/
      00-<reasoning-phase-name>.md
      01-<reasoning-phase-name>.md
      02-<polymorphic-reasoning-phase-name>/
        POLYMORPHISM.md
        A-<variant-reasoning-phase-name>.md
        B-<variant-reasoning-phase-name>.md
```

每個 `reasoning/**/*.md` 檔案稱為 **Reasoning Phase**，簡稱 **RP**。

### 28.3 RP YAML frontmatter

每個 RP 必須以 YAML frontmatter 起始，且在第一個 H1 之前：

```yaml
---
rp_type: reasoning_phase
id: <context>.<slot>-<reasoning-phase-name>
context: <reasoning-context>
slot: "<00|01|02|...>"
name: <Reasoning Phase Name>
variant: none
consumes:
  - name: <upstream material bundle / axis name>
    kind: material_bundle | required_axis | derived_axis | config | reference
    source: caller | skill_global | upstream_rp | reference | filesystem
    required: true
produces:
  - name: <derived axis / reducer output name>
    kind: material_bundle | derived_axis | decision | cic
    terminal: false
downstream:
  - <context>.<slot-or-rp-id>
---
```

### 28.4 RP 固定 sections

RP body 必須包含以下 5 個 H2 sections，順序固定：

~~~markdown
## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: <AxisName>
    source:
      kind: caller | skill_global | upstream_rp | reference | filesystem
      path: <optional path or RP id>
    granularity: <one precise unit>
    required_fields:
      - <field>
    optional_fields:
      - <field>
    completeness_check:
      rule: <machine-readable or prose invariant>
      on_missing: STOP | ASK | fallback | mark_unknown | cic
    examples:
      positive:
        - <what counts as this axis>
      negative:
        - <what does not count as this axis>
```

### 1.2 Search SOP

## 2. Modeling Element Definition

## 3. Reasoning SOP

## 4. Material Reducer SOP
~~~

`Required Axis` 必須寫成 YAML，因為 graph / reasoning eval scripts 會解析它。
若 RP frontmatter 的 `consumes[*].kind == required_axis`，同名 axis 必須出現在 `required_axis` YAML 中。

### 28.4.1 Modeling Element Definition schema

`Modeling Element Definition` 只定義 RP 完成後會出現在 Material Reducer output bundle 的**模型元素**，且必須用 YAML 撰寫。正式 schema 見 `references/modeling-element-definition-schema.md`。

```yaml
modeling_element_definition:
  output_model: <output-axis-or-bundle>
  element_rules:
    element_vs_field:
      element: <可被獨立引用 / 追蹤 / 修正 / 下游消費的單位>
      field: <只能隸屬於某個 element 的屬性>
  elements:
    <ElementName>:
      role: <domain-native purpose>
      fields:
        <field_name>: <type or nested element ref>
      invariants:
        - <semantic invariant>
```

**必須：**
- 使用 domain 既有名詞；若概念已叫 Actor，就直接叫 `Actor`，不得另造 `BehaviorRole` 之類 wrapper。
- 定義模型元素的 granularity / role / boundary，而不是描述產生它的判斷過程。
- 把屬性放在 parent element 的 `fields` 下；例如 `ActorRef` 應是 `Actor.fields.ref`，不是獨立 element。能獨立被引用 / 追蹤 / 修正 / 下游消費者才是 element，否則就是 field。
- 每個分類項都能在 `produces` 或 Material Reducer output 中找到承載位置。
- Reasoning SOP 最終必須透過 `CLASSIFY` verb 將 material 放入 `modeling_element_definition.elements` 的某個元素。

**禁止：**
- 放入中間推理變數，例如 `ActorLegalityVerdict`、`ActionGranularityVerdict`、`FooCheck`、`BarScore`、`TempCandidate`，除非這些就是 RP 的正式輸出。
- 把 render / format / projection concern 放進分類定義，除非該 RP 的輸出本身就是 render / format artifact。
- 用新名詞包舊概念，迫使讀者在 domain term 與 invented term 之間做翻譯。
- 在 YAML schema 中加入 `source_of_truth` 或 `classify_rule`。這些是 SOP / 規章層語意，不是 model field。

中間判斷要寫在 `## 3. Reasoning SOP`；輸出成形要寫在 `## 4. Material Reducer SOP`。

### 28.5 ASK in RP

RP SOP 允許 I verb / `ASK`。
若推理途中發現 information gap，RP 可以打開 clarification gate。
但 ASK 的結果必須進 Material Reducer output，讓下游 RP 能看到此 ambiguity 是如何被補上的。Material Reducer SOP 是 RP 唯一交棒契約；不得另設 `Completion Contract` 作為第二份輸出真相來源。

### 28.6 Polymorphism

Polymorphic reasoning slot 使用子目錄 + `POLYMORPHISM.md`。
`POLYMORPHISM.md` 是 slot interface，必須宣告 shared consumes / produces contract、selector、variants。

```yaml
---
rp_type: polymorphism
id: <context>.<slot>-<polymorphic-slot>
context: <reasoning-context>
slot: "<NN>"
name: <slot name>
selector:
  param: <variant-selector-name>
  source: caller | skill_global | upstream_rp
consumes:
  - name: <shared-input>
    kind: material_bundle | required_axis | derived_axis | config | reference
    source: caller | skill_global | upstream_rp | reference | filesystem
    required: true
produces:
  - name: <shared-output>
    kind: material_bundle | derived_axis | decision | cic
variants:
  - id: <variant-id>
    path: <variant-file.md>
    when: <selector predicate>
downstream:
  - <rp-id>
---
```

Variant files may use different Reasoning SOPs, but must satisfy the shared contract.
Variant stack is selected by `SKILL.md`; RP files only declare the contract and lazy-load paths.

### 28.7 SKILL.md relationship

`reasoning/` is not listed in `## §1 REFERENCES`.
No `## §1.5 REASONING INDEX` is added.
`SKILL.md` cites RP files inline in SOP steps:

```markdown
1. `$rp1` = THINK per [`reasoning/default/01-classify-axis.md`](reasoning/default/01-classify-axis.md), input=`$rp0.material_bundle`
```

---

## §29 Reasoning Graph Eval

Every generated skill with `reasoning/` must run:

```text
python3 scripts/python/eval_reasoning_graph.py <skill_dir>
```

The script parses RP YAML frontmatter and Required Axis YAML, builds a bipartite derivation graph, and writes:

```text
<skill_dir>/.quality/reasoning-derivation-graph.mmd
<skill_dir>/.quality/reasoning-graph-report.json
```

Mermaid is the only graph language. If Mermaid CLI is available, SVG may be produced as an additional artifact.
Graph eval is a hard quality gate: dangling required inputs, missing variant paths, invalid Required Axis YAML, or invalid downstream ids fail the generated skill.

---

## §30 Reasoning Eval

Every generated skill with `reasoning/` must run:

```text
python3 scripts/python/eval_reasoning_quality.py <skill_dir>
```

The script checks each `rp_type: reasoning_phase` file and writes:

```text
<skill_dir>/.quality/reasoning-eval-report.json
```

Reasoning Eval checks:

1. required RP sections exist;
2. reasoning-density is reported as health metric;
3. reducer-completeness is a hard gate;
4. ASK results are traceable into reducer output;
5. chain-of-thought output patterns are rejected.

`reasoning-density` is not a hard fail. It is a health signal:

- low S-density: RP may mostly be deterministic sourcing / rendering, consider script extraction;
- high S-density: RP may need to split into smaller RPs.

---

## §23 SSA Binding Grammar — `$var = VERB args`

### 23.1 強制：產出值的 step 必有 OUT binding

任何「會產出可被下游 step 引用的值」的 step，**必以 `$var = ` 開頭**：

```markdown
1. $cfg   = READ .specify/memory/bdd-constitution.md
2. $axes  = PARSE $cfg, schema=refs/axes.md
3. $kind  = CLASSIFY $err, refs=[a, b, c]
4. $reply = ASK "skill name?"
```

不產出值的 step（pure side-effect）不加 `$var =`：

```markdown
5. ASSERT $axes.todo == []
6. WRITE ${FEATURE_DIR}/tasks.md ← $rendered
7. CREATE $skill_dir/references/
8. EMIT $summary to user
9. STOP
```

### 23.2 為什麼

- **Data flow 顯性化** —— 任何 step 的 input 都是「之前某 step 的 output」，不是模糊「上下文」
- **Use-before-def 可機械檢查** —— validator 從上往下掃 binding，發現 step 引用未定義 `$var` 即報錯
- **Dead binding 可機械檢查** —— 永遠沒被引用的 `$var` 是 dead code
- **取名免費 review** —— 取不出名 = step 在做什麼？該拆 / 該砍

### 23.3 命名規範

- `$var`：snake_case 英文；簡短（≤20 chars）；具語意（`$cfg` 而非 `$x`）
- 關鍵字 / 保留字（`$null` / `$true` / `$false` / `$undefined`）禁用
- 同 phase 內 `$var` 不可重綁（SSA 原則）；需要新值用新名字（`$cfg2` / `$cfg_validated`）

### 23.4 引用語法

step body 內引用 `$var`，validator 認 `\$\$?[a-z_][a-z0-9_]*` regex：

```markdown
3. $patch = EDIT $err.file ← $ctx, fix=$err.message
              ↑          ↑                   ↑
              新 binding  引用既有            引用既有
```

允許 dot-access：`$err.file` / `$$config.path`。

---

## §24 Variable Scope Sigils — `$` vs `$$`

### 24.1 兩級 scope

| Sigil | Scope | 用途 |
|---|---|---|
| `$var` | **phase-local** | 中間值；跑完當前 phase 即 GC |
| `$$var` | **skill-global** | 跨 phase 流的狀態；intake 結果 / 最終 artifact path / 累計錯誤集 |

### 24.2 Phase 輸出契約 — `> produces:` 行

每個 phase 在 header 下方用 markdown blockquote 宣告它對外輸出的 `$$var`：

```markdown
### Phase 1 — INTAKE
> produces: `$$name`, `$$desc`, `$$lang`, `$$phases`

1. $$name = ASK "skill name?"
2. $$desc = ASK "description?"
...
```

無對外輸出的 phase 可省 `> produces:` 行。

### 24.3 紀律

- `$$var` 在某 phase 第一次被綁 → 該 phase header 必有 `produces:` 列入
- 跨 phase 引用 `$$var` 時，validator 檢查上游 phase `produces:` 有列
- `$$` 數量是 skill 健康指標：太多（>8）= phase 切太細或耦合太緊；太少（<2）多 phase skill = 可能該合併
- **禁止**在 step body 內把 `$var` 升級為 `$$var`（重綁不同 sigil 是 anti-pattern）；要跨 phase 從一開始就宣告 `$$`

---

## §25 Control Flow & Side-Effect Grammar

### 25.1 寫入箭頭 `←` vs 讀出 `=`

對稱地表示資料流向：

| 形式 | 意思 | 範例 |
|---|---|---|
| `$var = VERB args` | 讀出（產出 binding） | `$cfg = READ ./constitution` |
| `VERB target ← $payload` | 寫入（side effect 至 target） | `WRITE ./out.md ← $rendered` |
| `VERB args`（無 `=` 無 `←`） | 純 side effect 無資料流 | `CREATE $dir`, `STOP`, `EMIT $x to user` |

### 25.2 BRANCH —— 顯式控制流動詞

複雜分支用 `BRANCH` 而非 `IF`，吃 `$check` 或 `$kind` binding：

**二元 ternary 形式**：

```markdown
6. BRANCH $clean ? GOTO #4.1 : GOTO #2.1
```

**多 arm 形式**（縮排清單，每行一 arm）：

```markdown
3. BRANCH $result
   ok          → GOTO #4.4
   behind      → TRIGGER `git pull --rebase`; GOTO #1.1
   hook-failed → GOTO #1.1
   other       → STOP, EMIT $push_out to user
```

**簡單 in-place 條件用 IF/ELSE sub-step**（per §7.1）—— `IF` 仍保留給「不需 GOTO 出去、就在 sub-step 處理完」的場景：

```markdown
5.3 IF $kind == "unsure":
    5.3.1 $reply = ASK "如何修正？"
    5.3.2 $kind  = DECIDE $reply
```

### 25.3 BRANCH 與 IF 的選擇

| 情境 | 用 |
|---|---|
| 分支 ≥3 arm | BRANCH |
| 分支需要 GOTO 跳出當前 phase | BRANCH |
| 分支 body 是單一 STOP / RETURN | BRANCH |
| 分支 body 是 2-3 個 sub-step | IF/ELSE |
| 分支 body 是 LOOP 內的 continue/break | IF |

---

## §26 Cognitive-Type Detection & SCRIPT-CANDIDATE Audit

### 26.1 Type 推導 —— 不靠 source tag

每個 step 的 cognitive type **完全從 verb 名字推得**：

- verb ∈ §5.1 D-set → step is **D**
- verb ∈ §5.2 S-set → step is **S**
- verb ∈ §5.3 I-set → step is **I**

**作者永遠不寫 `[D]/[S]/[I]` 標記。** validator audit 時自動推。

### 26.2 SCRIPT-CANDIDATE block —— 連續 ≥3 D-step

Validator 掃 §2 SOP，找連續 ≥3 個 D-step（不被 S 或 I 打斷）的區段，標為 SCRIPT-CANDIDATE。

範例 audit 輸出：

```
SCRIPT-CANDIDATE blocks (consecutive ≥3 D-steps):
  #1.1..#1.6   (6 D-steps)  → suggest: scripts/python/run_pre_push_checks.py
  #2.1..#2.3   (3 D-steps)  → suggest: scripts/bash/biome_autofix.sh
  #3.1..#3.4   (4 D-steps)  → reuse: same as #1.1..#1.4 candidate
```

**不在 SKILL.md 源碼放 marker** —— 偵測純靠 verb-class，避免源碼噪音。

### 26.3 S-density health metric

```
S-density = (S-step count) / (D-step count + S-step count + I-step count)
```

- **Healthy 範圍**：5%–35%
- **<5%**：skill 幾乎沒 LLM 工作 —— 該整支抽 script，不需要 skill
- **>35%**：skill 過度依賴 LLM 推理 —— 該拆 sub-skill 或抽出更多 D 操作給 script

### 26.4 演化方向

每輪 dogfooding 應使 D-block 抽 script、`scripts/` 目錄變厚、`SKILL.md` body 變短、S-density 上升或穩定。詳見 [`DESIGN_PURPOSE.md`](../DESIGN_PURPOSE.md)。

---

## §22 待使用者批准

請審核：

1. §1 ~ §17 規章本身 — 各 section 嚴格度同意嗎？
2. §18 9 條 Open Questions — 想先拍板哪幾條？
3. §16 遷移計畫 — T1 / T2 / T3 / T4 分層同意嗎？要先遷哪支？
4. §19 wave 0 quick wins — 同意先把所有 skill 改 section 名 + Phase header 統一這種低成本動作？

批准後 → 進 Clarify Loop（剩餘 Open Questions 一題一題回） → 全題通過 → 進 Migration Wave 1 開始遷 T1。
