# Pipeline Integration Guidance

## §1 Recommended Placement

Invoke this helper inside `/aibdd-spec-by-example-analyze` only after RP-03 has produced `RuleTestDataBundle` and before RP-04 plans scenario grouping:

```text
RP-01 index input truth
RP-02 classify rule strategy
RP-03 enumerate rule data values
IF selected DSL entries contain L4.preset.name == web-frontend:
  DELEGATE /aibdd-frontend-context-analyze
  ASSERT FrontendContextHandoff.exit_ok
  MERGE context vectors into candidate case rows
RP-04 plan scenario structure
RP-05 build coverage handoff
```

## §2 Why Not Post-Process `.feature`

Do not run this after `/aibdd-form-feature-spec` to patch `.feature` text. Post-processing would bypass:

- DSL L1 pattern compliance
- ClauseBinding trace
- coverage rows
- CiC / STOP gates
- backend/frontend preset separation

## §3 Backend Pollution Guard

The caller must branch by DSL preset, not by feature filename or natural language:

```text
IF any selected DSL entry has L4.preset.name == web-frontend:
  delegate this helper for those frontend case rows
ELSE:
  keep existing backend Spec-by-Example path
```

Never make `route_context` globally required for all presets.

## §4 Merge Rules for Caller

- Merge hard v1 context (`route_context`, data-dependent `data_context`, and `observable_result`) into RP-04 grouping keys. Rows with different route/data/result setup must not share one Scenario Outline unless the context differences are represented as Examples columns and all step templates remain identical.
- Carry `ui_context`, `actor_context`, and `viewport_time_context` as soft/CiC context in v1; do not fail grouping solely because those soft slots are unresolved unless the caller explicitly promotes them to hard.
- Merge `required_clause_candidates` into RP-05 `BDDExample.steps` before final ClauseBinding validation.
- Preserve `cic_markers` in coverage/handoff artifacts, not in final `.feature` comments.
- If `exit_ok=false`, caller should STOP or report upstream action: usually rerun `/aibdd-plan` to add DSL/shared DSL or rerun `/aibdd-discovery-uiux` to resolve userflow truth.
