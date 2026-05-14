---
rp_type: reasoning_phase
id: aibdd-spec-by-example-analyze.05-build-coverage-handoff
context: aibdd-spec-by-example-analyze
slot: "05"
name: Build Coverage Handoff
variant: plan-dsl-trace
consumes:
  - name: ScenarioStructurePlan
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: IndexedTruthModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: FrontendContextHandoff
    kind: derived_axis
    source: delegated_helper
    required: false
produces:
  - name: ReasonHandoffBundle
    kind: derived_axis
    terminal: true
downstream: []
---

# Build Coverage Handoff

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: ScenarioStructurePlan
    source:
      kind: upstream_rp
    required_fields:
      - groups[].feature_path
      - groups[].rule_anchor
      - groups[].precondition_setup
      - groups[].merge_decision
      - groups[].example_body_shape
      - groups[].rows
  - name: IndexedTruthModel
    source:
      kind: upstream_rp
    required_fields:
      - plan_dsl_index.entries
      - dsl_l1_pattern_index.patterns_by_entry_id
      - contract_index.operations
      - files[]
  - name: FrontendContextHandoff
    source:
      kind: delegated_helper
    required: false
    required_fields_when_present:
      - exit_ok
      - required_clause_candidates[]
      - context_binding_trace[]
```

### 1.2 Search SOP

1. `$scenario_plan` = READ `ScenarioStructurePlan`
2. `$indexed_truth` = READ `IndexedTruthModel`
3. `$frontend_context_handoff` = READ optional `FrontendContextHandoff`
4. ASSERT `$scenario_plan.groups[]` is present
5. ASSERT `$indexed_truth.plan_dsl_index` is present
6. ASSERT `$indexed_truth.dsl_l1_pattern_index` is present
7. IF `$frontend_context_handoff` present:
   7.1 ASSERT `$frontend_context_handoff.exit_ok == true`
   7.2 ASSERT every executable `required_clause_candidate.dsl_entry_id` exists in `$indexed_truth.plan_dsl_index.entries[].id`
   7.3 ASSERT every executable `required_clause_candidate.dsl_l1_pattern` exists in `$indexed_truth.dsl_l1_pattern_index.patterns_by_entry_id[required_clause_candidate.dsl_entry_id]`
8. LOOP per `$group` in `$scenario_plan.groups[]` until all groups are reduced
   8.1 `$dsl_entries` = MATCH `$group.feature_path` against `plan_dsl_index.feature_to_entries`（path 正規化為相對 `${FEATURE_SPECS_DIR}`）
   8.2 IF `$dsl_entries` is empty:
       8.2.1 `$cic` = DERIVE CiC(GAP) "no matching /aibdd-plan DSL entry"
       8.2.2 CONTINUE
   8.3 ASSERT each candidate `$dsl_entry.id` has non-empty `dsl_l1_pattern_index.patterns_by_entry_id[$dsl_entry.id]`
   END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: ReasonHandoffBundle
  element_rules:
    element_vs_field:
      element: "A handoff unit consumed by feature formulation or coverage writing"
      field: "A scalar binding, path, dimension, or marker nested under a handoff unit"
  elements:
    BDDExample:
      role: "Represent one renderable Scenario or Scenario Outline semantic unit"
      fields:
        example_id: "string"
        feature_path: "path"
        rule_anchor: "string"
        scenario_kind: "Scenario|ScenarioOutline|Example"
        annotations_block: "internal metadata string"
        precondition_setup: "SetupBinding[]"
        frontend_context_refs: "string[]"
        steps: "ClauseBinding[]"
        rows: "dict[]"
      invariants:
        - "Each BDDExample maps to at least one atomic Rule"
        - "Examples rows contain concrete values"
        - "Each BDDExample has precondition setup bindings or setup CiC before the first When"
        - "web-frontend BDDExamples include hard frontend context clause candidates before the target operation when provided by FrontendContextHandoff"
        - "Each BDDExample includes only assertion clauses allowed by ScenarioStructureGroup.example_body_shape"
    SetupBinding:
      role: "Bind required precondition state to an existing setup source or explicit CiC"
      fields:
        entity_or_state: "string"
        identity: "dict<string,string>"
        setup_source_kind: "given_dsl|shared_dsl|dbml_seed|cic_gap"
        setup_source_ref: "string"
        dsl_entry_id: "string|null"
        cic: "CiCMarker[]"
      invariants:
        - "A generated Given step is legal only when setup_source_kind is given_dsl or shared_dsl and dsl_entry_id exists"
        - "If setup_source_kind is cic_gap, no executable Given step may be rendered for that setup item"
    ClauseBinding:
      role: "Bind one Given/When/Then sentence to a plan DSL L1 canonical pattern and physical surface"
      fields:
        clause_id: "string"
        keyword: "Given|When|Then|And|But"
        preset_name: "string"
        dsl_l1_pattern: "string"
        parameters: "dict"
        dsl_entry_id: "string"
        binding_keys: "string[]"
        contract_refs: "string[]"
        data_refs: "string[]"
        source_kind: "rule_example|frontend_context"
      invariants:
        - "dsl_l1_pattern must appear in IndexedTruthModel.dsl_l1_pattern_index.patterns_by_entry_id for the selected dsl_entry_id"
        - "dsl_entry_id must exist in IndexedTruthModel.plan_dsl_index"
        - "binding_keys must exist in the referenced DSL entry L4 bindings"
        - "No ClauseBinding may reference a sentence invented outside plan DSL/shared DSL"
        - "frontend_context ClauseBindings must map back to FrontendContextHandoff.required_clause_candidates"
    CoverageRow:
      role: "Record one example-layer coverage cell"
      fields:
        coverage_type: "example"
        rule_id: "string"
        dimension: "string"
        example_id: "string"
        feature_path: "path"
      invariants:
        - "coverage_type is always example in this RP"
        - "rule_id matches the atomic Rule anchor used by the BDDExample, not operation-level dsl.source.rule_id"
    DslBindingTrace:
      role: "Expose how examples consume plan-owned DSL without mutating it"
      fields:
        dsl_entry_id: "string"
        feature_path: "path"
        binding_key: "string"
        binding_kind: "param|datatable|default|assertion|response|data|route|ui"
        target: "string"
      invariants:
        - "Every non-comment Scenario step and Examples column has a trace"
    CiCMarker:
      role: "Expose unresolved gaps or conflicts to the caller without hidden assumptions"
      fields:
        kind: "GAP|ASM|BDY|CON"
        where: "string"
        text: "string"
```

## 3. Reasoning SOP

1. `$mdc` = DERIVE Modify/Delete/Create operations by comparing current feature and coverage example layer with `ScenarioStructurePlan`
2. LOOP per `$group` in `ScenarioStructurePlan.groups[]` until all groups are transformed
   2.1 `$dsl_entries` = MATCH `$group.feature_path` to `IndexedTruthModel.plan_dsl_index.feature_to_entries`（path 正規化為相對 `${FEATURE_SPECS_DIR}`）
  2.2 `$example` = DERIVE `BDDExample` from `$group`
  2.3 `$setup_bindings` = DERIVE `SetupBinding[]` from `$group.precondition_setup`
  2.4 ASSERT every `$setup_binding` with executable Given has `dsl_entry_id` in `IndexedTruthModel.plan_dsl_index`
  2.5 ASSERT every `$setup_binding` with `setup_source_kind == cic_gap` renders only non-feature internal notes in coverage / handoff and no executable Given step
  2.6 `$frontend_context_steps` = DERIVE ordered context clauses from `$group.example_body_shape.required_context_candidate_ids` by matching `FrontendContextHandoff.required_clause_candidates[]`
      2.6.1 IF candidate id missing: ADD CiC(CON) "frontend context candidate missing from delegated handoff" and STOP
      2.6.2 ASSERT every `$frontend_context_steps[].preset_name == "web-frontend"`
      2.6.3 ASSERT every `$frontend_context_steps[].dsl_l1_pattern` exists in `IndexedTruthModel.dsl_l1_pattern_index.patterns_by_entry_id[$frontend_context_steps[].dsl_entry_id]`
  2.7 `$rule_steps` = FILTER clauses by `$group.example_body_shape.allowed_then_entry_ids` and operation clause; exclude `$group.example_body_shape.forbidden_then_entry_ids`
  2.8 `$example.steps` = MERGE `$frontend_context_steps` before target operation clauses plus `$rule_steps`, preserving candidate order and avoiding duplicate DSL-pattern/parameter pairs
  2.9 LOOP per `$step` in `$example.steps` until every clause is bound
       2.9.1 `$dsl_entry` = SELECT matching DSL entry by operation/sentence scope OR by `$step.dsl_entry_id` when `$step.source_kind == frontend_context`
       2.9.2 `$preset_name` = READ `$dsl_entry.L4.preset.name`（trace / `/aibdd-red` asset routing；非 BDD Analyze markdown preset）
       2.9.3 `$dsl_l1_pattern` = MATCH `$step`（canonicalized）against `IndexedTruthModel.dsl_l1_pattern_index.patterns_by_entry_id[$dsl_entry.id]`
       2.9.4 IF `$dsl_l1_pattern` is missing:
             2.9.4.1 `$cic` = DERIVE CiC(GAP) "step 無對應 plan DSL L1 pattern"
             2.9.4.2 CONTINUE
       2.9.5 `$binding_keys` = DERIVE DSL binding keys consumed by `$step` / Examples row
       2.9.6 ASSERT every `$binding_keys` member exists in `$dsl_entry.L4.param_bindings`, `datatable_bindings`, `default_bindings`, or `assertion_bindings`
       2.9.7 `$contract_refs` = DERIVE contract targets from DSL binding targets and OpenAPI source refs
       2.9.8 `$data_refs` = DERIVE DBML targets for state setup/verifier clauses where applicable
       2.9.9 `$source_kind` = DERIVE `frontend_context` iff `$step` came from `FrontendContextHandoff.required_clause_candidates[]`, else `rule_example`
       2.9.10 `$clause_binding` = DERIVE `ClauseBinding` from `$step`, `$preset_name`, `$dsl_l1_pattern`, `$dsl_entry.id`, `$binding_keys`, `$contract_refs`, `$data_refs`, `$source_kind`
       END LOOP
   2.10 ASSERT `$example.steps` contains no forbidden Then entry for the current `$group.rule_anchor`
   2.11 ASSERT frontend context Then candidates are allowed only when they are the delegated `observable_result` for this example, not unrelated state/response assertions
   2.12 `$coverage_rows` = DERIVE `CoverageRow` entries for each `(atomic rule anchor, dimension, example_id)` cell
   2.13 ASSERT every rule-dimension cell has either one `CoverageRow` or CiC/N/A reason
   2.14 `$dsl_binding_trace` = DERIVE trace values from all setup, frontend context, clause, and row bindings
   2.15 ASSERT no `DslEntry` is created or mutated by this RP
   END LOOP
3. `$reason_handoff` = DERIVE `ReasonHandoffBundle` from `$mdc`, BDDExample, ClauseBinding, CoverageRow, DslBindingTrace, and CiCMarker elements
4. ASSERT no Rule body, feature path, feature filename, DSL, contract, data, or test-strategy artifact is changed by this RP

## 4. Material Reducer SOP

1. EMIT `ReasonHandoffBundle` with:
   1.1 `mdc`: Modify/Delete/Create operations
   1.2 `examples[]`: all `BDDExample` elements
   1.3 `clause_bindings[]`: all `ClauseBinding` elements
   1.4 `coverage_rows[]`: all `CoverageRow` elements
   1.5 `dsl_binding_trace[]`: all `DslBindingTrace` elements
   1.6 `cic_markers[]`: all `CiCMarker` elements
   1.7 `exit_ok`: boolean
2. ASSERT every Rule has `type`, `techniques`, and `dimensions` metadata carried from upstream
3. ASSERT every Rule has values or CiC carried from upstream
4. ASSERT every BDDExample has `precondition_setup` with setup source bindings or CiC(GAP)
5. ASSERT every Outline has `merge_decision` carried from upstream
6. ASSERT coverage matrix cells `(rule × dimension)` have `CoverageRow` or CiC/N/A reason
7. ASSERT every executable setup / Given / When / Then / And `ClauseBinding.dsl_l1_pattern` exists in `dsl_l1_pattern_index.patterns_by_entry_id[ClauseBinding.dsl_entry_id]`
8. ASSERT every executable setup / Given / When / Then / And `ClauseBinding.dsl_entry_id` exists in `IndexedTruthModel.plan_dsl_index`
9. ASSERT every Examples column has a `DslBindingTrace` or CiC reason
10. ASSERT no Example renders response and state Then clauses together unless `ScenarioStructureGroup.example_body_shape` explicitly marks one clause as a dynamic-id bridge
11. ASSERT every `frontend_context` ClauseBinding traces to `FrontendContextHandoff.required_clause_candidates[]`
12. ASSERT no web-backend example contains frontend-only `route-given`, `ui-action`, `ui-readmodel-then`, `url-then`, `api-call-then`, or `mock-state-then` unless its DSL entry preset is `web-frontend`
