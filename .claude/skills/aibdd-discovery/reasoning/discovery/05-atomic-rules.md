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
```

### 1.2 Search SOP

1. 先把這一輪要拿來切 atomic rules 的三條主軸讀進來：activity 分析、source material、impact scope。
   `$activity_analyses` = READ activity_analyses（只取 `modeled=true` 之 entries；caller 已確保 Seam A 已通過）
   `$bundle` = READ source_material_bundle
   `$impact_scope` = READ impact_scope
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
      invariants:
        - "保留 @ignore"
        - "不得包含 Background / Scenario / Examples"
        - "每個 rule 必須有 action_id、source_quote 或 impact_pointer、condition、consequence、target_feature_path"
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

2. 把不夠原子的地方顯式標成 violation，把仍未解決的規則歧義標成 `RuleCiC`。
   `$violations` = CLASSIFY `$rules` by `RuleAtomicityViolation`
   `$rule_cic` = DERIVE 根據 unresolved rule ambiguity 整理出的 `RuleCiC`

3. 先做交棒前的基本合法性檢查。
   ASSERT every `AtomicRuleDraft` item has action_id, source_quote or impact_pointer, condition, consequence, and target_feature_path
   ASSERT target_feature_path is under `${FEATURE_SPECS_DIR}` / target function package, not boundary root `features/`
   ASSERT no `AtomicRuleDraft` item contains example data, Background, Scenario, or Examples
   ASSERT 每個 `features[]` entry 在最終輸出中對應的 `target_feature_path` 唯一
   ASSERT 每個 `features[]` entry 只對應一個單一 operation surface

4. 對規則草稿做規則層歧義檢查，專門抓 raw 沒說、但 rule 自己長出來的工作語與限制。
   `$ambiguity_findings` = THINK 根據 `$rules` 與 [`../../references/rules/hallucination-detection-checklist.md`](../../references/rules/hallucination-detection-checklist.md) §Pattern2 + §Pattern3 整理出的歧義 findings
   - HTTP method / API verb 自生
   - hedge phrase 與 raw 原本的明確分類衝突
   - 版本／時間／重試欄位自生
   - range 上下限自生
   - implicit precondition 自生

5. 把 ambiguity findings 組成 `clarify_payload`；沒有 finding 就保持空陣列。
   `$clarify_payload` = DERIVE 根據 `$ambiguity_findings` 整理出的 clarify-loop 題組
   LOOP per `$finding` in `$ambiguity_findings`
   5.1 `$question` = DERIVE 單一 cic 題目，其中 `id=atm-Q<n>`、`concern=<finding 描述>`、`options=[A:移除留待 plan 階段, B:明確列入需求並補來源, OTHER:重新描述]`、`default=A`
   5.2 APPEND `$question` to `$clarify_payload.questions`
   END LOOP
   IF `$ambiguity_findings` empty: SET `$clarify_payload.questions = []`

6. 本 RP 不直接 ASK；若 `clarify_payload.questions` 非空，就由 caller 在 SKILL.md Phase 2 Seam B 觸發 `/clarify-loop`。

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
