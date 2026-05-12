# Compliance Checklist — §15 of 規章

> 純 declarative checklist。Phase 7 invoke `validate_skill_spec.py` 跑 C1–C16 / C25；
> 若 skill 含 `reasoning/`，另跑 `eval_reasoning_graph.py` 與
> `eval_reasoning_quality.py` 作為 reasoning quality gate。

| Check | What | How to detect |
|---|---|---|
| **C1** frontmatter 合規 | 6 個 allowed top-level key 內 (`name` / `description` / `license` / `allowed-tools` / `metadata` / `compatibility`) | YAML parse + key whitelist |
| **C2** description ≤1024 chars 無尖括號 | string length + `<` / `>` substring | str check |
| **C3** 第一個 H2 是 `## §1 REFERENCES` | regex `^##\s+§1\s+REFERENCES\s*$` | regex |
| **C4** 第二個 H2 是 `## §2 SOP` | regex `^##\s+§2\s+SOP\s*$`（reference-hub 豁免）| regex |
| **C5** Phase header 字面 `### Phase N — <name>` | regex `^###\s+Phase\s+\d+\s+[—-]\s+\S+` | regex |
| **C6** 每 step 動詞在 verb whitelist | tokenize 第一個 word；compare against whitelist | per-line |
| **C7** step body ≤80 chars 一行（warn） | line length | warn-only |
| **C8** description 無尖括號（C2 dup but split for clarity） | str check | str check |
| **C9** SKILL.md body ≤300 行（不含 frontmatter） | line count - frontmatter range | count |
| **C10** USER INTERACTION step 必標 `[USER INTERACTION]` | grep `WAIT for user` / `ASK user` lines lacking `[USER INTERACTION]` | regex |
| **C11** LOOP step 標 budget + exit condition | grep `LOOP` lines for `max\s+\d+` 或 `until` | regex |
| **C12** IF 有對應 ELSE / END IF | structural balance check | parser |
| **C13** SOP SSOT — references / assets / scripts 內無 step flow | scan 各檔；命中 `Phase \d+` / `Step \d+` / 連續 ≥3 行 verb-whitelist 動詞 | grep + heuristic |
| **C14** GOTO target 用 `#phase.step` literal | regex `GOTO\s+#\d+(\.\d+)*\b`；非此格式即違反 | regex |
| **C15** 禁止獨立 failure/fallback H2 section | top-level H2 只能是 `§1 REFERENCES`、`§2 SOP`、optional `§3 CROSS-REFERENCES`；失敗分支必須寫回對應 SOP step | regex + H2 whitelist |
| **C16** §1 REFERENCES YAML 合規 | 唯一 fenced YAML block；root 為 `references`；每筆只含非空 `path` / `purpose`；skill-relative path 必須存在 | parser + path check |
| **C25** skill artifact self-contained | runtime gate / rubric / contract / oracle 不得引用 `research/`、`.cursor/plans/`、`*-outcome-eval.md`、外部 `eval.md` / `proposal.md`；必須 inline、放 skill 內部，或引用 stable hub like `aibdd-core::` | regex + path classifier |

## Reasoning Quality Gate

> 這些檢查不塞進 `validate_skill_spec.py` 的 SKILL.md layout validator；
> 它們由 dedicated reasoning eval scripts 執行。

| Check | What | How to detect |
|---|---|---|
| **R1** RP meta 合規 | `reasoning/**/*.md` frontmatter 必有 `rp_type`、`id`、`context`、`slot`、`name`、`consumes`、`produces`、`downstream` | `eval_reasoning_graph.py` YAML parse |
| **R2** Required Axis YAML 合規 | 每個 `rp_type: reasoning_phase` 必有 `### 1.1 Required Axis` YAML，且 `consumes[*].kind == required_axis` 的同名 axis 必須存在 | graph eval |
| **R3** RP graph 可組成 | consumed axis 有 caller/reference/source 或 upstream producer；downstream id 存在；polymorphism variant path 存在 | graph eval |
| **R4** Mermaid graph 可輸出 | 產生 `.quality/reasoning-derivation-graph.mmd`；只支援 Mermaid | graph eval |
| **R5** RP sections 完整 | 每個 reasoning phase 含五段固定 H2 sections | `eval_reasoning_quality.py` |
| **R6** Reducer completeness | Modeling Element Definition 的 elements 必須在 Reasoning SOP / Material Reducer SOP 中被處理，且在 reducer output 中可追蹤 | reasoning eval |
| **R7** ASK traceability | RP SOP 中的 ASK binding 必須出現在 reducer output | reasoning eval |
| **R8** No chain-of-thought output | RP 不得要求輸出 hidden chain-of-thought / full reasoning trace | reasoning eval |
| **R9** Modeling elements only | Modeling Element Definition 只列最終 reducer output 會承載的模型元素；中間 verdict / check / score / temp / render-format concern 必須移到 Reasoning SOP 或 Reducer | semantic review + template audit |
| **R10** Domain-native naming | Modeling Element Definition 優先使用 domain 既有名詞；禁止為已清楚存在的概念發明同義 wrapper（例如明明是 Actor 卻另造 BehaviorRole） | semantic review |
| **R11** Element-field separation | Modeling Element Definition 必須符合 `references/modeling-element-definition-schema.md`；元素屬性必須放在 `fields`，不得把 `ActorRef` / `StepLabel` / `BranchGuard` 這類 field 提升為獨立 element；`source_of_truth` / `classify_rule` 是 forbidden keys | reasoning eval + semantic review |

## 嚴重度分級

- **HARD FAIL**: C1, C2, C3, C4, C5, C8, C13, C14, C15, C16, C25, R1, R2, R3, R4, R5, R6, R7, R8 — 違反即 invalid skill
- **SOFT WARN**: C6, C7, C9, C10, C11, C12 — 違反需顯式正當化（譬如 step body 超過 80 chars 是合理 trade-off）
- **SEMANTIC HARD FAIL**: R9, R10, R11 — script 不一定能完整判定；reviewer / subagent 發現即視為 invalid reasoning design

## 與 SpecFormula 既有 lint 的關係

- `quick_validate.py`（user-scope `~/.claude/skills/skill-creator/`）已實作 C1, C2, C8 — 本 validator 補上 C3–C16
- `package_skill.py` 跑 quick_validate；本 validator 是補強層
