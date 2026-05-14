---
rp_type: reasoning_phase
id: discovery-uiux.02-operation-classify
context: discovery-uiux
slot: "02"
name: Operation Has-UI Classification
variant: none
consumes:
  - name: operation_inventory
    kind: required_axis
    source: upstream_rp
    required: true
    note: 由 01-be-sourcing 產出
  - name: be_truth_bundle
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: runtime_context
    kind: required_axis
    source: skill_global
    required: true
    note: 需含 TLB.id（FE boundary） + TLB.role
  - name: be_to_fe_mapping_ref
    kind: reference
    source: reference
    required: true
    path: ../../references/be-to-fe-mapping.md
  - name: fe_intent_bundle
    kind: required_axis
    source: upstream_rp
    required: true
    note: 由 00-fe-intent-sourcing 產出；提供 scope_inclusion 作為 classification tie-breaker
  - name: be_gap_findings
    kind: derived_axis
    source: upstream_rp
    required: true
    note: 由 01-be-sourcing 產出；classification.reasoning 引用 GAP report pointer 而非內聯 BE 衝突字句
produces:
  - name: classification
    kind: derived_axis
    terminal: false
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: ambiguous classification 或缺欄 BE operation 觸發 Seam A clarify-loop
downstream:
  - discovery-uiux.03-userflow-derive
---

# Operation Has-UI Classification

對每個 BEOperation 依 4 維度評分（actor / trigger / permission / synchronicity）後 CLASSIFY 為 has-ui / no-ui / ambiguous，並對 no-ui operation 補上 reasoning + revisit trigger 後寫入 GAP 清單。同時消費 `fe_intent_bundle.scope_decisions` 作為 tie-breaker：intent.decision=exclude ∧ BE 訊號偏 has-ui → 強制 ambiguous（不得 silent has-ui）；classification.reasoning 在引用 BE 衝突時必須指向 `discovery-uiux-be-gap.md` pointer，禁止內聯 BE 衝突字句。

---

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: operation_inventory
    source:
      kind: upstream_rp
      path: discovery-uiux.01-be-sourcing
    granularity: 每筆 BEOperation 一筆 evaluation candidate
    required_fields:
      - items
    completeness_check:
      rule: length(items) ≥ 1
      on_missing: STOP
  # be_truth_bundle 為 material_bundle kind，已在 meta.consumes 列；不需出現在 Required Axis YAML
  # be_to_fe_mapping_ref 為 reference kind，已在 meta.consumes 列；不需出現在 Required Axis YAML
  - name: fe_intent_bundle
    source:
      kind: upstream_rp
      path: discovery-uiux.00-fe-intent-sourcing
    granularity: 整個 fe_intent_bundle 結構（scope_decisions 為主要 tie-breaker 來源）
    required_fields:
      - scope_decisions
    completeness_check:
      rule: scope_decisions 條目數 ≥ 對應的 has-ui BE op 候選數
      on_missing: STOP
  - name: runtime_context
    source:
      kind: skill_global
    granularity: FE TLB 全貌 + arguments.yml 語境
    required_fields:
      - TLB.id
      - TLB.role
    completeness_check:
      rule: TLB.role == "frontend"
      on_missing: STOP
```

### 1.2 Search SOP

1. `$rubric` = READ be-to-fe-mapping.md §1 / §1.3 / §1.4
2. `$ops` = READ operation_inventory.items（已含 actors / source / verb / object / uat_flow_attribution）
3. `$signals` = DERIVE per BEOperation 的 4 維度訊號（actor / trigger / permission / synchronicity）依 §1.1 rubric
4. ASSERT 每筆 BEOperation 4 維度訊號至少 2 個非空；若 ≥3 個維度缺訊號則記 CiC(GAP)

---

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: classification
  element_rules:
    element_vs_field:
      element: "對單一 BEOperation 的 classification 紀錄（含維度評分痕跡），是 03 / 04 直接 LOOKUP 的 join key"
      field: "只能隸屬於某個 OperationClassification 的訊號 / 推論 / 答覆"
  elements:
    OperationClassification:
      role: "BEOperation 在 frontend TLB 下的 has-ui / no-ui 判定結果"
      fields:
        op_id: string
        classification: enum    # has-ui | no-ui | ambiguous
        signals:
          actor: list<string>
          trigger: list<string>
          permission: list<string>
          synchronicity: list<string>
        rubric_hit:
          blacklist: list<string>   # §1.3 命中項目
          whitelist: list<string>   # §1.4 命中項目
          law: string               # §1.2 命中法則 id
        intent_trace:
          decision: enum            # include | exclude | defer | unknown（來自 fe_intent_bundle.scope_decisions）
          source_question_id: string | null  # 若 decision 為 clarify-answer
        be_gap_refs: list<string>   # 對應 BEGapFinding.detect_id；reasoning 引用 GAP report pointer
        reasoning: string
        revisit_trigger: string | null   # 僅 no-ui 必填
      invariants:
        - "classification 必為 enum 三值之一"
        - "blacklist 命中時 classification != has-ui（除非同時 whitelist 命中 → ambiguous）"
        - "no-ui 必填 reasoning + revisit_trigger"
        - "intent_trace.decision == exclude ∧ whitelist 命中 → classification 必為 ambiguous 或 no-ui，禁 has-ui"
        - "be_gap_refs 非空 → reasoning 必含 'see discovery-uiux-be-gap.md' literal pointer，禁內聯 BE 衝突字句"
    ClassificationCiC:
      role: "classification 過程中無法判定的便條紙；轉入 clarify_payload"
      fields:
        op_id: string
        question_id: string
        concern: string
        options: list<string>
        recommendation: string
        rationale: string
```

---

## 3. Reasoning SOP

1. `$op_signals` = DERIVE per BEOperation 4 維度訊號 ← `$ops` + `$be_truth_bundle`
2. `$blacklist_hits` = MATCH each BEOperation against be-to-fe-mapping.md §1.3 黑名單訊號
3. `$whitelist_hits` = MATCH each BEOperation against be-to-fe-mapping.md §1.4 白名單訊號
4. `$law_decisions` = CLASSIFY per BEOperation against §1.2 法則表 → has-ui / no-ui / ambiguous
5. `$intent_lookup` = DERIVE per BEOperation：對應 `fe_intent_bundle.scope_decisions[op_id].decision`（缺則 unknown）
6. `$be_gap_lookup` = DERIVE per BEOperation：對應 `be_gap_findings.items` 中 op_id 命中的 detect_id list
7. `$classifications` = DERIVE OperationClassification list：
   - 黑名單命中且白名單未命中 → no-ui
   - 白名單命中且黑名單未命中且 intent.decision ∈ {include, unknown, defer} → has-ui
   - 白名單命中但 intent.decision == exclude → ambiguous（強制 tie-breaker；CiC）
   - 兩者皆命中 → ambiguous（CiC）
   - 兩者皆未命中 → 依 §1.2 法則 推導；多模糊 → ambiguous（CiC）
8. `$reasoning_strings` = DRAFT per classification.reasoning：若 `$be_gap_lookup` 對應非空，reasoning 必含 literal `"see discovery-uiux-be-gap.md#${detect_id}"` 指標；禁內聯 BE 衝突字句
9. `$gap_list` = DERIVE 由 classification == no-ui 的子集，必填 reasoning + revisit_trigger（缺則記 CiC(GAP)）
10. `$clarify_payload` = DERIVE per OperationClassification.classification == ambiguous：
    - 每筆 ambiguous 補一道 question：`{id: cls-Q<n>, concern: "op_id ${op_id} 4 維度訊號模糊（intent=${decision}, be_gap=${detect_ids}）；請判定 has-ui / no-ui", options: ["has-ui", "no-ui", "split-into-multiple"], recommendation: 依目前訊號偏向值, rationale}`

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE classification + gap_list + clarify_payload：
   - `classification = {items: $classifications}`
   - `gap_list = items 中 classification == no-ui 的子集`
   - `clarify_payload = {questions: 上述 ambiguous 題組}`
2. ASSERT 每筆 OperationClassification invariants 成立（含 intent_trace / be_gap_refs invariants）
3. ASSERT classification.items 與 operation_inventory.items 一一對應（length 相等）
4. ASSERT 任何 ambiguous classification 都必須在 clarify_payload.questions 找到對應 op_id
5. ASSERT 任何 reasoning 含 BE 衝突陳述者，必含 `"see discovery-uiux-be-gap.md"` literal pointer（禁內聯）

Return:

```yaml
status: complete | needs_clarification | blocked
produces:
  classification:
    items: []        # OperationClassification[]
  gap_list:
    items: []        # no-ui subset
  clarify_payload:
    questions: []    # ambiguous → Seam A
traceability:
  inputs:
    - operation_inventory
    - be_truth_bundle
    - runtime_context
    - fe_intent_bundle
    - be_gap_findings
  derived:
    - OperationClassification
    - ClassificationCiC
clarifications:
  - clarify_payload  # 非空 → SKILL.md Phase 2 觸發 Seam A clarify-loop
```
