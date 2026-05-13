---
rp_type: reasoning_phase
id: discovery.05-atomic-rules
context: discovery
slot: "05"
name: Atomic Rules
variant: none
consumes:
  - name: activity_analyses
    kind: required_axis
    source: upstream_rp
    required: true
    cardinality: list
  - name: source_material_bundle
    kind: required_axis
    source: upstream_rp
    required: true
  - name: impact_scope
    kind: required_axis
    source: upstream_rp
    required: true
  - name: hallucination_detection_checklist
    kind: reference
    source: reference
    required: true
  - name: frontend_lens
    kind: required_axis
    source: upstream_rp
    required: false
    note: TLB.role=="frontend" 時 04b 產出非 null；否則為 null，本 RP 跳過 frontend 條款
produces:
  - name: atomic_rule_draft
    kind: derived_axis
    terminal: false
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: 偵測到規則層歧義（Class 2 — HTTP method 寫死 / hedging / 非 raw 提及之欄位）時輸出題目；無歧義則 questions 為空
downstream:
  - discovery.06-atomic-clarify
---

# Atomic Rules 草稿

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: activity_analyses
    source:
      kind: upstream_rp
      path: discovery.03-activity-analyze
    granularity: Activity model 清單（每個 modeled=true 的 uat_flow 一筆 activity_analysis）
    required_fields:
      - items
    optional_fields:
      - clarify_payload
    completeness_check:
      rule: Activity models 已通過 Seam A cic（clarify_payload.questions 為空）後，rule 才能依各 Action binding 切成 atomic
      on_missing: STOP
    examples:
      positive:
        - items 中每個 modeled=true item 的 Action 的 binds_feature 可追溯到 target feature 或 graph gap
      negative:
        - 還只有 raw idea 句子，沒有 items[].activity.nodes[]
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: raw idea + target boundary / function package traceability
    required_fields:
      - raw_idea
      - target_boundary
      - target_function_package
    optional_fields:
      - filename_axes
    completeness_check:
      rule: rule 草稿可追溯到 raw idea 或 impact scope pointer
      on_missing: ASK
    examples:
      positive:
        - rule candidate 有 raw idea quote 或 impact scope pointer
      negative:
        - rule 是憑空新增，無來源
  - name: impact_scope
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: flow / actor / state / operation / rule impacts
    required_fields:
      - impacts
    optional_fields:
      - blocking_gaps
    completeness_check:
      rule: Atomic Rules 只能消費 impact scope，不重新掃 truth 或建立第二份 sourcing
      on_missing: STOP
  - name: frontend_lens
    source:
      kind: upstream_rp
      path: discovery.04b-frontend-axes
    granularity: 全 boundary 一筆 frontend_lens（含 ui_verb_bindings + anchor_candidates + state_axes_hints）
    required_fields:
      - ui_verb_bindings
      - anchor_candidates
    optional_fields:
      - state_axes_hints
      - cic_marks
    completeness_check:
      rule: TLB.role=="frontend" 時必須非空；其他 role 時必須為 null
      on_missing: STOP
    gating: TLB.role=="frontend"
```

### 1.2 Search SOP

1. 先把這一輪要拿來切 atomic rules 的主軸讀進來：activity 分析、source material、impact scope、frontend lens（TLB.role=="frontend" 時非空，其他 role 為 null）。
   `$activity_analyses` = READ activity_analyses（只取 `modeled=true` 之 entries；caller 已確保 Seam A 已通過）
   `$bundle` = READ source_material_bundle
   `$impact_scope` = READ impact_scope
   `$frontend_lens` = READ frontend_lens（TLB.role=="frontend" 時為非空 struct；否則為 null）
   `$atomic_rule_definition` = READ `aibdd-core::atomic-rule-definition.md`

2. 再把所有 Action、raw idea、impact objects 拆成 action-scoped rule source units，讓後面每條 rule 都能回溯到具體來源。
   `$action_sources` = PARSE 跨所有 `$activity_analyses.items[*].activity.nodes[]`, `$bundle.raw_idea`, and `$impact_scope.impacts` into Action-scoped rule source units（每個 source unit 紀錄歸屬 `uat_flow_id`）

3. 先產出一版 atomic rule 草稿，後面再做原子性與歧義檢查。
   `$atomic_rule_draft` = DERIVE 根據 `$action_sources`、`$activity_analyses.items[*].activity`、`$impact_scope`、`$atomic_rule_definition` 組成的 atomic rules 草稿

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: atomic_rule_draft
  element_rules:
    element_vs_field:
      element: "會被後續 Feature formulation 獨立消費、追蹤或修正的規則單位"
      field: "只能隸屬於某個 rule draft / violation / CiC 的屬性"
  elements:
    AtomicRuleDraft:
      role: "依 Action / binds_feature 分組的 rule-only feature 草稿"
      fields:
        features: atomic_rule_feature[]
        rules_by_operation: object
        cic_marks: RuleCiC[]
        exit_status: complete | blocked
      conditional_fields:
        when_frontend_lens_present:    # 即 TLB.role == "frontend"
          each_rule_MUST_include:
            - ui_verb: "enum，取自 frontend-rule-axes §2 UI Verb Catalog"
            - anchor_hint:
                anchor_id: string
                role: "enum，取自 frontend-rule-axes §3 mapping；不得屬 §4.4 黑名單"
                accessible_name: "string，必須對齊 frontend_lens 對應 anchor 的 accessible_name（同義改寫禁止）"
      invariants:
        - "保留 @ignore"
        - "不得包含 Background / Scenario / Examples"
        - "每個 rule 必須有 action_id、source_quote 或 impact_pointer、condition、consequence、target_feature_path"
        - "TLB.role=='frontend' 時：每個 rule 必須額外帶 ui_verb 與 anchor_hint，且皆對齊 frontend_lens 中對應 action_id 的 binding；ui_verb 必須屬 frontend-rule-axes §2 catalog；anchor_hint.role 不得屬 §4.4 黑名單"
    RuleAtomicityViolation:
      role: "無法作為 atomic rule 直接交棒的規則缺陷"
      fields:
        kind: composite_rule | unclear_subject | unclear_condition | unclear_consequence | example_data_leak | multi_operation_aggregate
        action_id: string
        source_quote: string | null
        impact_pointer: string | null
        resolution: split | mark_cic | blocked
      invariants:
        - "必須在 reducer output 中表現為 split actions、violations 或 blocked status"
    RuleCiC:
      role: "規則切分、條件、例外、後果衝突未明時的 CiC 標記"
      fields:
        type: GAP | ASM | BDY | CON
        action_id: string
        message: string
      invariants:
        - "必須保留到 atomic_rule_draft.cic_marks"
```

## 3. Reasoning SOP

1. 先依 Action / binds_feature 分組，把 rule 草稿整理成真正可交棒的 `AtomicRuleDraft`。
   `$rules` = DERIVE 根據 `$action_sources` 與 `$activity_analyses.items[*].activity.nodes[]` 組成的 `AtomicRuleDraft`
   - 每條 rule 都必須保留 `action_id` 與其歸屬 `uat_flow_id`
   - 多張 Activity 若指向同一 `target_feature_path`，只有在它們仍屬同一個 operation surface 時才能合併
   - 同條件 + 同後果的重複 rules 要去重
   - 若同一 `target_feature_path` 同時承接多個可獨立命名／驗收／觸發的 operation trigger，必須標成 `multi_operation_aggregate`，不得直接交給 formulation

2. 若 `$frontend_lens` 非空（TLB.role=="frontend"），為每條 rule 繫結 `ui_verb` 與 `anchor_hint`；找不到對應 binding 時標 CiC，不自生 anchor。
   IF `$frontend_lens` is null: SKIP to step 3
   LOOP per `$rule` in `$rules.features[*].rules[*]`:
   2.1 `$binding` = LOOKUP `$frontend_lens.ui_verb_bindings` where `action_id == $rule.action_id`
   2.2 `$anchor`  = LOOKUP `$frontend_lens.anchor_candidates` where `anchor_id == $rule.action_id`
   2.3 IF `$binding` AND `$anchor` both found:
       - ATTACH `$rule.ui_verb` ← `$binding.ui_verb`
       - ATTACH `$rule.anchor_hint` ← `{anchor_id: $anchor.anchor_id, role: $anchor.role, accessible_name: $anchor.accessible_name}`
   2.4 ELSE:
       - APPEND `RuleCiC{type=GAP, action_id=$rule.action_id, message="rule action_id 在 frontend_lens 中無對應 binding/anchor；可能 04b 漏跑、action_id 不一致，或 activity action 屬 hand-off 不應寫成 frontend rule"}`
   END LOOP

3. 把不夠原子的地方顯式標成 violation，把仍未解決的規則歧義標成 `RuleCiC`。
   `$violations` = CLASSIFY `$rules` by `RuleAtomicityViolation`
   `$rule_cic` = DERIVE 根據 unresolved rule ambiguity 整理出的 `RuleCiC`

4. 先做交棒前的基本合法性檢查。
   ASSERT every `AtomicRuleDraft` item has action_id, source_quote or impact_pointer, condition, consequence, and target_feature_path
   ASSERT target_feature_path is under `${FEATURE_SPECS_DIR}` / target function package, not boundary root `features/`
   ASSERT no `AtomicRuleDraft` item contains example data, Background, Scenario, or Examples
   ASSERT 每個 `features[]` entry 在最終輸出中對應的 `target_feature_path` 唯一
   ASSERT 每個 `features[]` entry 只對應一個單一 operation surface
   IF `$frontend_lens` is non-null:
   4.1 ASSERT every rule item 帶 `ui_verb` 與 `anchor_hint`（步驟 2 已繫結；遺漏者必須已在 cic_marks 中）
   4.2 ASSERT every rule.anchor_hint.role 不屬 frontend-rule-axes §4.4 黑名單（generic / div / span / presentation / none）
   4.3 ASSERT every rule.ui_verb 屬 frontend-rule-axes §2 UI Verb Catalog enum

5. 對規則草稿做規則層歧義檢查，專門抓 raw 沒說、但 rule 自己長出來的工作語與限制。
   `$ambiguity_findings` = THINK 根據 `$rules` 與 [`../../references/rules/hallucination-detection-checklist.md`](../../references/rules/hallucination-detection-checklist.md) §Pattern2 + §Pattern3 整理出的歧義 findings
   - HTTP method / API verb 自生
   - hedge phrase 與 raw 原本的明確分類衝突
   - 版本／時間／重試欄位自生
   - range 上下限自生
   - implicit precondition 自生
   IF `$frontend_lens` is non-null: 額外依 §Pattern 4 Frontend Lens 加掃 backend verb 入侵 / accessible_name 同義改寫 / anchor 自生（步驟 2 標 CiC 後仍殘留的部分；多數已由 04b 預擋）

6. 把 ambiguity findings 組成 `clarify_payload`；沒有 finding 就保持空陣列。
   `$clarify_payload` = DERIVE 根據 `$ambiguity_findings` 整理出的 clarify-loop 題組
   LOOP per `$finding` in `$ambiguity_findings`
   6.1 `$question` = DERIVE 單一 cic 題目，其中 `id=atm-Q<n>`、`concern=<finding 描述>`、`options=[A:移除留待 plan 階段, B:明確列入需求並補來源, OTHER:重新描述]`、`default=A`
   6.2 APPEND `$question` to `$clarify_payload.questions`
   END LOOP
   IF `$ambiguity_findings` empty: SET `$clarify_payload.questions = []`

7. 本 RP 不直接 ASK；若 `clarify_payload.questions` 非空，就由 caller 在 SKILL.md Phase 2 Seam B 觸發 `/clarify-loop`。

## 4. Material Reducer SOP

1. 把 `AtomicRuleDraft`、`RuleAtomicityViolation`、`RuleCiC` 與 `clarify_payload` 收成最終的 `atomic_rule_draft`。
   `$reducer_output` = DERIVE 由 `AtomicRuleDraft`、`RuleAtomicityViolation`、`RuleCiC`、`$clarify_payload` 組成的 `atomic_rule_draft`

2. 最後確認 reducer 沒有把違規狀態吃掉，也沒有把 `clarify_payload` 漏掉。
   ASSERT `atomic_rule_draft.features[]` is shaped for `/aibdd-form-feature-spec` payload
   ASSERT `RuleAtomicityViolation` is represented as split actions or violations
   ASSERT `RuleCiC` is represented in `$reducer_output`
   ASSERT `clarify_payload` 並列輸出（即使 questions 為空也要保留欄位，以利 caller 一致檢查）

Return:

```yaml
status: complete | needs_clarification | blocked
produces:
  atomic_rule_draft:
    features:
      - target_path: string
        action_id: string
        rules: []
    rules_by_operation: {}
    cic_marks: []
    exit_status: complete | blocked
    clarify_payload:
      questions: []          # 步驟 8 產出；可空（無歧義即放行）；非空時 caller 觸發 Seam B cic
traceability:
  inputs:
    - activity_analyses
    - source_material_bundle
    - impact_scope
  derived:
    - AtomicRuleDraft
    - RuleAtomicityViolation
    - RuleCiC
clarifications:
  - clarify_payload  # 步驟 8 產出；非空時由 SKILL.md Phase 2 Seam B 觸發 /clarify-loop
```
