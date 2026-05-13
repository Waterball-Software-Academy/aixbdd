---
rp_type: reasoning_phase
id: discovery-uiux.01-be-sourcing
context: discovery-uiux
slot: "01"
name: Backend Truth Sourcing
variant: none
consumes:
  - name: be_features
    kind: required_axis
    source: filesystem
    required: true
  - name: be_activities
    kind: required_axis
    source: filesystem
    required: true
  - name: be_contracts
    kind: required_axis
    source: filesystem
    required: false
    note: 缺檔不致命；降低分類精度時於 sourcing report 標記
  - name: runtime_context
    kind: required_axis
    source: skill_global
    required: true
  - name: backend_input_contract_ref
    kind: reference
    source: reference
    required: true
    path: ../../references/backend-input-contract.md
produces:
  - name: be_truth_bundle
    kind: material_bundle
    terminal: false
  - name: operation_inventory
    kind: derived_axis
    terminal: false
downstream:
  - discovery-uiux.02-operation-classify
---

# Backend Truth Sourcing

從 sibling backend boundary 已讀入的 `.feature` / `.activity` / contracts artifacts 機械抽取 BE operation inventory（每筆含 source / verb / object / actors / uat_flow attribution），不做 has-ui 分類（屬下游 02）。

---

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: be_features
    source:
      kind: filesystem
      path: ${SPECS_ROOT_DIR}/${UIUX_BACKEND_BOUNDARY_ID}/packages/**/*.feature
    granularity: 每個 feature file 一筆，含 file path + parsed AST（Background / Rule / Scenario / Examples）
    required_fields:
      - path
      - background_actor
      - rules
    completeness_check:
      rule: length ≥ 1
      on_missing: STOP
  - name: be_activities
    source:
      kind: filesystem
      path: ${SPECS_ROOT_DIR}/${UIUX_BACKEND_BOUNDARY_ID}/packages/**/activities/*.activity
    granularity: 每個 activity file 一筆，含 actor / action nodes / decision nodes / terminals
    required_fields:
      - path
      - actor
      - nodes
    completeness_check:
      rule: length ≥ 1
      on_missing: STOP
  - name: be_contracts
    source:
      kind: filesystem
      path: ${SPECS_ROOT_DIR}/${UIUX_BACKEND_BOUNDARY_ID}/contracts/**/*.{yml,yaml}
    granularity: OpenAPI / AsyncAPI / GraphQL schema 各一份
    required_fields:
      - path
    completeness_check:
      rule: length ≥ 0（缺檔不致命，但會降低分類精度）
      on_missing: mark_unknown
  - name: runtime_context
    source:
      kind: skill_global
    granularity: FE TLB 全貌 + arguments.yml 解析後的執行設定
    required_fields:
      - TLB.id
      - TLB.role
      - UIUX_BACKEND_BOUNDARY_ID
    completeness_check:
      rule: TLB.role == "frontend" ∧ UIUX_BACKEND_BOUNDARY_ID 為非空字串
      on_missing: STOP
```

### 1.2 Search SOP

1. `$be_features_parsed` = PARSE 每個 `.feature` file 抽 Background actor + Rules + tags
2. `$be_activities_parsed` = PARSE 每個 `.activity` file 抽 header actor + action nodes + decision nodes + terminals
3. `$be_contracts_parsed` = PARSE 每個 contract 檔（OpenAPI 抽 paths × methods × operationId × security × tags × x-actors / x-uat-flow / x-no-ui / x-frontend-binding extensions）
4. ASSERT 所有 `.feature` 都成功 parse；任一 parse 失敗回 CiC(BDY)

---

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: operation_inventory
  element_rules:
    element_vs_field:
      element: "後續 02 classify 需要獨立評分 / 03 userflow-derive 需要直接引用的 BE operation"
      field: "只能隸屬於某個 BEOperation 的屬性（verb / object / actor 等）"
  elements:
    BEOperation:
      role: "後端真實 operation 的最小可引用單位；包含 OpenAPI endpoint、activity action、feature rule 三種來源"
      fields:
        op_id: string                # OpenAPI operationId 或 method:path 或 activity action id 或 feature rule id
        source: enum                 # openapi-endpoint | activity-action | feature-rule
        source_path: string          # 對應檔案 path
        verb: string                 # source 內動詞 lemma
        object: string               # source 內 object 名詞片語
        actors: list<string>         # 從 security / tags / actor header / Background actor 推得
        uat_flow_attribution: string | null  # BE activity flow id 或 null
        side_effects: list<string>   # description / x-side-effects 抽得
        request_shape_ref: string | null    # OpenAPI $ref or schema pointer
        response_shape_ref: string | null
      invariants:
        - "op_id 在 inventory 內唯一"
        - "source 必須是 enum 三值之一"
        - "verb / object 必須是 BE truth verbatim（不得同義改寫）"
    BEOperationCiC:
      role: "BE truth parse 過程中發現的缺欄 / 矛盾 / 邊界外便條紙；下游 02 看到後可選擇納入 ambiguous 清單"
      fields:
        type: enum                   # GAP | ASM | BDY | CON
        op_id: string
        message: string
      invariants:
        - "type 必為 enum 四值之一"
```

---

## 3. Reasoning SOP

1. `$bundle` = READ be_truth_files 後得到 features + activities + contracts in-memory 結構
2. `$openapi_ops` = DERIVE BEOperation list ← 每條 `paths.<route>.<method>`；source="openapi-endpoint"
3. `$activity_ops` = DERIVE BEOperation list ← 每個 `.activity` action node；source="activity-action"
4. `$feature_ops` = DERIVE BEOperation list ← 每條 Rule body（取主要動詞 + object）；source="feature-rule"
5. `$inventory_raw` = DERIVE union(`$openapi_ops`, `$activity_ops`, `$feature_ops`)；deduplicate by 同源 op_id
6. `$cic_marks` = THINK 標 BEOperationCiC：
   - 缺 actor / security → CiC(GAP)
   - openapi 與 activity 對應不上 → CiC(BDY)
   - 多 source 同一 op_id 但 verb 不一致 → CiC(CON)

---

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE be_truth_bundle + operation_inventory：
   - `be_truth_bundle = {features: $be_features_parsed, activities: $be_activities_parsed, contracts: $be_contracts_parsed, boundary_id: runtime_context.UIUX_BACKEND_BOUNDARY_ID}`
   - `operation_inventory = {items: $inventory_raw, cic_marks: $cic_marks}`
2. ASSERT length(`$reducer_output.operation_inventory.items`) ≥ 1
3. ASSERT 每筆 BEOperation invariants 成立（unique op_id / source enum / verbatim verb-object）

Return:

```yaml
status: complete | needs_clarification | blocked
produces:
  be_truth_bundle:
    features: []
    activities: []
    contracts: []
    boundary_id: string
  operation_inventory:
    items: []        # BEOperation[]
    cic_marks: []    # BEOperationCiC[]
traceability:
  inputs:
    - be_truth_files
    - runtime_context
  derived:
    - BEOperation
    - BEOperationCiC
clarifications:
  - none             # 此 RP 不直接 ASK；ambiguous 都標 CiC 給 02 處理
```
