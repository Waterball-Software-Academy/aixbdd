---
rp_type: reasoning_phase
id: discovery.01-source-material
context: discovery
slot: "01"
name: Discovery Sourcing
variant: none
consumes:
  - name: runtime_config
    kind: required_axis
    source: caller
    required: true
produces:
  - name: source_material_bundle
    kind: material_bundle
    terminal: false
  - name: discovery_sourcing_report
    kind: report_model
    terminal: false
  - name: impact_scope
    kind: derived_axis
    terminal: false
downstream:
  - discovery.02-sourcing-clarify
  - discovery.03-activity-analyze
  - discovery.04-activity-clarify
  - discovery.05-atomic-rules
  - discovery.06-atomic-clarify
  - discovery.07-clarification-dimensions
---

# Discovery Sourcing

本 RP 是 Discovery 的唯一 truth sourcing 階段。它把 raw idea 對照 target boundary full truth，產生 evidence matrix 與 impact scope；下游 Activity / Atomic Rules 只能消費此結果，不重新掃 truth 或另建第二份 sourcing。

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: runtime_config
    source:
      kind: caller
      path: arguments.yml + command payload
    granularity: 單次 Discovery 呼叫設定 + raw idea + target truth roots
    required_fields:
      - raw_idea
      - SPECS_ROOT_DIR
      - BOUNDARY_YML
      - PLAN_SPEC
      - PLAN_REPORTS_DIR
      - TRUTH_BOUNDARY_ROOT
      - TRUTH_BOUNDARY_PACKAGES_DIR
      - ACTIVITY_EXT
      - BDD_CONSTITUTION_PATH
    optional_fields:
      - TRUTH_FUNCTION_PACKAGE
      - FEATURE_SPECS_DIR
      - ACTIVITIES_DIR
      - TRUTH_TEST_PLAN_DIR
      - BOUNDARY_SHARED_DSL
      - BOUNDARY_PACKAGE_DSL
      - ACTORS_DIR
      - CONTRACTS_DIR
      - DATA_DIR
      - TEST_STRATEGY_FILE
    completeness_check:
      rule: 在語意分析前已取得 raw idea、target boundary truth root、`packages/` root anchor、plan session report path。
      notes: 「目標 `${TRUTH_FUNCTION_PACKAGE}` slug」可先 unknown；`/aibdd-discovery` Phase 2 bind block MUST 將其具象化並寫回 arguments.yml。
      on_missing: ASK
```

### 1.2 Truth Scope

1. 先把這次 Discovery 真的要看的 truth 範圍收乾淨，只讀 pointer，不搬運內文。
   `$raw_idea` = READ caller 提供的 raw idea 或其引用來源
   `$boundary_meta` = READ `${BOUNDARY_YML}`，定位唯一 target boundary id

2. 再依 boundary truth 的既有結構，補齊這次可能會用到的材料指標；有檔案就讀，沒有就略過，不補腦。
   `$actor_catalog` = READ `${TRUTH_BOUNDARY_ROOT}/actors/**`（存在時讀取）
   `$boundary_map` = READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`（存在時讀取）
   `$contracts` = READ `${TRUTH_BOUNDARY_ROOT}/contracts/**`（存在時讀取）
   `$data_truth` = READ `${TRUTH_BOUNDARY_ROOT}/data/**`（存在時讀取）
   `$shared_dsl` = READ `${BOUNDARY_SHARED_DSL}`（存在時讀取）
   `$package_dsl` = READ `${BOUNDARY_PACKAGE_DSL}`（存在時讀取）
   `$test_strategy` = READ `${TEST_STRATEGY_FILE}`（存在時讀取）
   `$existing_activities` = READ `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/activities/*${ACTIVITY_EXT}`（存在時讀取）
   `$existing_features` = READ `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/features/**/*.feature`（存在時讀取）

3. 這一步只允許留下 pointer、最小 evidence pointer、以及 relevance reason。
   - 不得把 truth 原文抄進來。
   - 不得提前寫 delta / diff。

### 1.3 Evidence Matrix SOP

1. 先把剛剛讀到的 truth 指標整理成一份可判讀的材料清單，標出 artifact 種類與最小定位資訊。
   `$truth_inventory` = DERIVE 每份可讀 truth artifact 的 pointer、artifact kind、minimal locator

2. 再判斷這次 raw idea 在 Discovery 軸上到底是 relevant、uncertain，還是根本 irrelevant。
  `$relevance` = CLASSIFY `$raw_idea` by `DiscoveryRelevance` using [`references/relevance.md`](../../references/relevance.md)

3. 逐列判斷這些 truth 指標跟 raw idea 的關係，分成真的要納入、只作背景、可以排除、或需要回頭澄清。
   `$candidate_evidence` = CLASSIFY 每筆 `$truth_inventory` 與 `$raw_idea` 的關係為 `include | context_only | exclude | clarify_required`

4. 把這些判斷整理成 evidence matrix，讓下游只消費這一份，而不是自己重掃 truth。
   `$evidence_matrix` = DERIVE 帶有 `pointer`、`evidence_pointer`、`reason`、`confidence`、`impact_scope`、`gap`、`use_in_discovery` 的矩陣列

5. 收尾檢查 evidence matrix 是否乾淨可交棒。
   ASSERT every included row has an evidence pointer and a non-empty reason
   ASSERT no row contains copied truth body text
   ASSERT no row contains proposed delta / diff

### 1.4 Impact Scope SOP

1. 從 evidence matrix 與 raw idea 收斂這次真正被影響到的範圍，整理成 impact objects。
   `$impact_scope` = DERIVE 根據 `$evidence_matrix` 與 `$raw_idea` 正規化後的 impact objects

2. 每個 impact object 都要被歸到清楚的類別，避免下游把不同層次的影響混在一起。
   CLASSIFY each impact object into `flow | atomic_rule | actor | state_or_data | operation_trigger | dsl_phrase | dependency_edge | contract_operation | new_behavior`

3. 只要 evidence 足夠，impact granularity 至少要落到 rule / flow / actor / state-or-data / operation-trigger 這一層。
   ASSERT impact granularity reaches at least rule / flow / actor / state-or-data / operation-trigger level when evidence exists

4. 如果這次需求明顯 relevant，但 truth 裡找不到可掛接的錨點，就明確標成 `new_behavior`，不要偷偷補腦。
   IF no truth evidence matches but `$relevance.status != irrelevant`, DERIVE `new_behavior` impact with gap `truth_anchor_missing` or `new_package_required`

5. 所有真的會卡住下游的 gap，都要在這裡先顯式化，讓 `/clarify-loop` 能接得住。
   ASSERT all blocking gaps are explicit and suitable for `/clarify-loop`

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: discovery_sourcing
  elements:
    SourceMaterialBundle:
      role: "正規化後的 Discovery input，不承載 truth copy"
      fields:
        raw_idea: string
        target_boundary:
          id: string
          pointer: string
        target_function_package:
          pointer: string
        filename_axes: object
        relevance: DiscoveryRelevance
      invariants:
        - "必須包含 raw idea、target boundary、target function package、filename axes"
        - "不得包含 truth artifact 原文 copy"
    DiscoverySourcingReport:
      role: "可落到 reports/discovery-sourcing.md 的 report model"
      fields:
        scope: object
        evidence_matrix: EvidenceRow[]
        impact_scope: ImpactScope[]
        gaps: Gap[]
      invariants:
        - "EvidenceRow 只能放 pointer / evidence pointer / reason / confidence / impact_scope / gap / use_in_discovery"
        - "不得寫 delta / diff"
    EvidenceRow:
      role: "raw idea 與 truth pointer 的 relevance judgment"
      fields:
        pointer: string
        evidence_pointer: string
        reason: string
        confidence: high | medium | low
        impact_scope: string[]
        gap: string | none
        use_in_discovery: include | context_only | exclude | clarify_required
    ImpactScope:
      role: "下游 Activity / Atomic Rules 的唯一 upstream impact axis"
      fields:
        kind: flow | atomic_rule | actor | state_or_data | operation_trigger | dsl_phrase | dependency_edge | contract_operation | new_behavior
        pointer: string | null
        reason: string
        gap: string | none
```

## 3. Reasoning SOP

1. 把 raw idea、boundary metadata、target function package、filename axes、以及 relevance 判斷，整成一份下游可以直接消費的 `SourceMaterialBundle`。
   `$source_material_bundle` = DERIVE 根據 `$raw_idea`、boundary metadata、target function package、filename axes、`DiscoveryRelevance` 組成的 `SourceMaterialBundle`

2. 把 evidence matrix 與 impact scope 整成可直接落成 report 的 `DiscoverySourcingReport`。
   `$discovery_sourcing_report` = DERIVE 根據 `$evidence_matrix` 與 `$impact_scope` 組成的 `DiscoverySourcingReport`

3. 收尾檢查這兩份核心產物是否已達到交棒條件。
   ASSERT `$discovery_sourcing_report` conforms to [`references/contracts/discovery-sourcing-report.md`](../../references/contracts/discovery-sourcing-report.md)
   ASSERT `$source_material_bundle.relevance.status` is `relevant` or `uncertain` before continuing

## 4. Material Reducer SOP

1. 把 `SourceMaterialBundle`、`DiscoverySourcingReport`、`ImpactScope` 收成一份最終的 `discovery_sourcing` package。
   `$reducer_output` = DERIVE 由 `SourceMaterialBundle`、`DiscoverySourcingReport`、`ImpactScope` 組成的最終 `discovery_sourcing` package

2. 最後確認 reducer 沒有把必要資訊漏掉，也沒有把不該留下的東西帶進終稿。
   ASSERT `source_material_bundle`, `discovery_sourcing_report`, and `impact_scope` are all represented
   ASSERT no truth copy and no delta / diff survived reduction

Return:

```yaml
status: complete | blocked
produces:
  source_material_bundle:
    raw_idea: string
    target_boundary:
      id: string
      pointer: string
    target_function_package:
      pointer: string
    filename_axes: object
    relevance: DiscoveryRelevance
  discovery_sourcing_report:
    scope: {}
    evidence_matrix: []
    impact_scope: []
    gaps: []
  impact_scope:
    impacts: []
    blocking_gaps: []
traceability:
  inputs:
    - runtime_config
  derived:
    - SourceMaterialBundle
    - DiscoverySourcingReport
    - ImpactScope
```
