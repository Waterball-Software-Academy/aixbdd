---
rp_type: reasoning_phase
id: discovery-uiux.04-fe-atomic-rules
context: discovery-uiux
slot: "04"
name: Frontend Atomic Rules with Verification Semantics
variant: none
consumes:
  - name: uat_flows
    kind: required_axis
    source: upstream_rp
    required: true
  - name: frontend_lens
    kind: required_axis
    source: upstream_rp
    required: true
  - name: classification
    kind: required_axis
    source: upstream_rp
    required: true
    note: 取 has-ui subset；coverage assert 用
  - name: verification_semantics_presets_ref
    kind: reference
    source: reference
    required: true
    path: ../../references/verification-semantics-presets.md
  - name: userflow_rule_coverage_ref
    kind: reference
    source: reference
    required: true
    path: ../../references/userflow-rule-coverage.md
  - name: atomic_rule_definition_ref
    kind: reference
    source: reference
    required: true
    path: aibdd-core::atomic-rule-definition.md
produces:
  - name: atomic_rule_draft
    kind: derived_axis
    terminal: true
    note: 直接餵 SKILL.md Phase 4 DELEGATE /aibdd-form-feature-spec
  - name: coverage_matrix
    kind: derived_axis
    terminal: true
    note: 直接寫入 sourcing report Coverage Matrix 章節
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: verification_mode 模糊 / coverage gap 觸發 Seam C clarify-loop
downstream:
  - discovery-uiux.05-clarification-dimensions
---

# Frontend Atomic Rules with Verification Semantics

對每個 UIVerbBinding 推一條或多條 atomic rule（含 ui_verb / anchor.accessible_name / verification_mode / optional be_operation_binding），並用 userflow-rule-coverage matrix 校驗每個 has-ui operation 在 happy / error / state-transition / a11y / cross-actor 維度的覆蓋完整性。

---

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: uat_flows
    source:
      kind: upstream_rp
      path: discovery-uiux.03-userflow-derive
    granularity: UATFlow + UATFlowStep + UATFlowTerminal 全部結構
    required_fields:
      - items
    completeness_check:
      rule: length(items) ≥ 1
      on_missing: STOP
  - name: frontend_lens
    source:
      kind: upstream_rp
      path: discovery-uiux.03-userflow-derive
    granularity: UIVerbBinding + AnchorCandidate + state_axes_hints
    required_fields:
      - ui_verb_bindings
      - anchor_candidates
    completeness_check:
      rule: ui_verb_bindings 與 anchor_candidates 至少各 1 筆
      on_missing: STOP
  - name: classification
    source:
      kind: upstream_rp
      path: discovery-uiux.02-operation-classify
    granularity: 取 has-ui subset 作為 coverage 母體
    required_fields:
      - items
    completeness_check:
      rule: items 中至少有 1 筆 classification == has-ui
      on_missing: STOP
  # verification_semantics_presets_ref / userflow_rule_coverage_ref / atomic_rule_definition_ref
  # 為 reference kind，已在 meta.consumes 列；不需出現在 Required Axis YAML
```

### 1.2 Search SOP

1. `$presets` = READ verification-semantics-presets.md §1 + §2
2. `$coverage` = READ userflow-rule-coverage.md §1 + §2
3. `$has_ui_subset` = DERIVE classification.items where classification == has-ui
4. `$bindings_by_op` = DERIVE map(be_op_id → list<UIVerbBinding>) ← frontend_lens.ui_verb_bindings
5. `$flow_by_op` = DERIVE map(be_op_id → UATFlow) ← uat_flows.items
6. ASSERT 每個 has_ui_subset.op_id 都有對應 UATFlow + 至少 1 個 UIVerbBinding

---

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: { atomic_rule_draft, coverage_matrix }
  element_rules:
    element_vs_field:
      element: "AtomicRule + FeatureBundle 是 Phase 4 DELEGATE /aibdd-form-feature-spec 的最小投遞單位；CoverageRow 是 sourcing report Coverage Matrix 的 join 主鍵"
      field: "rule body / anchor / verification_mode 屬性隸屬於 AtomicRule"
  elements:
    AtomicRule:
      role: "Frontend Rule 的最小可獨立驗證單位"
      fields:
        rule_id: string
        feature_id: string                 # 對應 FeatureBundle.id
        rule_body: string                  # 渲染後的 Gherkin Rule body
        ui_verb: string
        anchor:
          anchor_id: string
          role: string
          accessible_name: string
        verification_mode: enum            # locator | visual-state | route | api-binding
        be_operation_binding: string | null  # op_id；api-binding 必填
        coverage_dimension: enum           # happy | error | state-transition | a11y | cross-actor
        source_step_id: string             # 對應 UATFlowStep.step_id
      invariants:
        - "verification_mode 必為 enum 四值之一"
        - "verification_mode == api-binding ⇒ be_operation_binding 非空"
        - "anchor.role 不在 frontend-rule-axes §4.4 黑名單"
        - "rule_body 不得含 frontend-rule-axes §2.1 backend-verb 黑名單"
        - "同一 rule 不得同時標兩個 verification_mode"
    FeatureBundle:
      role: "對應一個 has-ui BEOperation 的 .feature 檔投遞單位；裡頭可包含多條 AtomicRule"
      fields:
        feature_id: string
        be_op_id: string
        target_path: string                # ${FEATURE_SPECS_DIR}/<slug>.feature
        rules: list<AtomicRule>
        reasoning_package:
          frontend_lens_subset: object
          verification_semantics_used: list<string>
      invariants:
        - "target_path flat under ${FEATURE_SPECS_DIR}"
        - "rules 非空"
        - "rules 中至少有 1 條 coverage_dimension == happy"
    CoverageRow:
      role: "對應一個 has-ui BEOperation 在 5 個 coverage 維度上的 rule 數統計"
      fields:
        be_op_id: string
        happy: int
        error: int | null                  # null 代表「不適用」
        state_transition: int | null
        a11y: int | null
        cross_actor: int | null
      invariants:
        - "happy ≥ 1（必填維度）"
        - "其他維度依 userflow-rule-coverage §2 觸發條件決定 null vs int"
    AtomicRuleCiC:
      role: "verification_mode 模糊 / coverage gap / be-op binding 缺漏 便條紙；轉入 clarify_payload"
      fields:
        type: enum                         # GAP | ASM | BDY | CON
        rule_id: string | null
        be_op_id: string | null
        message: string
```

---

## 3. Reasoning SOP

1. `$rules_raw` = DERIVE per UIVerbBinding：
   - 取對應 AnchorCandidate
   - 依 ui_verb category 決定預設 verification_mode：
     - input / state-change → 至少 1 條 locator + （如果觸發 BE 副作用）1 條 api-binding
     - visual / feedback → visual-state
     - navigation → route
   - 渲染 Rule body ← verification-semantics-presets §2 對應 preset 樣板
   - 標 coverage_dimension：先預設 happy；error / state-transition / a11y / cross-actor 由下一步補
2. `$rules_extra` = DERIVE 補 error / state-transition / a11y / cross-actor 維度：
   - 對 BE feature 有 fail Scenario / Decision branch 有失敗 → 補 error visual-state rule
   - 對 BE op async 或 state change → 補 state-transition rule
   - 對 BE op 觸發 dialog / async 反應 → 補 a11y rule
   - 對 BE op security 有多 actor 條件 → 補 cross-actor rule
3. `$features` = DERIVE FeatureBundle per has-ui BEOperation：
   - target_path = `${FEATURE_SPECS_DIR}/<be_op_slug>.feature`
   - rules = $rules_raw ∪ $rules_extra 過濾 be_op_id 對應
4. `$coverage_matrix` = DERIVE CoverageRow per has-ui BEOperation：
   - happy / error / state-transition / a11y / cross-actor 數量統計
   - 不適用維度（依 userflow-rule-coverage §2 觸發條件未命中）→ null
5. `$cic_marks` = THINK 標 AtomicRuleCiC：
   - rule.verification_mode 缺 → CiC(GAP)
   - rule.body 含 backend-verb 黑名單 → CiC(ASM)
   - happy 維度為 0 → CiC(BDY) coverage-gap
   - api-binding mode 缺 be_operation_binding → CiC(BDY)
6. `$clarify_payload` = DERIVE per $cic_marks → question 題組（id=`rule-Q<n>`）

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE atomic_rule_draft + coverage_matrix + clarify_payload：
   - `atomic_rule_draft = {features: $features, rules_total: count($features.rules), clarify_payload: $clarify_payload}`
   - `coverage_matrix = {rows: $coverage_matrix}`
2. ASSERT 每筆 AtomicRule invariants 成立
3. ASSERT 每個 has-ui BEOperation 都有對應 FeatureBundle
4. ASSERT 每個 FeatureBundle.rules 至少 1 條 coverage_dimension == happy
5. ASSERT 沒有 rule 同時標兩個 verification_mode

Return:

```yaml
status: complete | needs_clarification | blocked
produces:
  atomic_rule_draft:
    features: []
    rules_total: int
    clarify_payload:
      questions: []
  coverage_matrix:
    rows: []
traceability:
  inputs:
    - uat_flows
    - frontend_lens
    - classification
    - verification_semantics_presets_ref
    - userflow_rule_coverage_ref
    - atomic_rule_definition_ref
  derived:
    - AtomicRule
    - FeatureBundle
    - CoverageRow
    - AtomicRuleCiC
clarifications:
  - clarify_payload   # 非空 → SKILL.md Phase 3 §4 觸發 Seam C clarify-loop
```
