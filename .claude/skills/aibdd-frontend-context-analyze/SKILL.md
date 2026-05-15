---
name: aibdd-frontend-context-analyze
description: web-frontend 專用 helper skill。由 Spec-by-Example pipeline 在偵測到 `L4.preset.name == web-frontend` 時委派；消費 RuleTestDataBundle、IndexedTruthModel、plan DSL、shared DSL、userflow truth，產出 FrontendContextHandoff / required clause candidates，讓每個 frontend Scenario 可穩定帶出 route/data/ui/userflow context。只做 reasoning handoff，不寫 `.feature`、不修改 DSL、不卡 backend。
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-frontend-context-analyze

web-frontend context reasoning helper。它把「使用者目前在哪個頁面、當下有哪些 mock/data/UI 狀態、這次操作作用在哪個 UI target、結果從哪個 observable surface 驗證」整理成 caller 可併入 Spec-by-Example 的 `FrontendContextHandoff`。

本 skill **不是**另一條完整 Spec-by-Example pipeline；它不寫 `.feature`，不產 coverage file，不修改 `/aibdd-plan` 擁有的 `dsl.yml` / OpenAPI / data / test-strategy，也不替 formatter 發明 step。caller 必須把本 skill 的 output 併回既有 `ReasonHandoffBundle` / `ClauseBinding` flow。

Notation：本檔採 program-like SOP。`READ/DERIVE/PARSE/ASSERT/MATCH/TRIGGER/DELEGATE/EMIT` 為 deterministic；`THINK/CLASSIFY/JUDGE/DRAFT` 為 semantic；本 helper 沒有 `ASK`，不得直接向 user 提問。

## §1 REFERENCES

```yaml
references:
  - path: references/role-and-contract.md
    purpose: caller payload / output schema + ownership boundary
  - path: references/frontend-context-vector.md
    purpose: FrontendContextVector 欄位定義、requiredness、hard gates
  - path: references/pipeline-integration.md
    purpose: 建議如何被 `/aibdd-spec-by-example-analyze` 接入，而不污染 backend
  - path: aibdd-core::preset-contract/web-frontend.md
    purpose: web-frontend preset contract（handler、variant、source refs、Tier-1/Tier-2）
  - path: aibdd-core::authentication-binding.md
    purpose: actor/auth context 不應被發明成一般 Given step 的跨 skill 規則
  - path: aibdd-core::report-contract.md
    purpose: DELEGATE report style
  - path: aibdd-core/assets/boundaries/web-frontend/handler-routing.yml
    purpose: route-given / mock-state-given / ui-action / ui-readmodel 等 handler routing SSOT
  - path: aibdd-core/assets/boundaries/web-frontend/shared-dsl-template.yml
    purpose: canonical route / viewport / success-failure / time shared DSL entries
  - path: aibdd-spec-by-example-analyze::reasoning/aibdd-spec-by-example-analyze/03-enumerate-rule-data-values.md
    purpose: 上游 RuleTestDataBundle schema 與 precondition_setup 來源
  - path: aibdd-spec-by-example-analyze::reasoning/aibdd-spec-by-example-analyze/04-plan-scenario-structure.md
    purpose: 下游 scenario grouping 需保留 context shape 的接點
  - path: aibdd-spec-by-example-analyze::reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md
    purpose: 下游 ClauseBinding / ReasonHandoffBundle 接點
```

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `references/role-and-contract.md` | Phase 1 / output | caller payload / output schema + ownership boundary |
| R2 | `references/frontend-context-vector.md` | Phase 3 / gate | FrontendContextVector 欄位定義、requiredness、hard gates |
| R3 | `references/pipeline-integration.md` | global | 建議接入點與 backend 防污染原則 |
| R4 | `aibdd-core::preset-contract/web-frontend.md` | Phase 1-4 | web-frontend preset contract |
| R5 | `aibdd-core::authentication-binding.md` | Phase 3 | actor/auth context rule |
| R6 | `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml` | Phase 2-4 | handler routing SSOT |
| R7 | `aibdd-core/assets/boundaries/web-frontend/shared-dsl-template.yml` | Phase 2-4 | canonical shared context DSL entries |
| R8 | `aibdd-spec-by-example-analyze::RP-03` | Phase 1-3 | RuleTestDataBundle input |
| R9 | `aibdd-spec-by-example-analyze::RP-04` | downstream | scenario grouping integration |
| R10 | `aibdd-spec-by-example-analyze::RP-05` | downstream | clause binding integration |

## §2 SOP

### Phase 1 — VALIDATE caller payload and frontend applicability
> produces: `$$payload`, `$$indexed_truth`, `$$rule_test_data`, `$$frontend_applicability`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$payload` = READ caller payload
3. ASSERT `$$payload.mode == "frontend-context"`
4. `$$indexed_truth` = PARSE `$$payload.indexed_truth`
5. `$$rule_test_data` = PARSE `$$payload.rule_test_data`
6. `$caller_context` = PARSE optional `$$payload.caller_context`
7. `$frontend_entries` = DERIVE all DSL entries in `$$indexed_truth.plan_dsl_index.entries[]` where `entry.L4.preset.name == "web-frontend"`
8. `$backend_entries` = DERIVE all DSL entries where `entry.L4.preset.name != "web-frontend"`
9. `$$frontend_applicability` = DERIVE:
   - `applicable: count($frontend_entries) > 0`
   - `frontend_entry_ids: $frontend_entries[].id`
   - `non_frontend_entry_ids: $backend_entries[].id`
10. IF `$$frontend_applicability.applicable == false`:
    10.1 `$not_applicable` = RENDER output `{exit_ok: true, status: "not_applicable", context_vectors: [], required_clause_candidates: [], cic_markers: []}`
    10.2 EMIT `$not_applicable` to caller
    10.3 STOP
11. ASSERT every applicable entry has `L4.preset.handler`, `L4.preset.sentence_part`, and `L4.source_refs`
12. ASSERT caller did not request direct file writes (`target_path` may exist for trace only; this skill ignores write targets)

### Phase 2 — INDEX frontend context truth
> produces: `$$frontend_context_truth`

1. `$$frontend_context_truth` = THINK per [`reasoning/aibdd-frontend-context-analyze/01-index-context-truth.md`](reasoning/aibdd-frontend-context-analyze/01-index-context-truth.md), input=`$$indexed_truth` + `$$rule_test_data` + `$$frontend_applicability`
2. ASSERT `$$frontend_context_truth.frontend_dsl_entries[]` non-empty
3. ASSERT `$$frontend_context_truth.handler_policy.routes[]` includes `route-given`, `mock-state-given`, `ui-action`, `success-failure`, `ui-readmodel-then`
4. ASSERT every `shared_context_entry` selected from shared DSL exists in `$$indexed_truth.plan_dsl_index.entries[]` or is explicitly marked `missing_shared_dsl`
5. IF any required Tier-2 handler appears (`api-stub`, `url-then`, `api-call-then`, `mock-state-then`):
   5.1 ASSERT `$$frontend_context_truth.test_strategy.tier2_handlers[handler] == enabled` else emit CiC(GAP)

### Phase 3 — DERIVE frontend context vectors
> produces: `$$frontend_context_vectors`

1. `$$frontend_context_vectors` = THINK per [`reasoning/aibdd-frontend-context-analyze/02-derive-context-vector.md`](reasoning/aibdd-frontend-context-analyze/02-derive-context-vector.md), input=`$$frontend_context_truth` + `$$rule_test_data`
2. LOOP per `$vector` in `$$frontend_context_vectors.context_vectors[]`
   2.1 ASSERT `$vector.preset_name == "web-frontend"`
   2.2 ASSERT `$vector.operation_context` exists for renderable target operations
   2.3 IF `$vector.operation_context.handler == "ui-action"`:
       2.3.1 ASSERT `$vector.route_context.status ∈ {bound,cic_gap}`
       2.3.2 IF `$vector.route_context.status == cic_gap`: MARK `$vector.exit_ok = false`
   2.4 IF `$vector.requires_data_context == true`:
       2.4.1 ASSERT `$vector.data_context[]` non-empty OR `$vector.cic[]` includes data-context GAP
   2.5 IF `$vector.requires_ui_context == true`:
       2.5.1 ASSERT `$vector.ui_context[]` non-empty OR `$vector.cic[]` includes ui-context GAP
       2.5.2 NOTE missing `ui_context` is v1 soft/CiC and does not by itself mark `$vector.exit_ok = false`
   2.6 ASSERT `$vector.observable_result[]` non-empty OR `$vector.cic[]` includes observable-result GAP
   END LOOP
3. ASSERT no vector includes backend-only handler or backend preset name

### Phase 4 — BUILD clause binding handoff
> produces: `$$frontend_context_handoff`

1. `$$frontend_context_handoff` = THINK per [`reasoning/aibdd-frontend-context-analyze/03-build-context-handoff.md`](reasoning/aibdd-frontend-context-analyze/03-build-context-handoff.md), input=`$$frontend_context_vectors` + `$$frontend_context_truth`
2. LOOP per `$candidate` in `$$frontend_context_handoff.required_clause_candidates[]`
   2.1 ASSERT `$candidate.preset_name == "web-frontend"`
   2.2 ASSERT `$candidate.dsl_entry_id` exists in `$$indexed_truth.plan_dsl_index.entries[].id`
   2.3 ASSERT `$candidate.dsl_l1_pattern` exists in `$$indexed_truth.dsl_l1_pattern_index.patterns_by_entry_id[$candidate.dsl_entry_id]`
   2.4 ASSERT `$candidate.handler` is one of handler ids from `handler-routing.yml`
   2.5 ASSERT `$candidate.generated_sentence == null` OR `$candidate.generated_sentence` is an instantiation of `$candidate.dsl_l1_pattern`
   END LOOP
3. ASSERT no required clause candidate references raw CSS selector, Playwright API, fixture method name, OpenAPI operation id, or Zod schema in Gherkin-facing text
4. ASSERT `$$frontend_context_handoff.exit_ok == false` iff at least one v1 hard context has unresolved CiC(GAP|CON): route_context, data-dependent data_context, or observable_result
5. EMIT `$$frontend_context_handoff` to caller

### Phase 5 — REPORT to caller

1. `$summary` = RENDER per `aibdd-core::report-contract.md`: "Frontend Context Analyze 完成。產出 N 個 frontend context vectors 與 M 個 required clause candidates；未修改 .feature / DSL / contracts / data / test-strategy。若 exit_ok=false，caller 應 STOP 或回 `/aibdd-plan` 補 DSL / userflow truth。"
2. EMIT `$summary` to caller
3. STOP

## §3 FAILURE & FALLBACK

- IF payload 缺 `indexed_truth` 或 `rule_test_data`: STOP + RETURN `caller_misuse: missing_input`
- IF no `web-frontend` DSL entries: RETURN `status: not_applicable`，不得產生 frontend context
- IF route context required but no route-given DSL/shared entry exists: return CiC(GAP) and `exit_ok=false`; caller decides STOP / rerun `/aibdd-plan`
- IF data context required but no `mock-state-given` or declared seed source exists: return CiC(GAP) and `exit_ok=false`; do not invent fixture
- IF UI setup requires modal/tab/filter/selection but no Given-capable `ui-action` DSL entry exists: return soft CiC(GAP) in v1; do not synthesize a new step and do not set `exit_ok=false` unless caller promotes `ui_context` to hard
- IF Tier-2 handler is needed but test-strategy does not enable it: return CiC(GAP) and `exit_ok=false`
- IF any generated candidate cannot be traced to DSL L1 pattern: return CiC(CON) and `exit_ok=false`
- IF caller tries to use this skill for `web-backend`: return `not_applicable`; do not reinterpret backend preconditions as frontend context

## §4 CROSS-REFERENCES

- Intended caller: `/aibdd-spec-by-example-analyze` after RP-03 and before RP-04.
- Upstream truth: `/aibdd-discovery-uiux` userflow truth, `/aibdd-plan` DSL + shared DSL + test-strategy, `aibdd-spec-by-example-analyze` RuleTestDataBundle.
- Downstream consumer: `aibdd-spec-by-example-analyze` RP-04 / RP-05 merges `required_clause_candidates` into scenario grouping and final `ClauseBinding` output.
- Explicit non-caller: `/aibdd-form-feature-spec`; formatter must not invoke this helper to patch already-rendered `.feature` text.
