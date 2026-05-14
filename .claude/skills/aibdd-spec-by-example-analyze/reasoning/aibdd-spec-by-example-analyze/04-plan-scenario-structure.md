---
rp_type: reasoning_phase
id: aibdd-spec-by-example-analyze.04-plan-scenario-structure
context: aibdd-spec-by-example-analyze
slot: "04"
name: Plan Scenario Structure
variant: none
consumes:
  - name: RuleTestDataBundle
    kind: required_axis
    source: upstream_rp
    required: true
  - name: ContextAugmentationHandoff
    kind: required_axis
    source: skill_global
    required: false
produces:
  - name: ScenarioStructurePlan
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-spec-by-example-analyze.05-build-coverage-handoff
---

# Plan Scenario Structure

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: RuleTestDataBundle
    source:
      kind: upstream_rp
      producer: aibdd-spec-by-example-analyze.03-enumerate-rule-data-values
    granularity: "concrete Rule test data rows for the current package"
    required_fields:
      - data_rows[]
      - data_rows[].feature_path
      - data_rows[].rule_anchor
      - data_rows[].precondition_setup
      - data_rows[].given_value_sets
      - data_rows[].when_value_sets
      - data_rows[].then_expect_sets
    completeness_check:
      rule: "each non-CiC RuleData row has setup, operation values, and target expectation values before scenario grouping"
      on_missing: STOP
  - name: ContextAugmentationHandoff
    source:
      kind: skill_global
      path: "Phase 2 $$context_augmentation_handoff"
    granularity: "optional preset-scoped context vectors and clause candidates for this analyzer run"
    required: false
    required_fields:
      - status
      - exit_ok
      - context_vectors[]
      - required_clause_candidates[]
    optional_fields:
      - context_binding_trace[]
      - cic_markers[]
    completeness_check:
      rule: "when present, the handoff is ok/not_applicable, exit_ok true, and every executable candidate declares preset_name plus DSL trace"
      on_missing: mark_unknown
```

### 1.2 Search SOP

1. `$test_data_bundle` = READ `RuleTestDataBundle`
2. `$context_handoff` = READ optional `ContextAugmentationHandoff`
3. ASSERT `$test_data_bundle.data_rows[]` is present
4. IF `$context_handoff` present:
   4.1 ASSERT `$context_handoff.status ∈ {"ok","not_applicable"}`
   4.2 ASSERT `$context_handoff.exit_ok == true`
   4.3 ASSERT every executable candidate has `candidate_id`, `preset_name`, `dsl_entry_id`, `dsl_l1_pattern`, and `source_kind == context_augmentation`
5. LOOP per `$rule_data` in `$test_data_bundle.data_rows` until all rule data is grouped
   5.1 `$case_rows` = PARSE `$rule_data` into candidate test case rows
   5.2 `$context_rows` = MATCH `$context_handoff.context_vectors[]` by `feature_path` + `rule_anchor` + source case ref when present
   5.3 `$case_rows` = DERIVE attach matching context vector ids, required clause candidate ids, and context merge keys to corresponding case rows
   5.4 ASSERT `$case_rows` preserve dimension, technique, precondition setup, Given values, When values, rule-targeted Then expectations, and context candidate refs when present
   END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: ScenarioStructurePlan
  element_rules:
    element_vs_field:
      element: "A scenario grouping decision that downstream formulation can render"
      field: "A merge flag, row value, context merge key, or display column nested under a ScenarioStructureGroup"
  elements:
    ScenarioStructureGroup:
      role: "Represent one Scenario or Scenario Outline decision for a Rule"
      fields:
        feature_path: "path"
        rule_anchor: "string"
        precondition_setup: "PreconditionSetup[]"
        merge_decision: "MergeDecision"
        example_body_shape: "ExampleBodyShape"
        context_shape: "ContextShape|null"
        outline_title: "string|null"
        example_columns: "string[]"
        rows: "dict[]"
        cic: "CiCMarker[]"
      nested_fields:
        MergeDecision:
          step0_when_then_same: "boolean"
          step1_given_same: "boolean"
          extra_precondition_same: "boolean"
          row_count: "integer"
          outcome: "Scenario|ScenarioOutline|Example"
          reason: "string"
        ExampleBodyShape:
          setup_policy: "given_steps|setup_cic|mixed"
          operation_clause: "When"
          assertion_scope: "precondition|response|state|external|mixed"
          allowed_then_entry_ids: "string[]"
          forbidden_then_entry_ids: "string[]"
          required_context_candidate_ids: "string[]"
        ContextShape:
          source_preset_names: "string[]"
          context_vector_refs: "string[]"
          required_candidate_ids: "string[]"
          merge_keys: "string[]"
          hard_required_slots: "string[]"
          soft_cic: "CiCMarker[]"
      invariants:
        - "Every group carries precondition_setup analysis from RP-03"
        - "An Example may include only the assertion DSL entries needed for its own atomic Rule"
        - "Hard context clauses are setup/result context, not optional assertion noise; minimal assertion filtering must not remove them"
        - "Response-rule Examples must not include aggregate/state Then clauses unless the Rule itself requires state verification"
        - "State-rule Examples must not include response Then clauses unless needed to identify a dynamically generated value"
        - "ScenarioOutline is allowed only when Step 0 and Step 1 pass and row_count >= 2"
        - "Rows with different When+Then structures must never share one Outline"
        - "Rows with different extra preconditions must never share one Outline"
        - "Rows with different context merge keys must never share one Outline unless represented by Examples columns and all step templates remain identical"
        - "Rows with different DSL datatable column shapes must never share one Outline"
```

## 3. Reasoning SOP

1. LOOP per `$rule_data` in `RuleTestDataBundle.data_rows[]` until all scenario structures are planned
   1.1 `$case_rows` = DERIVE candidate rows from `$rule_data.precondition_setup`, `$rule_data.given_value_sets`, `$rule_data.when_value_sets`, and `$rule_data.then_expect_sets`
   1.1.1 IF `ContextAugmentationHandoff` present:
         1.1.1.1 `$case_rows` = MERGE matching `context_vectors` and `required_clause_candidates` by feature_path / rule_anchor / source case ref
         1.1.1.2 ASSERT every merged candidate targets the same DSL preset as its `preset_name`
   1.2 `$assertion_scope` = CLASSIFY `$rule_data.rule_anchor` / Rule prefix:
       - 前置（狀態） or 前置（參數） -> `precondition`
       - 後置（回應） -> `response`
       - 後置（狀態） / 後置（狀態：資料） / 後置（狀態：資源） / 後置（狀態：行為） -> `state`
       - 後置（狀態：外發） -> `external`
   1.3 `$case_rows` = FILTER Then expectations to the minimal `$assertion_scope`; carry non-target Then entries as `forbidden_then_entry_ids`, not executable steps; DO NOT filter hard context candidates as non-target Then noise
   1.4 ASSERT `$assertion_scope == response` implies aggregate/state Then entries are excluded unless needed only as a dynamic-id bridge with trace
   1.5 ASSERT `$assertion_scope == state` implies response Then entries are excluded unless the state verifier needs a response-generated identity and no business identity exists
   1.6 `$row_clusters` = DERIVE candidate clusters by `rule_anchor`, `$assertion_scope`, setup policy, context shape, and normalized clause shape
   1.7 LOOP per `$cluster` in `$row_clusters` until all clusters are decided
       1.7.1 `$when_then_same` = JUDGE normalized When step templates, Then step templates, context clause templates, and DSL datatable column shapes are identical across rows
       1.7.1.1 IF `$cluster` has context augmentation:
               1.7.1.1.1 `$context_same` = JUDGE context merge keys and required context candidate templates are identical across rows OR every varying context value is represented by DSL-visible Examples columns
               1.7.1.1.2 IF `$context_same == false`: SET `$when_then_same = false`
       1.7.2 IF `$when_then_same == false`:
             1.7.2.1 `$group` = DERIVE `ScenarioStructureGroup` with outcome `Scenario`
             1.7.2.2 ASSERT success and failure rows with different Then templates are not merged
             1.7.2.3 CONTINUE
       1.7.3 `$given_same` = JUDGE normalized Given step templates and setup policy are identical across rows
       1.7.4 `$extra_precondition_same` = JUDGE extra precondition labels and context labels are identical across rows unless represented by Examples columns
       1.7.5 IF `$given_same == true` and `$extra_precondition_same == true` and count(`$cluster.rows`) >= 2:
             1.7.5.1 `$group` = DERIVE `ScenarioStructureGroup` with outcome `ScenarioOutline`
       1.7.6 ELSE IF count(`$cluster.rows`) == 1:
             1.7.6.1 `$group` = DERIVE `ScenarioStructureGroup` with outcome `Example`
       1.7.7 ELSE:
             1.7.7.1 `$group` = DERIVE `ScenarioStructureGroup` with outcome `Scenario`
       1.7.8 `$columns` = DERIVE business-readable Examples columns from varying Given/When/Then values, context values, and DSL-visible binding keys
       1.7.9 ASSERT `$columns` do not expose raw internal locators, production internals, or contract fields that are not DSL-visible
       1.7.10 ASSERT `$group.example_body_shape.allowed_then_entry_ids` excludes non-target assertion DSL entries
       1.7.11 ASSERT `$group.example_body_shape.required_context_candidate_ids` contains every hard context candidate id needed by rows in this group
       END LOOP
   END LOOP
2. `$scenario_structure_plan` = DERIVE `ScenarioStructurePlan` from all `ScenarioStructureGroup` elements
3. ASSERT every ScenarioOutline group has merge decision trace for Step 0, Step 1, row count, and outcome

## 4. Material Reducer SOP

1. EMIT `ScenarioStructurePlan` with:
   1.1 `groups[]`: all `ScenarioStructureGroup` elements
   1.2 `cic_markers[]`: all CiC(GAP|ASM|BDY|CON) emitted during scenario planning
2. ASSERT every `ScenarioStructureGroup.merge_decision` includes `step0_when_then_same`, `step1_given_same`, `extra_precondition_same`, `row_count`, `outcome`, and `reason`
3. ASSERT every `ScenarioStructureGroup` carries `precondition_setup`, `example_body_shape`, and `context_shape` when applicable
4. ASSERT `outcome == ScenarioOutline` implies `step0_when_then_same == true`, `step1_given_same == true`, `extra_precondition_same == true`, and `row_count >= 2`
5. ASSERT successful and failing rows with different Then templates, context templates, or datatable shapes appear in separate groups
6. ASSERT rows with different extra preconditions or context merge keys appear in separate groups
7. ASSERT response-rule groups do not carry state assertion clauses, and state-rule groups do not carry response assertion clauses, unless explicitly justified as dynamic-id bridge
8. ASSERT context candidate ids required by `ContextAugmentationHandoff` are preserved for RP-05 without preset-specific interpretation
