---
rp_type: reasoning_phase
id: aibdd-frontend-context-analyze.01-index-context-truth
context: aibdd-frontend-context-analyze
slot: "01"
name: Index Frontend Context Truth
variant: web-frontend-only
consumes:
  - name: IndexedTruthModel
    kind: required_axis
    source: caller
    required: true
  - name: RuleTestDataBundle
    kind: required_axis
    source: caller
    required: true
  - name: FrontendApplicability
    kind: derived_axis
    source: skill_phase_1
    required: true
produces:
  - name: FrontendContextTruthIndex
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-frontend-context-analyze.02-derive-context-vector
---

# Index Frontend Context Truth

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: IndexedTruthModel
    required_fields:
      - plan_dsl_index.entries[]
      - dsl_l1_pattern_index.patterns_by_entry_id
      - test_strategy
  - name: RuleTestDataBundle
    required_fields:
      - data_rows[].feature_path
      - data_rows[].rule_anchor
      - data_rows[].precondition_setup
      - data_rows[].when_value_sets
      - data_rows[].then_expect_sets
  - name: FrontendApplicability
    required_fields:
      - applicable
      - frontend_entry_ids[]
```

### 1.2 Search SOP

1. `$indexed_truth` = READ `IndexedTruthModel`
2. `$rule_test_data` = READ `RuleTestDataBundle`
3. ASSERT `FrontendApplicability.applicable == true`
4. `$all_entries` = READ `$indexed_truth.plan_dsl_index.entries[]`
5. `$frontend_dsl_entries` = FILTER `$all_entries` where `L4.preset.name == "web-frontend"`
6. `$shared_context_entries` = FILTER `$frontend_dsl_entries` where `source.feature_path == null` OR `id` starts with `shared.`
7. `$handler_groups` = GROUP `$frontend_dsl_entries` by `L4.preset.handler`
8. `$route_entries` = FILTER handler `route-given`
9. `$mock_state_entries` = FILTER handler `mock-state-given`
10. `$ui_action_entries` = FILTER handler `ui-action`
11. `$result_entries` = FILTER handlers in `{success-failure, ui-readmodel-then, url-then, api-call-then, mock-state-then}`
12. `$viewport_time_entries` = FILTER handlers in `{viewport-control, time-control}`
13. `$feature_to_frontend_entries` = DERIVE mapping from feature_path to frontend DSL entries using `plan_dsl_index.feature_to_entries` plus shared entries
14. `$userflow_refs` = DERIVE optional userflow truth refs from:
    - `IndexedTruthModel.plan_paths.plan_reports_dir/discovery-uiux-userflow-intent.md`
    - feature/activity source refs present in DSL entries
    - caller_context.userflow_truth_refs
15. `$tier2_status` = DERIVE enabled Tier-2 handlers from `IndexedTruthModel.test_strategy.tier2_handlers`
16. ASSERT every `$frontend_dsl_entry.id` has at least one L1 pattern in `dsl_l1_pattern_index.patterns_by_entry_id`
17. ASSERT handler ids are not empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: FrontendContextTruthIndex
  elements:
    FrontendContextTruthIndex:
      role: "Indexed frontend-only truth consumed by context vector derivation"
      fields:
        frontend_dsl_entries: "DslEntry[]"
        shared_context_entries: "DslEntry[]"
        handler_groups: "dict<handler,DslEntry[]>"
        feature_to_frontend_entries: "dict<feature_path,DslEntry[]>"
        dsl_l1_pattern_index: "dict<entry_id,set<string>>"
        tier2_status: "dict<handler,enabled|disabled|missing>"
        userflow_refs: "string[]"
        test_strategy: "object"
        cic_markers: "CiCMarker[]"
      invariants:
        - "Only web-frontend preset entries appear in frontend_dsl_entries"
        - "Shared route/viewport/time/success entries are indexed when present, but missing shared entries are represented as CiC candidates rather than invented"
        - "Tier-2 handlers are marked disabled unless explicitly enabled by test_strategy"
```

## 3. Reasoning SOP

1. DERIVE `FrontendContextTruthIndex` from Search SOP outputs
2. IF `route-given` handler group is empty:
   2.1 ADD CiC(GAP) `where=route_context` text="web-frontend context requires route-given shared/local DSL for ui-action examples"
3. IF `ui-action` handler group is empty:
   3.1 ADD CiC(GAP) `where=operation_context` text="frontend feature has no ui-action DSL entry for target operation"
4. LOOP per `$handler` in Tier-2 handler groups
   4.1 IF `$tier2_status[$handler] != enabled`:
       4.1.1 ADD CiC(GAP) `where=tier2:${handler}` text="Tier-2 handler used by DSL but not enabled in test-strategy"
   END LOOP
5. ASSERT no backend preset entries are copied into the index

## 4. Material Reducer SOP

1. EMIT `FrontendContextTruthIndex` with all fields in §2
2. ASSERT count(`frontend_dsl_entries`) > 0
3. ASSERT every `handler_groups.*[].L4.preset.name == web-frontend`
4. ASSERT every entry id in `frontend_dsl_entries` has an L1 pattern set or a CiC(CON)
