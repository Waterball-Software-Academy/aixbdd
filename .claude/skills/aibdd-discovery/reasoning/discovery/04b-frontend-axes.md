---
rp_type: reasoning_phase
id: discovery.04b-frontend-axes
context: discovery
slot: "04b"
name: Frontend Axes
variant: conditional
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
    note: 需含 target_boundary.role 以判定是否啟動
  - name: impact_scope
    kind: required_axis
    source: upstream_rp
    required: true
  - name: frontend_rule_axes
    kind: reference
    source: reference
    required: true
    path: ../../references/rules/frontend-rule-axes.md
  - name: hallucination_detection_checklist
    kind: reference
    source: reference
    required: true
produces:
  - name: frontend_lens
    kind: derived_axis
    terminal: false
    note: TLB.role != "frontend" 時為 null；下游 atomic-rules 將以 null 跳過 frontend 條款
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: activity action 無法被 UI verb catalog 涵蓋、accessible_name 與 source_quote lemma 不一致、或 role 無法判定時輸出題目
downstream:
  - discovery.05-atomic-rules
---

# Frontend Axes 草稿

從 activity actions 機械推導出 atomic-rules 撰寫時可用的 UI 動詞集 + 每個 action 的 anchor 候選；強迫後續 rule 草稿在純前端 boundary 下不退化成 backend command 的轉錄。本 RP **不**承擔視覺設計（component / state matrix / frame composition 由下游 `/aibdd-uiux-discovery` 負責）；本 RP 只負責**讓 rule 出生時就帶 UI 詞性與 anchor 鉤子**。

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: activity_analyses
    source:
      kind: upstream_rp
      path: discovery.03-activity-analyze
    granularity: 每個 modeled=true 的 uat_flow 一筆 activity_analysis
    required_fields:
      - items
    completeness_check:
      rule: Seam A 已通過（activity clarify_payload.questions 為空）；否則此 RP 不應啟動
      on_missing: STOP
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: raw idea + target boundary + function package traceability
    required_fields:
      - raw_idea
      - target_boundary
      - target_function_package
    extra_required_fields:
      - target_boundary.role
    completeness_check:
      rule: target_boundary.role 必須存在且為 enum；否則交 clarify
      on_missing: ASK
  - name: impact_scope
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: flow / actor / state / operation / rule impacts
    required_fields:
      - impacts
```

### 1.2 Search SOP

1. 讀取此輪要用的三條主軸與兩份參考。
   `$activity_analyses` = READ activity_analyses（僅取 `modeled=true`）
   `$bundle` = READ source_material_bundle
   `$impact_scope` = READ impact_scope
   `$ui_verb_catalog` = READ [`../../references/rules/frontend-rule-axes.md`](../../references/rules/frontend-rule-axes.md) §2 UI Verb Catalog
   `$anchor_rules` = READ [`../../references/rules/frontend-rule-axes.md`](../../references/rules/frontend-rule-axes.md) §4 Anchor Naming Rules

2. 啟動 gate；非 frontend boundary 直接 short-circuit。
   `$role` = READ `$bundle.target_boundary.role`
   IF `$role` not in {"frontend"}: SET `$frontend_lens = null`; SKIP to §4 Reducer
   IF `$role` 缺漏或非 enum: APPEND clarify question `fea-Q0` 詢問 boundary role；SKIP to §4 Reducer with `clarify_payload` non-empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: frontend_lens
  element_rules:
    element_vs_field:
      element: "後續 atomic-rules 必須能引用、且 Pattern 4 Frontend Lens 會核對的單位"
      field: "只能隸屬於某個 anchor candidate 或 ui_verb binding 的屬性"
  elements:
    UIVerbBinding:
      role: "把 activity action 的動詞綁到 UI verb catalog 的一條對應"
      fields:
        action_id: string
        uat_flow_id: string
        source_verb: string
        ui_verb: enum
        category: input | state-change | feedback | visual | navigation
      invariants:
        - "ui_verb 必須在 catalog enum 內，禁自創"
        - "source_verb 必須是 activity action 動詞 verbatim quote"
    AnchorCandidate:
      role: "下游 uiux-discovery 與 form-story-spec 將直接消費的 binding 鉤子起點"
      fields:
        anchor_id: string             # 必須等於對應 activity action 的 action_id
        role: enum
        accessible_name: string
        source_quote: string
        interactivity: interactive | informational
        state_axes_hint:
          base: list<enum>
          domain: list<enum>
      invariants:
        - "anchor_id 必須等於對應 activity action 的 action_id（無例外；多 frame 情境下同一 action 仍共用同一 anchor_id，禁分裂命名）；此規約讓 05-atomic-rules step 2 的 LOOKUP `anchor_id == $rule.action_id` 為確定性 join"
        - "每個 modeled activity action node 至少對應一個 AnchorCandidate；informational node 例外可標 interactivity=informational"
        - "accessible_name 必須對齊 source_quote 的動詞詞素（lemma 一致；正規化見 frontend-rule-axes §4.2）"
        - "role 必須來自 frontend-rule-axes §3 mapping 的 enum；禁出現 generic / div / span"
    FrontendLensCiC:
      role: "activity action 無法被 catalog 涵蓋、或 role 不能判定時的便條紙"
      fields:
        type: GAP | ASM | BDY | CON
        action_id: string
        message: string
      invariants:
        - "必須保留到 frontend_lens.cic_marks；下游 atomic-rules 可參考但不負責解決"
```

## 3. Reasoning SOP

1. 把每個 modeled activity action 對到 catalog 的 UI verb；無法對應就標 CiC，不自創 verb。
   `$ui_verb_bindings` = DERIVE per `$activity_analyses.items[*].activity.nodes[]`：
   - 從 action 動詞 lemma 查 catalog `ui_verb` 對應
   - 若 action 是純資訊呈現（如「使用者看到退款摘要」），category=`visual`，ui_verb=`render`
   - 若 action 涉及跨頁路由，category=`navigation`，ui_verb=`navigate`
   LOOP per node without match:
   1.1 APPEND `FrontendLensCiC{type=GAP, action_id, message="action verb 不在 UI verb catalog；可能是 backend command 誤入 frontend boundary，或 catalog 需擴充"}`

2. 為每個 action 推 anchor candidate；role 取自 catalog 對應規則，accessible_name 取自 source verb + object。
   `$anchor_candidates` = DERIVE per action：
   - role ← frontend-rule-axes §3（ui_verb → role mapping；object 觸發例外 role 時使用例外）
   - accessible_name ← source verb phrase + object（verbatim；禁同義改寫）
   - interactivity ← catalog 標記
   LOOP per action with ambiguous role:
   2.1 APPEND `FrontendLensCiC{type=BDY, action_id, message="同一 action 對應多個合法 role；需 clarify"}`

3. 為每個 anchor 推 state axes hint（base + domain），下游 uiux-discovery 不必再從頭推導。
   `$state_hints` = DERIVE per anchor：
   - base ← frontend-rule-axes §5.1 對應 role 的預設集
   - domain ← 從 `$activity_analyses` DECISION 分支 + `$impact_scope.impacts` 抽（loading / empty / error / populated / pristine 之中對應者）

4. 對全體 lens 做 hallucination 檢查（Pattern 4 Frontend Lens 預擋；checklist 見 references/rules/hallucination-detection-checklist.md §Pattern 4）。
   `$pattern4_findings` = THINK 依下列檢查：
   - frontend boundary 內冒出 backend verb（POST / persist / 200 / database / API / commit transaction 等，黑名單見 frontend-rule-axes §2.1）→ flag
   - `accessible_name` 與 `source_quote` lemma 不一致（同義改寫；判定見 frontend-rule-axes §4.2）→ flag
   - role ∈ {generic, div, span, presentation, none} → flag
   - 自生未在 activity action 出現的 anchor → flag
   LOOP per finding:
   4.1 APPEND `FrontendLensCiC{type=ASM, action_id, message=finding}`

5. 組 clarify_payload；無 finding 則空陣列。
   `$clarify_payload` = DERIVE per `FrontendLensCiC`：
   - id=`fea-Q<n>`, concern=message, options=[A:catalog 擴充, B:重寫 activity action 對齊 catalog, OTHER:重新描述], default=B
   IF no finding: SET `$clarify_payload.questions = []`

6. 本 RP 不直接 ASK；非空時由 SKILL.md Phase 2 Seam C 觸發 `/clarify-loop`。

## 4. Material Reducer SOP

1. 整出 `frontend_lens`：UIVerbBinding[] + AnchorCandidate[] + FrontendLensCiC[] + clarify_payload。
   `$reducer_output` = DERIVE 由 `$ui_verb_bindings`, `$anchor_candidates`, `$state_hints`, `$pattern4_findings`, `$clarify_payload` 組成的 `frontend_lens`
   IF TLB.role != "frontend": SET `$reducer_output = null`

2. ASSERT 結構合法（僅在 lens non-null 時生效）。
   IF `$reducer_output` is non-null:
   2.1 ASSERT every modeled activity action 至少一個 AnchorCandidate 或 informational 標記
   2.2 ASSERT every AnchorCandidate.role ∈ frontend-rule-axes §3 mapping enum，且不在 §4.4 黑名單
   2.3 ASSERT no accessible_name 與 source_quote lemma 不一致（依 §4.2 正規化規則）
   2.4 ASSERT clarify_payload 欄位並列輸出（即使 questions 為空也要保留欄位）

Return:

```yaml
status: complete | needs_clarification | skipped
produces:
  frontend_lens:
    ui_verb_bindings: []
    anchor_candidates: []
    state_axes_hints: []
    cic_marks: []
    clarify_payload:
      questions: []
traceability:
  inputs:
    - activity_analyses
    - source_material_bundle
    - impact_scope
  derived:
    - UIVerbBinding
    - AnchorCandidate
    - FrontendLensCiC
clarifications:
  - clarify_payload   # 非空時由 SKILL.md Phase 2 Seam C 觸發 /clarify-loop
```
