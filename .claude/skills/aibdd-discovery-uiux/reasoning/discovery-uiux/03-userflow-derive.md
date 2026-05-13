---
rp_type: reasoning_phase
id: discovery-uiux.03-userflow-derive
context: discovery-uiux
slot: "03"
name: Userflow & Frontend Lens Derivation
variant: none
consumes:
  - name: classification
    kind: required_axis
    source: upstream_rp
    required: true
    note: 由 02-operation-classify 產出；只 LOOP has-ui 子集
  - name: be_truth_bundle
    kind: material_bundle
    source: upstream_rp
    required: true
    note: 03 需要 BE activity 內的 action 順序作為 step order 參考
  - name: frontend_rule_axes_ref
    kind: reference
    source: reference
    required: true
    path: ../../../aibdd-discovery/references/rules/frontend-rule-axes.md
    note: UI verb catalog / role mapping / anchor 命名 / boundary role gate（aibdd-discovery sibling）
  - name: hallucination_detection_checklist_ref
    kind: reference
    source: reference
    required: true
    path: ../../../aibdd-discovery/references/rules/hallucination-detection-checklist.md
    note: Pattern 4 Frontend Lens 腦補檢測（aibdd-discovery sibling）
produces:
  - name: uat_flows
    kind: derived_axis
    terminal: false
  - name: frontend_lens
    kind: derived_axis
    terminal: false
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: anchor name / role / ui_verb / step order 模糊時觸發 Seam B clarify-loop
downstream:
  - discovery-uiux.04-fe-atomic-rules
---

# Userflow & Frontend Lens Derivation

對每個 has-ui BEOperation 推導對應的 frontend uat_flow（actor=end-user，nodes=UI verbs + DECISION + terminals），同時 reuse aibdd-discovery 04b-frontend-axes 的 frontend_lens 規格抽 UIVerbBinding[] + AnchorCandidate[]。

---

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: classification
    source:
      kind: upstream_rp
      path: discovery-uiux.02-operation-classify
    granularity: 每筆 has-ui OperationClassification
    required_fields:
      - items
    completeness_check:
      rule: items 中至少有 1 筆 classification == has-ui
      on_missing: STOP
  # be_truth_bundle 為 material_bundle kind，已在 meta.consumes 列；不需出現在 Required Axis YAML
  # frontend_rule_axes_ref / hallucination_detection_checklist_ref 為 reference kind，已在 meta.consumes 列
```

### 1.2 Search SOP

1. `$has_ui_ops` = DERIVE 由 classification.items 過濾出 classification == has-ui 子集
2. `$ui_verb_catalog` = READ frontend-rule-axes.md §2
3. `$role_mapping` = READ frontend-rule-axes.md §3
4. `$anchor_rules` = READ frontend-rule-axes.md §4
5. `$pattern4_checklist` = READ hallucination-detection-checklist Pattern 4 Frontend Lens
6. ASSERT length(`$has_ui_ops`) ≥ 1；否則本 RP 直接 short-circuit 為空 uat_flows + 空 frontend_lens

---

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: { uat_flows, frontend_lens }
  element_rules:
    element_vs_field:
      element: "uat_flow 與 ui-verb-binding / anchor-candidate 是 04 atomic-rules 必須 LOOKUP 的最小單位"
      field: "step_id / actor / target 等屬性隸屬於 uat_flow 或 UIVerbBinding"
  elements:
    UATFlow:
      role: "對應一個 has-ui BEOperation 的 frontend userflow，描述 end-user 從 entry 到 terminal 的互動路徑"
      fields:
        flow_id: string
        be_op_id: string                  # 對回 BEOperation.op_id
        actor: enum                       # end-user | guest | authenticated-user
        entry_trigger: string             # 使用者進入此 flow 的入口（page load / 點 nav 等）
        steps: list<UATFlowStep>
        terminals: list<UATFlowTerminal>
      invariants:
        - "actor 必為 enum 三值之一（external user / third-party 範疇）"
        - "be_op_id 必須對應到 classification 中 has-ui 的 op_id"
        - "至少有 1 個 entry + 1 個 terminal"
    UATFlowStep:
      role: "userflow 中單一 user 動作或 decision 點"
      fields:
        step_id: string
        kind: enum                        # action | decision | visual-feedback
        ui_verb: string                   # 對應 frontend-rule-axes §2 catalog
        target_anchor_id: string | null   # 對應 AnchorCandidate.anchor_id
        decision_branches: list<string> | null  # kind=decision 時必填
        source_quote: string              # BE truth verbatim 來源
    UATFlowTerminal:
      role: "userflow 的終結節點"
      fields:
        terminal_id: string
        kind: enum                        # success | error | abandoned
        visual_outcome: string            # 對應 visual-state preset 之一
    UIVerbBinding:
      role: "把 uat_flow action 的動詞綁到 UI verb catalog 的一條對應；reuse aibdd-discovery 04b 規格"
      fields:
        binding_id: string
        flow_id: string
        step_id: string
        be_op_id: string
        source_verb: string
        ui_verb: string                   # catalog enum
        category: enum                    # input | state-change | feedback | visual | navigation
      invariants:
        - "ui_verb 必須在 catalog enum 內；禁自創"
        - "source_verb 必須是 BE truth 動詞 verbatim"
    AnchorCandidate:
      role: "下游 04 atomic-rules + form-story-spec 直接消費的 binding 鉤子；reuse 04b 規格"
      fields:
        anchor_id: string
        role: string                      # ARIA role；禁 generic / div / span
        accessible_name: string           # verbatim 動詞片語
        source_quote: string
        interactivity: enum               # interactive | informational
        state_axes_hint:
          base: list<string>
          domain: list<string>
      invariants:
        - "anchor_id 在 frontend_lens 內唯一；同一 BE op 多 frame 共用同一 anchor_id"
        - "accessible_name 與 source_quote lemma 一致（依 frontend-rule-axes §4.2）"
        - "role 必須來自 frontend-rule-axes §3 mapping enum；禁出現 generic / div / span"
    FrontendLensCiC:
      role: "ui_verb 無法對應 catalog / role 模糊 / 黑名單動詞 leak 等問題的便條紙"
      fields:
        type: enum                        # GAP | ASM | BDY | CON
        binding_id: string | null
        anchor_id: string | null
        message: string
```

---

## 3. Reasoning SOP

1. `$flows_raw` = DERIVE per has-ui BEOperation：
   - 從 BE `.activity` 找 attribution flow → 把 BE action 序列翻譯成 user-side UATFlowStep（保留順序）
   - 從 BE feature Rule body 找 visual outcome → 補 UATFlowTerminal
   - DECISION 分支 → UATFlowStep.kind=decision + 子 branch 對應 terminal
2. `$ui_verb_bindings` = DERIVE per UATFlowStep（kind == action）：
   - lemma 對應 catalog `ui_verb`；對應不上 → FrontendLensCiC(GAP)
   - 黑名單動詞命中（POST / persist / 200 等）→ FrontendLensCiC(ASM)
3. `$anchor_candidates` = DERIVE per UIVerbBinding：
   - role ← frontend-rule-axes §3 mapping
   - accessible_name ← source_verb + object verbatim quote
   - 同義改寫 → FrontendLensCiC(ASM)
4. `$state_hints` = DERIVE per AnchorCandidate：
   - base ← §5.1 對應 role 預設集
   - domain ← BE activity DECISION 分支推得（loading / empty / error / populated / pristine）
5. `$pattern4_findings` = THINK Pattern 4 Frontend Lens 檢查（backend-verb leak / accessible_name 同義改寫 / role 黑名單 / 自生 anchor）
6. `$clarify_payload` = DERIVE per FrontendLensCiC + step order 模糊：
   - 每筆 finding 補一道 question；id=`flow-Q<n>`；options=[A: 改 BE 來源 verbatim, B: 補 catalog, C: split-flow]

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE uat_flows + frontend_lens + clarify_payload：
   - `uat_flows = {items: $flows_raw}`
   - `frontend_lens = {ui_verb_bindings: $ui_verb_bindings, anchor_candidates: $anchor_candidates, state_axes_hints: $state_hints, cic_marks: $pattern4_findings, clarify_payload: $clarify_payload}`
2. ASSERT 每個 UATFlow.be_op_id 都對應到 classification has-ui 子集
3. ASSERT 每個 modeled UATFlowStep.kind=action 都有對應 UIVerbBinding；資訊性 step 例外
4. ASSERT 每個 UIVerbBinding 都有對應 AnchorCandidate（informational 例外）
5. ASSERT 無 accessible_name 與 source_quote lemma 不一致

Return:

```yaml
status: complete | needs_clarification | blocked
produces:
  uat_flows:
    items: []
  frontend_lens:
    ui_verb_bindings: []
    anchor_candidates: []
    state_axes_hints: []
    cic_marks: []
    clarify_payload:
      questions: []
traceability:
  inputs:
    - classification
    - be_truth_bundle
    - frontend_rule_axes_ref
    - hallucination_detection_checklist_ref
  derived:
    - UATFlow
    - UATFlowStep
    - UATFlowTerminal
    - UIVerbBinding
    - AnchorCandidate
    - FrontendLensCiC
clarifications:
  - clarify_payload   # 非空 → SKILL.md Phase 2 §6 觸發 Seam B clarify-loop
```
