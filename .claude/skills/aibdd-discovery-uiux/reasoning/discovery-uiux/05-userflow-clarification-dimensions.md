---
rp_type: reasoning_phase
id: discovery-uiux.05-clarification-dimensions
context: discovery-uiux
slot: "05"
name: Residual Clarification Sweep
variant: none
consumes:
  - name: atomic_rule_draft
    kind: required_axis
    source: upstream_rp
    required: true
  - name: uat_flows
    kind: required_axis
    source: upstream_rp
    required: true
  - name: artifact_bundle
    kind: material_bundle
    source: skill_global
    required: true
    note: SKILL.md Phase 4 落檔後的 .activity / .feature 路徑與內容
  - name: quality_verdict
    kind: required_axis
    source: skill_global
    required: true
    note: Phase 5 §5.A script + §5.B semantic gate 合併 verdict
produces:
  - name: residual_clarify_payload
    kind: derived_axis
    terminal: true
    note: 直接餵 SKILL.md Phase 5 §5.D Seam D clarify-loop
downstream: []
---

# Residual Clarification Sweep

當 deterministic + semantic gate 都通過一輪後，跨 artifact 機械掃描下列維度，把無法被前 4 個 RP 涵蓋的殘留模糊收進一份 clarify payload 餵 Seam D。

---

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: atomic_rule_draft
    source:
      kind: upstream_rp
      path: discovery-uiux.04-fe-atomic-rules
    granularity: FeatureBundle + AtomicRule 全部結構
    required_fields:
      - features
    completeness_check:
      rule: length(features) ≥ 1
      on_missing: STOP
  - name: uat_flows
    source:
      kind: upstream_rp
      path: discovery-uiux.03-userflow-derive
    granularity: UATFlow 全部結構（含 terminal / decision branch）
    required_fields:
      - items
    completeness_check:
      rule: length(items) ≥ 1
      on_missing: STOP
  - name: quality_verdict
    source:
      kind: skill_global
    granularity: script + semantic gate 合併 verdict（rule_id → pass/fail）
    required_fields:
      - rule_results
    completeness_check:
      rule: rule_results 為 non-empty dict
      on_missing: STOP
  # artifact_bundle 為 material_bundle kind，已在 meta.consumes 列；不需出現在 Required Axis YAML
```

### 1.2 Search SOP

1. `$features_on_disk` = READ artifact_bundle.features 檔案內容
2. `$activities_on_disk` = READ artifact_bundle.activities 檔案內容
3. `$gate_results` = READ quality_verdict.rule_results

---

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: residual_clarify_payload
  element_rules:
    element_vs_field:
      element: "Question 是 Seam D clarify-loop 投遞單位，必須可獨立 LOOKUP 回答案"
      field: "options / recommendation / rationale 隸屬於 Question"
  elements:
    ResidualQuestion:
      role: "跨 artifact / 多 RP 才能浮現的殘留模糊；不歸屬任何單一上游 RP"
      fields:
        question_id: string                # res-Q<n>
        dimension: enum                    # cross-rule-consistency | terminal-coverage | actor-mismatch | gap-revisit | gate-soft-warn
        concern: string
        evidence_paths: list<string>       # 對應的 artifact 檔路徑
        options: list<string>
        recommendation: string
        rationale: string
      invariants:
        - "dimension 必為 enum 五值之一"
        - "evidence_paths 非空（殘留必須可被使用者 trace）"
```

---

## 3. Reasoning SOP

1. `$cross_rule_consistency` = THINK 掃跨 feature 的命名 / verbatim / role 衝突：
   - 同一 anchor_id 在多 feature 內 accessible_name 不一致
   - 同一 BE op_id 被多個 feature 引用（違反 OPERATION_WISE_FEATURE_FILE）
2. `$terminal_coverage` = THINK 掃 UATFlow.terminals 與 feature rules 對應：
   - terminal 標 success 但無對應 happy rule
   - terminal 標 error 但無對應 error rule（且 §2 觸發 error 必填）
3. `$actor_mismatch` = THINK 掃 activity actor vs feature Background actor 是否一致
4. `$gap_revisit` = THINK 掃 GAP report no-ui operations 是否有 revisit_trigger 缺漏
5. `$soft_warn` = THINK 掃 quality_verdict.rule_results 中 SOFT 等級命中項（a11y / state-transition 對應）
6. `$residual_questions` = DERIVE ResidualQuestion list ← union(`$cross_rule_consistency`, `$terminal_coverage`, `$actor_mismatch`, `$gap_revisit`, `$soft_warn`)

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE residual_clarify_payload：
   - `residual_clarify_payload = {questions: $residual_questions}`
2. ASSERT 每筆 ResidualQuestion invariants 成立
3. ASSERT 任何 ResidualQuestion 都對應到至少一條 evidence_path（artifact_bundle 內存在）

Return:

```yaml
status: complete
produces:
  residual_clarify_payload:
    questions: []
traceability:
  inputs:
    - atomic_rule_draft
    - uat_flows
    - artifact_bundle
    - quality_verdict
  derived:
    - ResidualQuestion
clarifications:
  - residual_clarify_payload   # 非空 → SKILL.md Phase 5 §5.D 觸發 Seam D clarify-loop
```
