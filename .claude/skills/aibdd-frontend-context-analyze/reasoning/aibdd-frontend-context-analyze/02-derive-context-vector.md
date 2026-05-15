---
rp_type: reasoning_phase
id: aibdd-frontend-context-analyze.02-derive-context-vector
context: aibdd-frontend-context-analyze
slot: "02"
name: Derive Frontend Context Vector
variant: web-frontend-only
consumes:
  - name: FrontendContextTruthIndex
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: RuleTestDataBundle
    kind: required_axis
    source: caller
    required: true
produces:
  - name: FrontendContextVectorBundle
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-frontend-context-analyze.03-build-context-handoff
---

# Derive Frontend Context Vector

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: FrontendContextTruthIndex
    required_fields:
      - frontend_dsl_entries[]
      - handler_groups
      - feature_to_frontend_entries
      - dsl_l1_pattern_index
  - name: RuleTestDataBundle
    required_fields:
      - data_rows[]
```

### 1.2 Search SOP

1. `$truth` = READ `FrontendContextTruthIndex`
2. `$rule_test_data` = READ `RuleTestDataBundle`
3. LOOP per `$row` in `$rule_test_data.data_rows[]`
   3.1 `$entries` = MATCH `$row.feature_path` against `$truth.feature_to_frontend_entries`; include shared entries
   3.2 `$target_operation` = SELECT best `ui-action` or frontend operation entry using `$row.when_value_sets[].binding_keys`, DSL `param_bindings`, and Rule text
   3.3 `$candidate_results` = SELECT result entries using `$row.then_expect_sets[].binding_keys`, assertion scope, and DSL assertion bindings
   3.4 `$candidate_route` = SELECT route source from `$target_operation.L4.source_refs.route`, matching `route-given` entry, or userflow refs
   3.5 `$candidate_data` = SELECT data setup entries from `$row.precondition_setup[]`, `mock-state-given` entries, and test-strategy seed truth
   3.6 `$candidate_ui_setup` = SELECT prior UI setup entries when Rule/userflow/DSL L2 context indicates modal/tab/filter/selection/wizard/edit mode not implied by route
   END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: FrontendContextVectorBundle
  elements:
    FrontendContextVector:
      role: "One frontend scenario-case context vector before final scenario grouping"
      fields:
        context_id: "string"
        feature_path: "path"
        rule_anchor: "string"
        source_case_ref: "string"
        preset_name: "web-frontend"
        route_context: "ContextSlot"
        actor_context: "ContextSlot"
        data_context: "ContextSlot[]"
        ui_context: "ContextSlot[]"
        viewport_time_context: "ContextSlot[]"
        operation_context: "ContextSlot"
        observable_result: "ContextSlot[]"
        requires_data_context: "boolean"
        requires_ui_context: "boolean"
        cic: "CiCMarker[]"
        exit_ok: "boolean"
      nested_fields:
        ContextSlot:
          slot: "route_context|actor_context|data_context|ui_context|viewport_time_context|operation_context|observable_result"
          status: "bound|not_required|inherited|cic_gap|cic_con"
          handler: "string|null"
          dsl_entry_id: "string|null"
          dsl_l1_pattern: "string|null"
          parameters: "dict"
          binding_keys: "string[]"
          source_refs: "dict"
          reason: "string"
      invariants:
        - "Every renderable vector has operation_context and observable_result or CiC"
        - "ui-action operation_context implies route_context is bound or cic_gap"
        - "data-dependent UI examples have data_context bound or cic_gap"
        - "UI setup not implied by route/data is explicit in ui_context or soft cic_gap; v1 does not fail exit_ok for ui_context alone"
        - "No slot uses a non-web-frontend preset entry"
```

## 3. Reasoning SOP

1. LOOP per `$row` in `RuleTestDataBundle.data_rows[]`
   1.1 `$entries` = MATCH frontend entries for `$row.feature_path`
   1.2 IF `$entries` is empty:
       1.2.1 CONTINUE because this helper only handles frontend rows
   1.3 `$operation_context` = DERIVE from matching `ui-action` entry and `$row.when_value_sets`
   1.4 IF `$operation_context` missing:
       1.4.1 ADD CiC(GAP) `where=operation_context` text="No ui-action/frontend operation DSL entry matches this rule row"
   1.5 `$route_context` = DERIVE:
       - Prefer `operation_context.dsl_entry.L4.source_refs.route`
       - Bind to `route-given` shared/local DSL pattern when route value is known
       - Use userflow entry route when DSL source ref points to a route map but no literal path is available
       - Otherwise CiC(GAP)
   1.6 `$actor_context` = DERIVE from feature tags, actor binding, or userflow actor; if auth is generic, mark `inherited` rather than generating a Given
   1.7 `$requires_data_context` = JUDGE whether `$row.precondition_setup[]`, UI readmodel, validation, state transition, or result expectations depend on pre-existing data
   1.8 IF `$requires_data_context`:
       1.8.1 `$data_context` = DERIVE each required setup item from `mock-state-given` DSL, declared seed truth, or api-stub behavior override where semantically correct
       1.8.2 IF any required setup lacks source: ADD CiC(GAP) `where=data_context`
   1.9 `$requires_ui_context` = JUDGE whether target action requires a prior visible UI mode beyond route/data:
       - modal/dialog open
       - non-default tab/filter/sort/search active
       - row/card selected
       - wizard step beyond first
       - edit mode entered before submit
   1.10 IF `$requires_ui_context`:
       1.10.1 `$ui_context` = DERIVE Given-capable `ui-action` setup clauses from DSL
       1.10.2 IF no legal DSL entry exists: ADD soft CiC(GAP) `where=ui_context` and keep `$vector.exit_ok` unchanged unless caller explicitly promotes ui_context to hard
   1.11 `$viewport_time_context` = DERIVE only if test-strategy/rule requires responsive or time-dependent setup
   1.12 `$observable_result` = DERIVE from result handlers matching `$row.then_expect_sets`:
       - `success-failure` for feedback class / reason
       - `ui-readmodel-then` for DOM-visible values
       - `url-then` for navigation result
       - `api-call-then` for outgoing call presence/content
       - `mock-state-then` for mock store mutation not visible in UI
   1.13 IF `$observable_result` missing:
       1.13.1 ADD CiC(GAP) `where=observable_result`
   1.14 `$exit_ok` = DERIVE false iff any v1 hard-required slot has CiC(GAP|CON): route_context, data-dependent data_context, or observable_result
   1.15 `$vector` = DERIVE `FrontendContextVector`
   END LOOP
2. `$bundle` = DERIVE `FrontendContextVectorBundle` from all vectors and CiC markers

## 4. Material Reducer SOP

1. EMIT `FrontendContextVectorBundle` with `context_vectors[]` and `cic_markers[]`
2. ASSERT every `context_id` unique
3. ASSERT every bound slot has `dsl_entry_id` and `dsl_l1_pattern`
4. ASSERT every `dsl_entry_id` belongs to a `web-frontend` preset entry
5. ASSERT every v1 hard-required missing slot is represented as CiC and sets `exit_ok=false`
6. ASSERT missing actor_context / ui_context / viewport_time_context are represented as soft CiC or inherited/not_required and do not alone set `exit_ok=false`
