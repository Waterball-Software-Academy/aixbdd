# Role and Contract — aibdd-frontend-context-analyze

## §1 Role

`aibdd-frontend-context-analyze` is a delegated reasoning helper for `web-frontend` Spec-by-Example. It answers one question:

> For this frontend example, what current route, actor/session, mock/data state, UI mode, operation target, and observable result must be explicit before rendering Gherkin?

It does not own `.feature` rendering or coverage writing.

## §2 Caller Payload Schema

```yaml
payload:
  mode: frontend-context
  indexed_truth: IndexedTruthModel          # from aibdd-spec-by-example-analyze RP-01
  rule_test_data: RuleTestDataBundle        # from aibdd-spec-by-example-analyze RP-03
  caller_context:                           # optional, trace-only
    target_feature_paths: string[]
    plan_paths: object
    userflow_truth_refs: string[]
    integration_point: "after-rp03-before-rp04"
```

Required:

- `indexed_truth.plan_dsl_index.entries[]`
- `indexed_truth.dsl_l1_pattern_index.patterns_by_entry_id`
- `indexed_truth.test_strategy`
- `rule_test_data.data_rows[]`

Optional but preferred:

- `indexed_truth.files[].rules[]` for exact Rule wording
- `indexed_truth.plan_paths.plan_reports_dir` to locate discovery-uiux userflow intent reports
- `indexed_truth.plan_dsl_index.feature_to_entries`

## §3 Output Schema

```yaml
FrontendContextHandoff:
  status: ok | not_applicable | blocked
  exit_ok: boolean
  context_vectors:
    - context_id: string
      feature_path: string
      rule_anchor: string
      source_case_ref: string
      preset_name: web-frontend
      route_context: ContextSlot
      actor_context: ContextSlot
      data_context: ContextSlot[]
      ui_context: ContextSlot[]
      viewport_time_context: ContextSlot[]
      operation_context: ContextSlot
      observable_result: ContextSlot[]
      requires_data_context: boolean
      requires_ui_context: boolean
      cic: CiCMarker[]
  required_clause_candidates:
    - candidate_id: string
      context_id: string
      order: integer
      keyword: Given | When | Then | And
      handler: string
      preset_name: web-frontend
      dsl_entry_id: string
      dsl_l1_pattern: string
      generated_sentence: string | null
      parameters: object
      binding_keys: string[]
      requiredness: hard | conditional | optional
      reason: string
  context_binding_trace:
    - context_id: string
      slot: string
      dsl_entry_id: string
      binding_key: string
      binding_kind: param | datatable | default | assertion | response | data | route | ui
      target: string
  cic_markers:
    - kind: GAP | ASM | BDY | CON
      where: string
      text: string
```

## §4 Ownership Boundary

This skill may:

- Read caller payload.
- Read frontend preset contracts and shared DSL truth through the caller-provided `IndexedTruthModel`.
- Return context vectors, clause candidates, traces, and CiC markers.

This skill must not:

- Write `.feature`, `.coverage.yml`, `dsl.yml`, OpenAPI, DBML, test-strategy, Storybook, or product code.
- Invent a Gherkin sentence absent from selected DSL/shared DSL L1 patterns.
- Enable Tier-2 frontend handlers without test-strategy truth.
- Apply to `web-backend` or non-frontend presets.
- Ask the user directly.
