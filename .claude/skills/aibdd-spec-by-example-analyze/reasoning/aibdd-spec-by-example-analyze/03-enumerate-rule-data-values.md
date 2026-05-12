---
rp_type: reasoning_phase
id: aibdd-spec-by-example-analyze.03-enumerate-rule-data-values
context: aibdd-spec-by-example-analyze
slot: "03"
name: Enumerate Rule Data Values
variant: plan-dsl-driven
consumes:
  - name: RuleStrategyBundle
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: IndexedTruthModel
    kind: derived_axis
    source: upstream_rp
    required: true
produces:
  - name: RuleTestDataBundle
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-spec-by-example-analyze.04-plan-scenario-structure
---

# Enumerate Rule Data Values

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: RuleStrategyBundle
    source:
      kind: upstream_rp
    required_fields:
      - strategies[].feature_path
      - strategies[].rule_anchor
      - strategies[].techniques
      - strategies[].dimensions
  - name: PlanDslIndex
    source:
      kind: IndexedTruthModel
      path: "plan_dsl_index"
    required_fields:
      - entries[].id
      - entries[].L1
      - entries[].L4.surface_kind
      - entries[].L4.param_bindings
      - entries[].L4.datatable_bindings
      - entries[].L4.default_bindings
      - entries[].L4.assertion_bindings
      - entries[].L4.source_refs
  - name: ContractIndex
    source:
      kind: IndexedTruthModel
      path: "contract_index"
    required_fields:
      - operations
      - required_inputs
      - response_fields
  - name: DataIndex
    source:
      kind: IndexedTruthModel
      path: "data_index"
    required: false
```

### 1.2 Search SOP

1. `$strategy_bundle` = READ `RuleStrategyBundle`
2. `$indexed_truth` = READ `IndexedTruthModel`
3. ASSERT `$indexed_truth.plan_dsl_index.feature_to_entries` is present
4. ASSERT `$indexed_truth.contract_index` is present for operation-backed DSL entries
5. LOOP per `$strategy` in `$strategy_bundle.strategies` until all rules are enumerated
   5.1 IF `$strategy.cic` blocks enumeration:
       5.1.1 `$blocked_data` = DERIVE `RuleTestData` carrying the CiC marker
       5.1.2 CONTINUE
   5.2 `$dsl_entries` = MATCH `$strategy.feature_path` against `PlanDslIndex.feature_to_entries`
   5.3 IF `$dsl_entries` is empty:
       5.3.1 `$cic` = DERIVE CiC(GAP) "no plan DSL entry for feature"
       5.3.2 CONTINUE
   5.4 `$precondition_setup` = DERIVE required existing entities/states from Rule text, operation inputs, DBML targets, and matching DSL source refs
   5.5 ASSERT every required setup item has a setup source: matching Given-capable DSL entry, shared DSL entry, DBML seed fixture declared by test strategy, or CiC(GAP)
   5.6 `$binding_surface` = DERIVE visible binding keys from `param_bindings`, `datatable_bindings`, `default_bindings`, and `assertion_bindings`
   5.7 `$contract_surface` = DERIVE OpenAPI fields from `L4.source_refs.contract`
   5.8 ASSERT every When input value maps to one binding key in `param_bindings` / `datatable_bindings` / `default_bindings`
   5.9 ASSERT every Then expectation maps to `assertion_bindings`, OpenAPI response field, or DBML state field
   END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: RuleTestDataBundle
  element_rules:
    element_vs_field:
      element: "A per-Rule set of concrete test data rows consumed by scenario planning"
      field: "A value, dimension label, binding trace, or technique-specific note nested under RuleTestData"
  elements:
    RuleTestData:
      role: "Bind one RuleStrategy to concrete Given/When/Then value sets using plan DSL truth"
      fields:
        feature_path: "path"
        rule_anchor: "string"
        dsl_entry_ids: "string[]"
        precondition_setup: "PreconditionSetup[]"
        given_value_sets: "ValueSet[]"
        when_value_sets: "ValueSet[]"
        then_expect_sets: "ExpectationSet[]"
        binding_trace: "BindingTrace[]"
        technique_notes: "dict<string,string>"
        cic: "CiCMarker[]"
      nested_fields:
        PreconditionSetup:
          entity_or_state: "string"
          identity: "dict<string,string>"
          required_for: "rule_anchor|example_id|clause_id"
          setup_source_kind: "given_dsl|shared_dsl|dbml_seed|cic_gap"
          setup_source_ref: "string"
          dsl_entry_id: "string|null"
          cic: "CiCMarker[]"
        ValueSet:
          dimension: "string"
          technique: "string"
          payload: "dict"
          binding_keys: "string[]"
        ExpectationSet:
          dimension: "string"
          technique: "string"
          payload: "dict"
          binding_keys: "string[]"
          target_refs: "string[]"
        BindingTrace:
          dsl_entry_id: "string"
          binding_key: "string"
          binding_kind: "param|datatable|default|assertion|response|data"
          target: "string"
      invariants:
        - "Every Example must have a PreconditionSetup analysis before When value enumeration"
        - "Every required existing entity/state has a concrete business identity"
        - "If no existing DSL/shared/seed source can establish the required state, emit CiC(GAP) and do not invent a Given sentence"
        - "Every declared dimension has at least one concrete value or a CiC marker"
        - "Every When payload key traces to a plan DSL input binding"
        - "Every Then payload key traces to assertion_bindings, response schema, or DBML"
        - "BVA rows must include boundary values beyond happy_path"
        - "Error Guessing rows must not replace rule-derived rows"
```

## 3. Reasoning SOP

1. LOOP per `$strategy` in `RuleStrategyBundle.strategies[]` until all strategies are reduced
   1.1 `$dsl_entries` = MATCH DSL entries by `$strategy.feature_path`
   1.2 `$operation_entries` = FILTER `$dsl_entries` where `L4.surface_kind == operation`
   1.3 `$precondition_setup` = DERIVE required setup items:
       - existing entities named by the Rule text (for example: student, journey, stage)
       - aggregate rows required by operation `param_bindings`
       - DBML rows needed before state transition or response verification
       - external dependency state required by `external-stub` entries
   1.4 LOOP per `$setup_item` in `$precondition_setup` until all setup items are sourced
       1.4.1 `$setup_source` = MATCH existing plan DSL entry whose L1 can be rendered as a `Given`/setup clause, shared DSL setup entry, or test-strategy-declared DBML seed
       1.4.2 IF `$setup_source` is missing:
             1.4.2.1 `$cic` = DERIVE CiC(GAP) "precondition setup requires /aibdd-plan DSL or seed mapping"
             1.4.2.2 SET `$setup_item.setup_source_kind = cic_gap`
       1.4.3 ASSERT no new Given sentence is invented outside plan DSL/shared DSL/test-strategy seed truth
       END LOOP
   1.5 `$given_sets` = DERIVE Given value sets only from sourced `$precondition_setup`; if any required setup item is `cic_gap`, carry CiC and leave executable Given absent
   1.6 `$when_sets` = DERIVE When value sets only from:
       - `L4.param_bindings`
       - `L4.datatable_bindings`
       - `L4.default_bindings`
   1.7 `$then_sets` = DERIVE Then expectation sets only from:
       - `L4.assertion_bindings`
       - OpenAPI response schema fields referenced by assertion bindings
       - DBML fields needed for state verification
   1.8 IF `$strategy.techniques` includes `EP`:
       1.8.1 `$ep_rows` = DERIVE valid and invalid equivalence class representatives using DSL binding names and OpenAPI required fields
       1.8.2 ASSERT each invalid EP maps to `invalid_input` or `error_handling`
   1.9 IF `$strategy.techniques` includes `BVA` or `3v-BVA`:
       1.9.1 `$bva_sources` = READ OpenAPI numeric/string constraints (`minimum`, `maximum`, `format`, required) plus rule text business ranges
       1.9.2 `$bva_rows` = DERIVE min, just_above_min, nominal, just_below_max, max, just_below_min, and just_above_max where applicable
       1.9.3 IF rule requires boundary but contract lacks numeric/range truth:
             1.9.3.1 `$cic` = DERIVE CiC(BDY) "BVA requires /aibdd-plan contract/data range truth"
       1.9.4 ASSERT BVA rows include at least one non-happy-path boundary dimension or CiC(BDY)
   1.10 IF `$strategy.techniques` includes `State Transition`:
       1.10.1 `$state_rows` = DERIVE from_state, event, to_state, and illegal transition from rule text + DBML state fields
       1.10.2 IF DBML or DSL lacks state verifier target:
             1.10.2.1 `$cic` = DERIVE CiC(GAP) "state transition requires DBML/state binding from /aibdd-plan"
       1.10.3 ASSERT `$state_rows` has explicit states and events or CiC
   1.11 IF `$strategy.techniques` includes `Decision Table`:
       1.11.1 `$decision_rows` = DERIVE condition columns from DSL-visible binding keys and action columns from assertion/state targets
       1.11.2 IF row count explodes:
             1.11.2.1 `$pairwise_rows` = DERIVE pairwise or minimal interaction rows
             1.11.2.2 `$cic` = DERIVE CiC(BDY) for any business-critical combination that still needs human selection
   1.12 IF `$strategy.techniques` includes `Combinatorial`:
       1.12.1 `$combo_rows` = DERIVE pairwise rows over independent DSL-visible dimensions
       1.12.2 ASSERT `$combo_rows` does not enumerate a Cartesian explosion
   1.13 IF `$strategy.techniques` includes `Clock Mock`:
       1.13.1 `$time_rows` = DERIVE now anchor plus in-window, just-expired, or not-yet-active timestamps
       1.13.2 ASSERT clock/time source is represented in DSL/test-strategy or emit CiC(GAP)
   1.14 IF `$strategy.techniques` includes `Error Guessing`:
       1.14.1 `$guess_rows` = DERIVE at most two residual-risk rows using existing DSL bindings only
       1.14.2 ASSERT each `$guess_rows` entry has `guess_reason`
   1.15 `$binding_trace` = DERIVE trace rows for every setup item and payload key to DSL/OpenAPI/DBML target
   1.16 `$rule_test_data` = DERIVE `RuleTestData` by merging precondition setup and all technique rows into Given/When/Then buckets
   1.17 ASSERT `$rule_test_data` uses concrete business-readable values, not placeholders
   1.18 ASSERT no payload introduces a contract field or response assertion absent from plan truth
   END LOOP
2. `$rule_test_data_bundle` = DERIVE `RuleTestDataBundle` from all `RuleTestData` elements
3. ASSERT each non-CiC RuleTestData has at least one Then expectation set

## 4. Material Reducer SOP

1. EMIT `RuleTestDataBundle` with:
   1.1 `data_rows[]`: all `RuleTestData` elements
   1.2 `binding_trace[]`: all binding trace entries
   1.3 `cic_markers[]`: all CiC(GAP|ASM|BDY|CON) emitted during value enumeration
2. ASSERT every `RuleTestData.rule_anchor` matches one `RuleStrategy.rule_anchor`
3. ASSERT every `RuleTestData` has `precondition_setup[]` analysis for required existing state, even when the result is CiC(GAP)
4. ASSERT every technique in `RuleStrategy.techniques` appears in `RuleTestData.technique_notes` or concrete value sets
5. ASSERT every dimension has a concrete Given/When/Then contribution or explicit CiC/N/A reason
6. ASSERT no value contains placeholders such as `某個`, `一些`, `XX`, `正確的`, or `錯誤的`
7. ASSERT every setup/When/Then value has at least one `binding_trace` row or explicit CiC(GAP)
