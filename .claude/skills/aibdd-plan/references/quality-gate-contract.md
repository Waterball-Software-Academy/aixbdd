# Quality Gate Contract

This file is the self-contained semantic quality contract for `/aibdd-plan`.
It replaces any dependency on external research or evaluation files.

## Veto Conditions

- Plan/truth path overlap: any accepted technical truth is written only inside the plan package.
- Shadow truth: contracts, data, test strategy, or DSL mappings are duplicated as plan-package-only truth.
- Specifier bypass: for a boundary profile that declares an operation contract specifier or state specifier, `/aibdd-plan` hand-renders that truth instead of delegating to the declared formulation skill.
- Role boundary leak: the skill writes Discovery behavior, Spec-by-Example examples, tasks, product code, step definitions, or runtime fixtures.
- DSL not red-usable: changed DSL entries lack L1-L4, physical surface, L4 `source_refs`, parameter bindings, assertion bindings, valid `dsl.yml` paths in `arguments.yml`, or they fail deterministic `check_dsl_entries.py` (e.g. operation required inputs are not exactly covered by `param_bindings + datatable_bindings + default_bindings`).
- DSL mirrors API payload: L1 exposes technical request shape or an excessive parameter list instead of the feature atomic-rule focus.
- DSL defaults without atomic-rule justification: `default_bindings` exist without explaining why the value does not affect majority behavior under test, or without a datatable override policy.
- DSL readability pressure failure: operation-backed entries have more than 3 sentence parameters, more than 6 datatable parameters after defaults, or use defaults to hide behavior that the atomic rules actually vary.
- DSL statelessness failure: L1/Then/And sentences cannot identify the business subject, lookup identity, and expected data/effect without reading neighboring steps.
- DSL identity opacity: ID-like targets are exposed under keys that do not say `ID`, or dynamic ID references use ambiguous aliases such as `$previous.id`.
- Raw technical datatable payload: datatable cells contain JSON/YAML/DTO/DB-shaped payloads instead of business columns, or nested aggregate bindings lack deterministic `group` / `item_field` projection when needed.
- Backend preset asset drift: `handler-routing.yml` fails its consistency check or a backend DSL entry's `L4.preset` does not resolve to the handler-routing asset.
- Sequence path incompleteness: major happy/alternative/error behavior paths are collapsed into one sequence diagram, use legacy `*.backend.sequence.mmd` naming, or are missing from `plan.md`.
- Impacted feature scope gap: `plan.md` lacks `## Impacted Feature Files`, the section is empty, bullets do not contain canonical repo-relative feature paths, or listed paths fall outside `${FEATURE_SPECS_DIR}`.
- External mock violation: same-boundary internal collaborator is modeled as a mock/stub provider.
- Fixture upload gap: upload contract exists but DSL lacks fixture source, invocation, response verifier, state/file-store verifier, or missing-file behavior.
- Test-plan dependency: completion requires `/aibdd-test-plan` or `speckit-aibdd-test-plan`.

## Weighted Semantic Dimensions

### Q1 Role Coherence

The skill behaves as a technical planning orchestrator. It starts after `/aibdd-discovery`, prepares exact input graph for `/aibdd-spec-by-example-analyze`, and does not absorb tasks or implementation.

### Q2 Owner-Scoped Truth

Truth changes are direct updates to owner-scoped boundary truth files. Git diff on actual truth files is the review surface.

### Q3 External/Internal Planning Completeness

External boundary surface, provider contracts, dependency test strategy, internal sequence diagrams, and internal structure are all represented at a task-usable granularity. Contract/state truth formats follow the resolved boundary profile instead of planner-local assumptions.

### Q4 DSL Physical Mapping Quality

DSL entries map exact business sentences to red-usable L4 surfaces. Bindings point to contracts, data, response paths, fixtures, stub payloads, or literals. **Operation** entries must satisfy exact required-input coverage across `param_bindings + datatable_bindings + default_bindings` enforced by `check_dsl_entries.py`. L1 keys may be natural language when `$$dsl_key_locale` demands it; contract/data field names remain technical English.

Readability pressure is part of Q4:

- L1 sentence parameters are capped at `<= 3` and must be atomic-rule-critical.
- Datatable parameters are capped at `<= 6` after defaults and must remain business-understandable.
- Defaults must be derived from feature atomic rules, not from field-name heuristics.
- Defaults must include a target, concrete value, atomic-rule reason, and override policy.
- The combined coverage of sentence parameters, datatable parameters, and defaults must cover every required operation input without adding non-input contract bindings.
- Each sentence is stateless enough for `/aibdd-red` to match, bind, and verify it without scenario-memory inference.
- ID-like binding keys expose identity explicitly (`XXX ID`) and dynamic IDs use `$<unique business identifier>.id`.
- Nested datatables are business projections with reconstructable grouping metadata, not raw technical payloads.

### Q5 Backend Reusable Preset Use

Backend entries reference `web-backend` handlers and a variant such as `python-e2e` when reusable patterns apply.

`handler-routing.yml` is the SSOT for backend sentence part / handler ids and
per-handler L4 policy. No boundary-local or package-local sentence-parts inventory
is required or accepted as a replacement.

### Q6 Downstream Handoff Precision

Final handoff lists plan, research, impacted feature files, boundary map, contracts, data/test strategy, local/shared DSL, implementation diagrams, quality report, blocking gaps, and Git diff review focus.

Implementation diagrams are listed per major path using
`<scenario>.<category>.sequence.mmd`, where `category` is `happy`, `alt`, or
`err`.

## Verdict Shape

```json
{
  "verdict": "PASS | SOFT_FAIL | VETO",
  "vetoes": [
    {
      "condition": "string",
      "evidence": "string"
    }
  ],
  "dimension_scores": {
    "Q1": 1.0,
    "Q2": 1.0,
    "Q3": 1.0,
    "Q4": 1.0,
    "Q5": 1.0,
    "Q6": 1.0
  },
  "fix_hints": []
}
```

## Pass Rule

- `VETO` if any veto condition is true.
- `SOFT_FAIL` if no veto exists but any weighted dimension is below `0.7`.
- `PASS` if no veto exists and every weighted dimension is at least `0.7`.
