---
rp_type: reasoning_phase
id: discovery-uiux.00-fe-intent-sourcing
context: discovery-uiux
slot: "00"
name: FE Intent Sourcing
variant: none
consumes:
  - name: raw_idea
    kind: required_axis
    source: caller
    required: true
    note: caller payload 或 arguments.yml#LAST_USER_PROMPT；空字串視為「使用者未提供」
  - name: operation_inventory
    kind: material_bundle
    source: upstream_rp
    required: true
    note: 由 01-be-sourcing 產出；用來建 intent ↔ BE alignment matrix
  - name: be_truth_bundle
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: runtime_context
    kind: required_axis
    source: skill_global
    required: true
  - name: fe_intent_contract_ref
    kind: reference
    source: reference
    required: true
    path: ../../references/fe-intent-contract.md
produces:
  - name: fe_intent_bundle
    kind: derived_axis
    terminal: false
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: 7 類 intent question 任一非空時觸發 Seam 0 clarify-loop
downstream:
  - discovery-uiux.02-operation-classify
  - discovery-uiux.03-userflow-derive
  - discovery-uiux.04-fe-atomic-rules
---

# FE Intent Sourcing

從 caller payload 拿 raw idea，與上游 `01-be-sourcing` 產出的 `operation_inventory` 對齊，產生 `fe_intent_bundle`（page_composition / navigation_topology / state_axis_priority / scope_inclusion / actor_split / ux_only_flows / brand_seed）。模糊／缺口項轉成 Seam 0 clarify_payload；下游 02 / 03 / 04 必須消費此 bundle 才能正確收斂。

---

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: raw_idea
    source:
      kind: caller
      path: arguments.yml#LAST_USER_PROMPT or caller payload field `raw_idea`
    granularity: 單一字串（可為空）
    required_fields:
      - text
    completeness_check:
      rule: text is string（允許空字串；空字串強制觸發 intent-empty 題）
      on_missing: STOP
    examples:
      positive:
        - "做一個 dashboard 給 admin 看 token 用量；要有 filter 與 sort"
        - ""  # 空字串合法，但會強制 Seam 0 first question
      negative:
        - undefined / null（視同 axis missing → STOP）
  - name: runtime_context
    source:
      kind: skill_global
    granularity: FE TLB 全貌 + arguments.yml 解析後的執行設定
    required_fields:
      - TLB.id
      - TLB.role
      - PLAN_REPORTS_DIR
    completeness_check:
      rule: TLB.role == "frontend" ∧ PLAN_REPORTS_DIR 已展開
      on_missing: STOP
```

### 1.2 Search SOP

1. `$raw` = READ raw_idea text from caller payload
2. `$inventory` = READ operation_inventory.items from upstream RP 01
3. `$be_bundle` = READ be_truth_bundle from upstream RP 01
4. `$contract` = READ fe-intent-contract.md §1 schema + §2 question categories + §3 alignment matrix shape
5. ASSERT `$raw` is string（允許空）
6. ASSERT length(`$inventory`) ≥ 1（無 BE op → 應在 RP 01 已 STOP，本 RP 不重判）

---

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: fe_intent_bundle
  element_rules:
    element_vs_field:
      element: "下游 02 / 03 / 04 直接 LOOKUP 或 LOOP 的最小單位（PageComposition / ScopeDecision / ActorSplit / UXOnlyFlow 等），須能獨立追溯回 raw idea 或 clarify answer"
      field: "只能隸屬於 FEIntentBundle 或上述元素的屬性（visual_direction / density / coverage 等）"
  elements:
    FEIntentBundle:
      role: "raw idea 收斂後的 FE 範疇 SSOT；貫穿下游 02 / 03 / 04"
      fields:
        raw_idea: string
        navigation_topology: enum
        state_axis_priority: StateAxisPriority
        brand_seed: BrandSeed | null
        page_compositions: list<PageComposition>
        scope_decisions: list<ScopeDecision>
        actor_splits: list<ActorSplit>
        ux_only_flows: list<UXOnlyFlow>
      invariants:
        - "scope_decisions 條目數與 has-ui BE op 一一對應（已知 ambiguous 也須登一筆 unknown）"
        - "raw_idea 為空時 navigation_topology 必為 unknown 且 Seam 0 必含 intent-empty 題"
    PageComposition:
      role: "把多個 BE op 聚合在同一 FE page / wizard step 的單位"
      fields:
        composition_id: string
        be_op_ids: list<string>
        cardinality: enum                # one-page | wizard-step | branch-by-entry | modal
        source: enum                     # raw-idea | be-default-1to1 | clarify-answer
      invariants:
        - "cardinality=one-page → be_op_ids 至少 1 項；wizard-step 允許 1 項"
        - "source=clarify-answer → 必有對應 clarify question_id 在 IntentClarifyQuestion"
    ScopeDecision:
      role: "對單一 has-ui BE op 是否納入本輪 FE scope 的決議"
      fields:
        op_id: string
        decision: enum                   # include | exclude | defer | unknown
        reasoning: string
      invariants:
        - "decision ∈ {exclude, defer, unknown} → reasoning 必填"
        - "decision == unknown → 對應 IntentClarifyQuestion 必存在"
    ActorSplit:
      role: "BE actor 在 UX 上的人設細分"
      fields:
        be_actor: string
        fe_personas: list<string>
        source: enum                     # raw-idea | clarify-answer
      invariants:
        - "fe_personas 至少 1 項；同名於 be_actor 視為不 split（不得記錄）"
    UXOnlyFlow:
      role: "raw idea 提到但 BE 無對應 op 的 UX-only userflow"
      fields:
        flow_slug: string
        trigger_quote: string
        proposed_anchor: string | null
      invariants:
        - "trigger_quote 必為 raw idea verbatim 引用"
    StateAxisPriority:
      role: "error / empty / loading / partial 四類 state 的 must-cover / optional / skip 政策"
      fields:
        error: enum
        empty: enum
        loading: enum
        partial: enum
    BrandSeed:
      role: "為下游 /aibdd-uiux-design 提供視覺探索錨點"
      fields:
        visual_direction: string
        density: enum                    # compact | comfortable | spacious | unknown
        raw_quote: string
    IntentClarifyQuestion:
      role: "Seam 0 待澄清題目；下游 SKILL.md Phase 2 fire /clarify-loop 時消費"
      fields:
        id: string                       # int-Q<n>
        category: enum                   # 7 種 per fe-intent-contract.md §2
        concern: string
        options: list<ClarifyOption>
        recommendation: string
        rationale: string
      nested_fields:
        ClarifyOption:
          id: string                     # A | B | C | OTHER
          label: string
          impact: string
```

---

## 3. Reasoning SOP

1. `$alignment_matrix` = DERIVE per `$inventory.items`：每列 `{be_op_id, raw_idea_mentions, coverage, intent_decision, clarify_question_id}` per [`../../references/fe-intent-contract.md`](../../references/fe-intent-contract.md) §3
2. `$raw_idea_surplus` = MATCH `$raw` against UX 詞彙白名單 (`wizard` / `stepper` / `modal` / `filter` / `sort` / `search` / `dashboard` / `wizard` 等) 找出無 BE op 對應的片段
3. `$nav_topology` = CLASSIFY `$raw` into navigation_topology enum ∈ {dashboard, wizard, spa, multi-page, modal-overlay, unknown}；缺訊號 → unknown
4. `$state_priority_draft` = CLASSIFY `$raw` 對 error / empty / loading / partial 四軸的提及；缺訊號 → 預設 `{error: must-cover, empty: optional, loading: optional, partial: skip}` 並標 Seam 0 `intent-state-priority` 題
5. `$actor_signals` = DERIVE per `$be_bundle.activities` + `$raw`：對每個 BE actor 看 raw idea 是否暗示分眾（first-time / returning / suspended 等 lexical marker）
6. `$brand_signal` = CLASSIFY `$raw` for visual direction lexical markers（editorial / brutalism / luxury / neutral）；缺訊號 → null + Seam 0 `intent-brand-seed` 題
7. `$composition_draft` = THINK per has-ui op cluster：raw idea 是否明示組合（"在同一頁"／"分步驟"）；缺訊號 ∧ has-ui ops ≥ 2 → 標 Seam 0 `intent-composition` 題
8. `$clarify_questions` = DERIVE Seam 0 題組 ← 上述各步驟標記之 cic：
   - length(`$raw`) ≤ 10 → 必含 `intent-empty` 題（並 short-circuit 其他題：等使用者回答 intent-empty 後重跑 RP）
   - `$alignment_matrix.coverage == gap` 每筆 → 一道 `intent-coverage-gap` 題
   - `$raw_idea_surplus` 非空每筆 → 一道 `intent-surplus` 題
   - `$nav_topology == unknown` ∧ has-ui ops ≥ 2 → `intent-composition` 題
   - `$actor_signals.ambiguous` 每筆 → 一道 `intent-actor-split` 題
   - `$state_priority_draft.missing_signal == true` → `intent-state-priority` 題
   - `$brand_signal == null` → `intent-brand-seed` 題
9. ASSERT 每題 `category` ∈ fe-intent-contract.md §2 enum；options 至少 2 項並含 `OTHER`
10. ASSERT 任一 `intent-coverage-gap` 題對應的 `alignment_matrix.intent_decision == unknown`

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE fe_intent_bundle + clarify_payload：
   - `fe_intent_bundle.raw_idea` = `$raw`
   - `fe_intent_bundle.navigation_topology` = `$nav_topology`
   - `fe_intent_bundle.state_axis_priority` = `$state_priority_draft`
   - `fe_intent_bundle.brand_seed` = `$brand_signal`（可 null）
   - `fe_intent_bundle.page_compositions` = `$composition_draft.resolved`（unknown 留 placeholder，待 clarify 回填）
   - `fe_intent_bundle.scope_decisions` = derive from `$alignment_matrix.intent_decision`（unknown 視為待答）
   - `fe_intent_bundle.actor_splits` = `$actor_signals.resolved`
   - `fe_intent_bundle.ux_only_flows` = derive from `$raw_idea_surplus.resolved`
   - `clarify_payload.questions` = `$clarify_questions`
2. ASSERT `fe_intent_bundle.scope_decisions` length == count(has-ui ops in upstream classification candidate set)；若上游 02 尚未跑，length == count(`$inventory.items` 對應 BE has-ui 訊號最小子集)
3. ASSERT 每筆 `IntentClarifyQuestion` 都能在 `fe_intent_bundle` 找到對應 unknown 欄位（trace-back）
4. ASSERT `$reducer_output.fe_intent_bundle.ux_only_flows[*].trigger_quote` 均為 raw idea verbatim 子字串

Return:

```yaml
status: complete | needs_clarification | blocked
produces:
  fe_intent_bundle:
    raw_idea: string
    navigation_topology: enum
    state_axis_priority: {}
    brand_seed: {} | null
    page_compositions: []
    scope_decisions: []
    actor_splits: []
    ux_only_flows: []
  clarify_payload:
    questions: []   # Seam 0 — SKILL.md Phase 2 fire /clarify-loop
traceability:
  inputs:
    - raw_idea
    - operation_inventory
    - be_truth_bundle
    - runtime_context
    - fe_intent_contract_ref
  derived:
    - FEIntentBundle
    - PageComposition
    - ScopeDecision
    - ActorSplit
    - UXOnlyFlow
    - StateAxisPriority
    - BrandSeed
    - IntentClarifyQuestion
clarifications:
  - clarify_payload  # 非空 → SKILL.md Phase 2 §2 觸發 Seam 0 clarify-loop
```
