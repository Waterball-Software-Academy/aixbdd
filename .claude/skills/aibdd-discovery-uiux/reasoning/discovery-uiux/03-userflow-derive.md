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
  - name: fe_intent_bundle
    kind: required_axis
    source: upstream_rp
    required: true
    note: 由 00-fe-intent-sourcing 產出；提供 page_composition / navigation_topology / ux_only_flows / actor_split 作為 userflow 組裝指引
  - name: be_gap_findings
    kind: derived_axis
    source: upstream_rp
    required: true
    note: 由 01-be-sourcing 產出；BG-003 / BG-004 / BG-007 resolution 影響 userflow actor / DECISION / verb
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

對每個 has-ui BEOperation 推導對應的 frontend uat_flow（actor=end-user，nodes=UI verbs + DECISION + terminals），同時 reuse aibdd-discovery 04b-frontend-axes 的 frontend_lens 規格抽 UIVerbBinding[] + AnchorCandidate[]。消費 `fe_intent_bundle.page_compositions` 決定 N:1 / 1:N userflow 組裝；`ux_only_flows` 物化為 UATFlow with `be_op_id: null`；`actor_split` 寫進 UATFlow.actor；BE gap（BG-003 / BG-004 / BG-007）的 chosen_option 決定 DECISION / actor / verb assumption。

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
  - name: fe_intent_bundle
    source:
      kind: upstream_rp
      path: discovery-uiux.00-fe-intent-sourcing
    granularity: 整個 fe_intent_bundle 結構（page_compositions / navigation_topology / ux_only_flows / actor_splits 直接消費）
    required_fields:
      - page_compositions
      - navigation_topology
      - ux_only_flows
      - actor_splits
    completeness_check:
      rule: page_compositions / actor_splits 至少 placeholder 存在；ux_only_flows 可為空 list
      on_missing: STOP
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
      role: "對應一個 has-ui BEOperation 的 frontend userflow，描述 end-user 從 entry 到 terminal 的互動路徑；ux-only-flow 時 be_op_id 為 null"
      fields:
        flow_id: string
        be_op_id: string | null           # 對回 BEOperation.op_id；ux-only-flow 為 null
        composition_id: string | null     # 對回 fe_intent_bundle.page_compositions[].composition_id；無組合時為 null
        actor: string                     # 採 fe_intent_bundle.actor_splits 細分後的 persona；無 split 時為 BE actor verbatim
        entry_trigger: string             # 使用者進入此 flow 的入口（page load / 點 nav 等）
        steps: list<UATFlowStep>
        terminals: list<UATFlowTerminal>
        be_gap_assumption_refs: list<string>  # 對應 BEGapFinding.detect_id（BG-003 / BG-004 / BG-007 採用的 assumption）
      invariants:
        - "be_op_id == null → 必有對應 fe_intent_bundle.ux_only_flows[].flow_slug match"
        - "be_op_id != null → 必對應到 classification 中 has-ui 的 op_id"
        - "至少有 1 個 entry + 1 個 terminal"
        - "actor 來源：fe_intent_bundle.actor_splits.fe_personas 或 BE truth verbatim；禁 AI 自生 actor 名稱"
        - "composition_id 非空 → 同 composition 下的 UATFlow 共享 entry_trigger（or wizard-step 序列）"
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

1. `$composition_lookup` = DERIVE per has-ui op：對應 `fe_intent_bundle.page_compositions` 中包含此 op_id 的 entry（缺則視為 1:1 default）
2. `$actor_lookup` = DERIVE per has-ui op：對應 BE activity actor → 套用 `fe_intent_bundle.actor_splits[be_actor].fe_personas`（缺 split 則 BE actor verbatim）
3. `$be_gap_lookup` = DERIVE per has-ui op：對應 `be_gap_findings.items` 中 BG-003 / BG-004 / BG-007 chosen_option_id
4. `$flows_raw` = DERIVE per has-ui BEOperation：
   - 從 BE `.activity` 找 attribution flow → 把 BE action 序列翻譯成 user-side UATFlowStep（保留順序）
   - 從 BE feature Rule body 找 visual outcome → 補 UATFlowTerminal
   - DECISION 分支 → UATFlowStep.kind=decision + 子 branch 對應 terminal；BG-003 chosen option 為「沿 OpenAPI 4xx 列舉」時，從 OpenAPI 4xx 補 DECISION 分支
   - 套用 `$composition_lookup`：composite cardinality 合併同 composition 下的 UATFlow steps；wizard-step cardinality 串成 sequence；branch-by-entry 拆分為多 UATFlow（共享 be_op_id）
   - 套用 `$actor_lookup`：UATFlow.actor 採 split 後 persona
   - 套用 `$be_gap_lookup`：BG-004 衝突採 chosen actor；BG-007 衝突採 chosen verb；對應 detect_id 寫入 UATFlow.be_gap_assumption_refs
5. `$ux_only_flows` = DERIVE per `fe_intent_bundle.ux_only_flows`：物化為 UATFlow with `be_op_id: null`；steps 由 trigger_quote + proposed_anchor 拼出 minimal `action → terminal` 序列
6. `$ui_verb_bindings` = DERIVE per UATFlowStep（kind == action）：
   - lemma 對應 catalog `ui_verb`；對應不上 → FrontendLensCiC(GAP)
   - 黑名單動詞命中（POST / persist / 200 等）→ FrontendLensCiC(ASM)
7. `$anchor_candidates` = DERIVE per UIVerbBinding：
   - role ← frontend-rule-axes §3 mapping
   - accessible_name ← source_verb + object verbatim quote
   - 同義改寫 → FrontendLensCiC(ASM)
8. `$state_hints` = DERIVE per AnchorCandidate：
   - base ← §5.1 對應 role 預設集
   - domain ← BE activity DECISION 分支推得（loading / empty / error / populated / pristine）
9. `$pattern4_findings` = THINK Pattern 4 Frontend Lens 檢查（backend-verb leak / accessible_name 同義改寫 / role 黑名單 / 自生 anchor）
10. `$clarify_payload` = DERIVE per FrontendLensCiC + step order 模糊：
    - 每筆 finding 補一道 question；id=`flow-Q<n>`；options=[A: 採 BE 來源 verbatim, B: 補 catalog, C: split-flow]（**禁** "改 BE" 字樣）

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE uat_flows + frontend_lens + clarify_payload：
   - `uat_flows = {items: concat($flows_raw, $ux_only_flows)}`
   - `frontend_lens = {ui_verb_bindings: $ui_verb_bindings, anchor_candidates: $anchor_candidates, state_axes_hints: $state_hints, cic_marks: $pattern4_findings, clarify_payload: $clarify_payload}`
2. ASSERT 每個 UATFlow.be_op_id 非 null 時必對應到 classification has-ui 子集；be_op_id == null 時必對應到 `fe_intent_bundle.ux_only_flows`
3. ASSERT 每個 modeled UATFlowStep.kind=action 都有對應 UIVerbBinding；資訊性 step 例外
4. ASSERT 每個 UIVerbBinding 都有對應 AnchorCandidate（informational 例外）
5. ASSERT 無 accessible_name 與 source_quote lemma 不一致
6. ASSERT 每個 UATFlow.be_gap_assumption_refs 條目都能在 `be_gap_findings.items[].detect_id` 找到對應；reasoning 引用 GAP report pointer
7. ASSERT 每筆 clarify question option label 不含 [`../../references/be-gap-handling.md`](../../references/be-gap-handling.md) §3 forbidden phrase

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
    - fe_intent_bundle
    - be_gap_findings
  derived:
    - UATFlow
    - UATFlowStep
    - UATFlowTerminal
    - UIVerbBinding
    - AnchorCandidate
    - FrontendLensCiC
clarifications:
  - clarify_payload   # 非空 → SKILL.md Phase 2 觸發 Seam B clarify-loop
```
