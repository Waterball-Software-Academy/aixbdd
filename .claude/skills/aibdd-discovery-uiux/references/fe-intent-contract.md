# FE Intent Contract

> 純 declarative — 規範 `raw_idea` 在本 skill 內如何被收斂成 `fe_intent_bundle`，以及下游 RP 怎麼消費。**不含**任何步驟流程；步驟流程在 SKILL.md Phase 2 與 `reasoning/discovery-uiux/00-fe-intent-sourcing.md`。

---

## §1 fe_intent_bundle schema

`fe_intent_bundle` 是 raw idea sourcing 的唯一結構化產物，貫穿 02 / 03 / 04 三支 RP。

| 欄位 | 型別 | 用途 |
|---|---|---|
| `raw_idea` | string | caller payload verbatim；空字串視為「使用者未提供」 |
| `page_composition` | list<PageComposition> | 哪些 has-ui op 合在同一 page / 分頁 / 多步驟；下游 03 組裝 entry_trigger 用 |
| `navigation_topology` | enum | `dashboard` / `wizard` / `spa` / `multi-page` / `modal-overlay` / `unknown` |
| `state_axis_priority` | StateAxisPriority | error / empty / loading / partial 四類 state 的 must-cover / optional / skip |
| `scope_inclusion` | list<ScopeDecision> | 對每個 has-ui op 是否納入本輪 FE scope（intent=include / exclude / defer） |
| `actor_split` | list<ActorSplit> | 同一 BE actor 在 UX 上的人設細分（first-time / returning / suspended 等） |
| `ux_only_flows` | list<UXOnlyFlow> | raw idea 提到但 BE 無對應 op 的 UX-only userflow（filter / sort / client search） |
| `brand_seed` | BrandSeed \| null | 為下游 `/aibdd-uiux-design` 鋪錨點；可空 |
| `clarify_payload` | ClarifyPayload | Seam 0 待澄清題組（依 [`aibdd-discovery::references/turn-discipline.md`](aibdd-discovery::references/turn-discipline.md) clarify-loop schema） |

### §1.1 sub-element shapes

```yaml
PageComposition:
  composition_id: string
  be_op_ids: list<string>           # 此 page 上聚合的 BE op；可空（純 UX-only page）
  cardinality: enum                 # one-page | wizard-step | branch-by-entry | modal
  source: enum                      # raw-idea | be-default-1to1 | clarify-answer

StateAxisPriority:
  error:    enum   # must-cover | optional | skip
  empty:    enum
  loading:  enum
  partial:  enum

ScopeDecision:
  op_id: string
  decision: enum                    # include | exclude | defer
  reasoning: string                 # raw-idea quote 或 clarify answer trace；exclude/defer 必填

ActorSplit:
  be_actor: string                  # BE truth verbatim actor
  fe_personas: list<string>         # raw idea 提到的人設細分；至少 1 項
  source: enum                      # raw-idea | clarify-answer

UXOnlyFlow:
  flow_slug: string
  trigger_quote: string             # raw idea verbatim 引發此 flow 的詞彙
  proposed_anchor: string \| null   # 候選 accessible_name（可空，由 03 補）

BrandSeed:
  visual_direction: string          # editorial / brutalism / luxury / neutral / unknown
  density: enum                     # compact | comfortable | spacious | unknown
  raw_quote: string
```

> **invariant**：所有 element 的 `source` 欄位必為「raw idea verbatim」或「clarify-loop answer 的 question_id 引用」；禁出現 AI 自生內容。

---

## §2 Seam 0 question categories

下表是 Seam 0（FE Intent）唯一允許的提問軸；每題 id 形如 `int-Q<n>`，options 至少 2 項並包含 `OTHER`（per clarify-loop schema）。

| Category | 觸發條件 | 範例 concern | options 樣式 |
|---|---|---|---|
| `intent-empty` | `raw_idea` 為空或長度 ≤ 10 字元 | 「請描述本輪 FE boundary 的 UX 範疇」 | navigation_topology enum + OTHER |
| `intent-coverage-gap` | has-ui BE op ∉ raw_idea coverage | 「BE 有 `${op_id}` 但 raw idea 未提及；本輪是否納入 FE？」 | include / exclude / defer / OTHER |
| `intent-surplus` | raw_idea 含 UX 詞彙（wizard/stepper/modal/filter/sort）但 BE 無對應 op | 「raw idea 提到 `${term}`，BE 無對應 op」 | be-missing-op / ux-only-flow / out-of-scope / OTHER |
| `intent-composition` | has-ui ops ≥ 2 且 raw idea 未給組合線索 | 「`${op_id_list}` 要合在同 page 還是分開？」 | one-page / wizard / branch-by-entry / multi-page / OTHER |
| `intent-actor-split` | BE actor=end-user 但 raw idea 暗示分眾 | 「`end-user` 是否需要 split 成 first-time / returning？」 | yes-list-personas / no-single-persona / OTHER |
| `intent-state-priority` | raw idea 未提錯誤 / 空狀態 / loading 語氣 | 「error / empty / loading / partial 哪幾類必納入 must-cover？」 | multi-select 4 enum + OTHER |
| `intent-brand-seed` | 為下游 `/aibdd-uiux-design` 鋪錨點且 raw idea 無視覺指引 | 「視覺風格錨點？」 | editorial / brutalism / luxury / neutral / OTHER |

> **invariant**：Seam 0 提問內容只屬「FE 範疇收斂」軸；**禁出現** BE truth 修改類選項（黑名單詞彙見 [`be-gap-handling.md`](be-gap-handling.md) §3）。

---

## §3 Intent ↔ BE inventory alignment matrix

`alignment_matrix` 是 00-fe-intent-sourcing RP 的中間產物（不入 reducer output，僅供 02/03 consume 時可追溯）；每列形狀：

| 欄位 | 內容 |
|---|---|
| `be_op_id` | BE inventory op_id |
| `raw_idea_mentions` | raw idea 中出現的 verbatim 片段（可空 list） |
| `coverage` | `covered` / `gap` / `surplus`（surplus 反向：raw idea 提到但 BE 無 op） |
| `intent_decision` | `include` / `exclude` / `defer` / `ux-only-flow` / `unknown` |
| `clarify_question_id` | 若 decision == unknown 則為對應 Seam 0 question id |

`alignment_matrix` 必須能由 RP 00 直接 reduce 為 `scope_inclusion` + `ux_only_flows` 兩個欄位。

---

## §4 下游 RP 消費規約

| 下游 RP | 消費欄位 | 用途 |
|---|---|---|
| `01-be-sourcing` | （無 — 01 早於 00 完成 BE inventory） | — |
| `02-operation-classify` | `scope_inclusion` | classification tie-breaker：intent=exclude ∧ BE has-ui 訊號 → 強制 ambiguous（不得 silent has-ui） |
| `03-userflow-derive` | `page_composition` / `navigation_topology` / `ux_only_flows` / `actor_split` | userflow N:1 / 1:N 組裝；ux_only_flows 物化為 UATFlow with `be_op_id: null`；actor_split 寫進 UATFlow.actor |
| `04-fe-atomic-rules` | `state_axis_priority` | coverage matrix 權重；must-cover 缺漏才開 Seam C 題；skip 不入 gap |
| `06 / Phase 6 report` | `brand_seed` | 報告 pointer，供下游 `/aibdd-uiux-design` 參考 |

> **invariant**：下游 RP 不得「跳過 intent」直接套 BE truth；缺 intent 時必須在 reducer 標 `cic` 並回 Seam 0 重跑。

---

## §5 File-first 錨點

| 階段 | 錨檔 | Open Section | Resolved Section |
|---|---|---|---|
| Draft（Seam 0 fire 前） | `${PLAN_REPORTS_DIR}/discovery-uiux-intent.md` | `## Open Intent Questions` | — |
| Final（Seam 0 回答併入後） | 同上（覆寫） | （清空） | `## Resolved Intent Decisions` |

寫入內容必含：
- raw idea verbatim block（fenced quote）
- alignment_matrix table
- fe_intent_bundle YAML 摘要（不抄 raw idea 兩遍）
- Open / Resolved sections（依階段）

---

## §6 不在本檔範疇

- 「如何 fire Seam 0 / 何時 fire」 — 屬 SKILL.md Phase 2
- 「intent 與 BE 衝突如何 supplement」 — 屬 [`be-gap-handling.md`](be-gap-handling.md)
- 「has-ui / no-ui rubric」 — 屬 [`be-to-fe-mapping.md`](be-to-fe-mapping.md)
- 「Rule 句型 / verification mode」 — 屬 [`verification-semantics-presets.md`](verification-semantics-presets.md)
- 「coverage gap 細節規則」 — 屬 [`userflow-rule-coverage.md`](userflow-rule-coverage.md)
- 「`/aibdd-uiux-design` 視覺探索」 — 屬該 sibling skill，本檔只提供 brand_seed 鋪錨
