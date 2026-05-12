---
rp_type: reasoning_phase
id: discovery.06-atomic-clarify
context: discovery
slot: "06"
name: Atomic Clarify (Seam B)
variant: post_atomic_draft
consumes:
  - name: atomic_rule_draft
    kind: required_axis
    source: upstream_rp
    required: true
  - name: source_material_bundle
    kind: required_axis
    source: upstream_rp
    required: true
  - name: hallucination_detection_checklist
    kind: reference
    source: reference
    required: true
produces:
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: 偵測到 Class 2 規則層腦補（HTTP method 寫死 / hedging / 版本欄位 / 範圍上下限自生）時輸出題目；無歧義則 questions 為空
downstream:
  - discovery.07-clarification-dimensions
---

# Atomic Clarify — Seam B（規則層歧義）

本 RP 在 RP03 atomic-rules 完成後、formulation 落檔前執行。目的是攔截 **Class 2 — raw 留白但 AI 自生規則文字** 的腦補（規則層）。RP03 已先做 ambiguity detection；本 RP 把 detection 結果整理成 `clarify_payload`。

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: atomic_rule_draft
    source:
      kind: upstream_rp
      path: discovery.05-atomic-rules
    granularity: rules_by_operation + features[].rules[]；含每條 rule 的 condition / consequence / source_quote
    required_fields:
      - features
      - rules_by_operation
    optional_fields:
      - clarify_payload
    completeness_check:
      rule: RP03 atomic_rule_draft 已輸出，cic_marks 已落
      on_missing: STOP
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: raw idea + normalized_excerpts，用於 traceback 比對
    required_fields:
      - raw_material_pointers
      - normalized_excerpts
    optional_fields: []
    completeness_check:
      rule: RP01 source_material_bundle 已落定
      on_missing: STOP
```

> 註：`hallucination_detection_checklist` 不在 Required Axis（屬靜態 reference doc）；本 RP 引用 §Pattern2（inference-without-source）+ §Pattern3（demo-anchor）。

### 1.2 Search SOP

1. 先把這一輪要檢查的 rules、source material、與腦補檢查表讀進來。
   `$rules` = READ `atomic_rule_draft.features[*].rules`
   `$bundle` = READ `source_material_bundle`
   `$checklist` = READ `hallucination_detection_checklist`

2. 這一輪至少要有 rules 可掃；如果規則清單是空的，就不應該進 Atomic Clarify。
   ASSERT `$rules` non-empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: clarify_payload
  element_rules:
    element_vs_field:
      element: "規則層待回問的歧義題目"
      field: "題目的屬性（id / concern / options / default）"
  elements:
    ClarifyQuestion:
      role: "atomic rule 階段一個待回問的歧義題目"
      fields:
        id: stable_id
        concern: string
        options: option[]
        default: option_id
      invariants:
        - "id 形如 atm-Q<n>"
        - "concern 描述命中的 rule 文字片段與其違反的 detection pattern（HTTP method / hedge / version / range / precondition）"
      nested_fields:
        option:
          id: A | B | OTHER
          label: string
          impact: string
```

## 3. Reasoning SOP

1. 先從空的 findings 開始，逐條 rule 掃描哪些規則文字是 raw 沒講、卻由系統自行補出來的。
   `$findings` = DERIVE 空清單

2. 逐條 rule 檢查常見的規則層腦補。
   LOOP per `$rule` in `$rules` (budget=count(`$rules`)；exit when 每條 rule 都已掃描)
   2.1 `$http_hit` = MATCH `$rule.text` against /POST|GET|PUT|DELETE|PATCH/
   2.2 IF `$http_hit` == true ∧ MATCH(`$bundle.normalized_excerpts`, http_method) == false: APPEND `{kind:http_method, ref:$rule.id}` to `$findings`
   2.3 `$hedge_hit` = MATCH `$rule.text` against /等價|正向／負向|類似|左右/
   2.4 IF `$hedge_hit` == true: APPEND `{kind:hedge, ref:$rule.id}` to `$findings`
   2.5 `$version_hit` = MATCH `$rule.text` against /version|expires|retry|timestamp/
   2.6 IF `$version_hit` == true ∧ MATCH(`$bundle.normalized_excerpts`, version_field) == false: APPEND `{kind:version_field, ref:$rule.id}` to `$findings`
   2.7 `$range_hit` = MATCH `$rule.text` for 具體上限／下限數字
   2.8 IF `$range_hit` == true ∧ raw 對應數字無 traceback 或帶 marker: APPEND `{kind:range_anchor, ref:$rule.id}` to `$findings`
   2.9 `$precondition_hit` = MATCH `$rule.text` for implicit precondition
   2.10 IF `$precondition_hit` == true ∧ MATCH(`$bundle.normalized_excerpts`, precondition) == false: APPEND `{kind:precondition, ref:$rule.id}` to `$findings`
   END LOOP

3. 把 findings 組成 `ClarifyQuestion`；沒有 finding 就讓 questions 保持空陣列。
   LOOP per `$finding` in `$findings` (budget=count(`$findings`))
   3.1 `$question` = CLASSIFY `$finding` into `ClarifyQuestion`，其中 `id=atm-Q<n>`、`concern=<finding 描述>`、`options=[A:移除留待 plan 階段, B:明確列入需求並補來源, OTHER:重新描述]`、`default=A`
   3.2 APPEND `$question` to `$questions`
   END LOOP

4. 收尾檢查每個題目 id 是否穩定且唯一。
   ASSERT 所有 `$questions[*].id` unique

## 4. Material Reducer SOP

1. 把這輪整理好的題目收成 `clarify_payload`；沒有題目也要回空陣列。
   `$reducer_output` = DERIVE 由 `$questions` 組成的 `clarify_payload`

2. 最後確認輸出形狀穩定，讓 caller 能直接判斷要不要進 Seam B 的 `/clarify-loop`。
   ASSERT `$reducer_output.questions` 為 list（可空）
   ASSERT 每題滿足 `ClarifyQuestion` invariants

Return:

```yaml
status: complete | blocked
produces:
  clarify_payload:
    questions: []                # 0..N 筆 ClarifyQuestion
traceability:
  inputs:
    - atomic_rule_draft
    - source_material_bundle
    - hallucination_detection_checklist
  derived:
    - ClarifyQuestion
clarifications:
  - clarify_payload  # caller (SKILL.md Phase 2 Seam B) 觸發 /clarify-loop
```

## 5. Anti-Pattern

- ❌ 對 activity 結構歧義丟題目（屬 Seam A 範疇）
- ❌ 對 sourcing 層 marker 丟題目（屬 Seam 0 範疇）
- ❌ 對 raw 已明確的規則細節重複問（屬 Class 3 失讀，由 P5 sweep 處理）
- ❌ 對 entity 欄位 schema / 內部資料結構越界提問（屬 plan 階段，不在 Discovery scope）
