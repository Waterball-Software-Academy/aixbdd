---
name: aibdd-red-execute
description: Create legal AIBDD red for target feature files by loading project config, mapping every Scenario step to DSL and core preset assets, rendering runtime-visible step definitions, and emitting a Red handoff. TRIGGER when Red execute is requested or delegated by implementation/debug flow. SKIP when the feature package or BDD stack config is absent.
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-red-execute

Create legal red for every Scenario in the target feature-file set.

<!-- VERB-GLOSSARY:BEGIN — auto-rendered from programlike-skill-creator/references/verb-cheatsheet.md by render_verb_glossary.py; do not hand-edit -->
> **Program-like SKILL.md — self-contained notation**
>
> **3 verb classes** (type auto-derived from verb name):
> - **D** = Deterministic — no LLM judgment required; future scripting candidate
> - **S** = Semantic — LLM reasoning required
> - **I** = Interactive — yields turn to user
>
> **Yield discipline** (executor 鐵律): **ONLY** `I` verbs yield turn to the user. `D` and `S` verbs MUST NOT pause for user reaction. In particular:
> - `EMIT $x to user` is **fire-and-forget** — continue immediately to the next step; do not wait for acknowledgment.
> - `WRITE` / `CREATE` / `DELETE` are side effects, **not** phase boundaries — execution continues to the next sub-step.
> - Phase transitions (Phase N → Phase N+1) and sub-step transitions are **non-yielding**.
> - Mid-SOP messages of the form 「要繼續嗎？」/「先 review 一下？」/「先 checkpoint？」/「先停下來確認？」/「want me to proceed?」/「should I continue?」are **FORBIDDEN**. The ONLY way to ask the user is an `[USER INTERACTION] $reply = ASK ...` step.
> - `STOP` / `RETURN` are terminations, not yields — no next step follows.
>
> **SSA bindings**: `$x = VERB args` (productive steps name their output);
> `$x` is phase-local; `$$x` crosses phases (declared in phase header's `> produces:` line).
>
> **Side effect**: `VERB target ← $payload` — `←` arrow = "write into target".
>
> **Control flow**: `BRANCH $check ? then : else` (binary) or indented arms (multi);
> `GOTO #N.M` = jump to Phase N step M (literal `#phase.step`).
>
> **Canonical verb table** (T = D / S / I):
>
> | Verb | T | Meaning |
> |---|---|---|
> | READ | D | 讀檔 → bytes / text |
> | WRITE | D | 寫檔（內容已備好） |
> | CREATE | D | 建立目錄 / 空檔 |
> | DELETE | D | 刪檔（rollback） |
> | COMPUTE | D | 純運算 |
> | DERIVE | D | 從既定規則推算 |
> | PARSE | D | 字串 → in-memory 結構 |
> | RENDER | D | template + vars → string |
> | ASSERT | D | 斷言 invariant；fail-stop |
> | MATCH | D | regex / pattern 比對 |
> | TRIGGER | D | 啟動 process / subagent / tool / script；output 可 bind |
> | DELEGATE | D | 呼叫其他 skill |
> | MARK | D | 紀錄狀態（譬如 TodoWrite） |
> | BRANCH | D | 分支（吃 `$check` / `$kind` binding） |
> | GOTO | D | 跳 `#phase.step` literal |
> | IF / ELSE / END IF | D | 條件 sub-step |
> | LOOP / END LOOP | D | 迴圈（必標 budget + exit） |
> | RETURN | D | 提前結束 phase |
> | STOP | D | 終止整個 skill |
> | EMIT | D | 輸出已生成資料（fire-and-forget；**不 yield**，continue 下一 step） |
> | WAIT | D | 等待已 spawn 的 process |
> | THINK | S | 內部判斷（不印 user） |
> | CLASSIFY | S | 多類別分類 → enum 之一 |
> | JUDGE | S | 二元語意判斷 |
> | DECIDE | S | 從 user reply / context 推結論 |
> | DRAFT | S | 生成 prose / 訊息 |
> | EDIT | S | LLM 推 patch 改既有檔 |
> | PARAPHRASE | S | 改寫 / 翻譯 prose |
> | CRITIQUE | S | 批評 / 建議 |
> | SUMMARIZE | S | 抽取重點 |
> | EXPLAIN | S | 對 user 解釋 why |
> | ASK | I | 問 user 等回應（仍配 `[USER INTERACTION]` tag）；**唯一允許 yield turn 給 user 的 verb**。**Planner-level skill** 對 user 的提問**必須 `DELEGATE /clarify-loop`**，不得直接 `ASK`（其他角色的 skill 自決）。 |
<!-- VERB-GLOSSARY:END -->

## §1 REFERENCES

```yaml
references:
  - path: references/execute-config-contract.md
    purpose: Defines target, arguments, core reference, preset asset, runtime ref, drift, and routing contracts
  - path: references/handoff-schemas.md
    purpose: Defines behavior report and execute handoff schemas for downstream drift checks
  - path: references/legal-red-classification.md
    purpose: Defines legal red, false red, stop routing, and red loop budget semantics
```

## §2 SOP

### Phase 1 — RECEIVE target
> produces: `$$payload`, `$$target_feature_files`, `$$arguments_path`

1. `$$payload` = READ caller payload with `target_feature_files`, optional `arguments_path`, optional `task_id`, optional `phase`.
2. `$$target_feature_files` = PARSE `$$payload.target_feature_files` as non-empty path list.
3. ASSERT `$$target_feature_files` contains only feature files.
4. `$$arguments_path` = DERIVE caller override or `${AIBDD_CONFIG_DIR}/arguments.yml` per [`references/execute-config-contract.md`](references/execute-config-contract.md).
5. ASSERT `$$arguments_path` exists; on failure STOP with `missing_arguments_path`.

### Phase 2 — LOAD runtime truth
> produces: `$$config`, `$$core_refs`, `$$runtime_refs`, `$$pre_hook_doc`

1. `$$config` = PARSE `$$arguments_path` as project config.
   1.1 `$preset_kind` = COMPUTE `${PRESET_KIND}` from `$$config`（default `web-backend` when key missing — backward compat for existing backend projects）
   1.2 BRANCH `$preset_kind`
       web-backend  → `$preset_contract_ref_key` = COMPUTE `BACKEND_PRESET_CONTRACT_REF`
       web-frontend → `$preset_contract_ref_key` = COMPUTE `FRONTEND_PRESET_CONTRACT_REF`
       other        → STOP with `unsupported_preset_kind`
2. `$$core_refs` = READ every configured `GHERKIN_*_REF`, `FILENAME_*_REF`, `DSL_OUTPUT_CONTRACT_REF`, and `${$preset_contract_ref_key}` (active key dispatched by `$preset_kind`).
3. ASSERT every core ref path exists and is read from path, not basename.
4. `$$runtime_refs` = READ `ACCEPTANCE_RUNNER_RUNTIME_REF`, `STEP_DEFINITIONS_RUNTIME_REF`, `FIXTURES_RUNTIME_REF`, and `FEATURE_ARCHIVE_RUNTIME_REF`.
5. ASSERT every runtime ref exists and declares command, glob, fixture, archive, or visibility behavior it owns.
6. `$backend_root` = COMPUTE parent directory of `.aibdd/` resolved from `$$arguments_path`.
7. ASSERT `$$config` contains non-empty `RED_PREHANDLING_HOOK_REF`; on failure STOP with `missing_red_prehandling_hook_ref`.
8. `$$pre_hook_doc` = READ resolved absolute path `join($backend_root, resolved($$config.RED_PREHANDLING_HOOK_REF))`; ASSERT file exists and is non-empty; on failure STOP route project BDD stack configuration.
9. ASSERT Worker completes Pre-Red gate described in `$$pre_hook_doc` before Phase 3; on NO-GO STOP with `pre_red_gate_blocked`.
10. `$snapshot` = DERIVE runtime ref paths and content fingerprints including `RED_PREHANDLING_HOOK_REF`.

### Phase 3 — BUILD DSL and preset registry
> produces: `$$dsl_index`, `$$preset_registry`

1. `$shared_dsl` = READ shared DSL path from `$$config`; missing shared DSL becomes empty entries.
2. `$package_dsl` = READ package DSL path from `$$config`.
3. ASSERT `$package_dsl` exists; on failure STOP route `/aibdd-plan`.
4. `$$dsl_index` = DERIVE merged package-over-shared index with entry-id and placeholder-aware L1 pattern indexes.
5. ASSERT no same-tier duplicate ids and every entry has `id`, `L1`, `L4`, `L4.preset`, and `L4.source_refs`.
6. `$$preset_registry` = DERIVE each `L4.preset.name` to `.claude/skills/aibdd-core/assets/boundaries/<preset-name>/`.
7. ASSERT preset layout per `${$preset_contract_ref_key}` § Layout SSOT (resolved via `$$core_refs` in Phase 2 step 2) for every preset in `$$preset_registry`. The four assertions below mirror that SSOT verbatim; if the SSOT changes, this step changes with it.
   7.1 ASSERT `handler-routing.yml` exists at preset root (Layout SSOT L1).
   7.2 ASSERT `handlers/<handler>.md` exists for every handler id referenced by `L4.preset.handler` in `$$dsl_index` (Layout SSOT L2).
   7.3 ASSERT `variants/<variant>.md` exists for every variant id referenced by `L4.preset.variant` in `$$dsl_index` (Layout SSOT L3).
   7.4 ASSERT preset name resolves directly to the directory name; no alias resolution is allowed (Layout SSOT L4).
8. ASSERT `web-backend` entries have `sentence_part == handler`.
9. ASSERT `web-frontend` entries have `sentence_part == handler`.

### Phase 4 — ARCHIVE runtime features
> produces: `$$runtime_feature_files`

1. `$$runtime_feature_files` = DERIVE archive/copy/include destinations for `$$target_feature_files` from `FEATURE_ARCHIVE_RUNTIME_REF`.
2. TRIGGER the project-owned archive command or mechanical copy procedure.
3. ASSERT runtime feature glob sees every `$$runtime_feature_files`.
4. ASSERT no target feature is assumed runner-visible without archive proof.

### Phase 5 — COMPILE StepPlan
> produces: `$$step_plans`

1. LOOP per `$feature_file` in `$$runtime_feature_files`
   1.1 `$scenarios` = PARSE all Scenarios in `$feature_file`.
   1.2 LOOP per `$scenario` in `$scenarios`
       1.2.1 LOOP per `$step` in `$scenario.steps`
             1.2.1.1 `$match` = MATCH `$step.prose` against `$$dsl_index.l1_patterns`.
             1.2.1.2 ASSERT `$match` is exact and unique; on failure STOP route `/aibdd-spec-by-example-analyze`.
             1.2.1.3 ASSERT datatable/docstring shape matches matched entry bindings.
             1.2.1.4 ASSERT dynamic IDs resolve to declared Scenario, response, repository, or fixture truth.
             END LOOP
       END LOOP
   END LOOP
2. `$$step_plans` = DERIVE normalized StepPlan IR for every matched step.
3. ASSERT each StepPlan contains matched entry, preset tuple, surface, source refs, bindings, runtime inputs, context IO, forbidden list, and target step-def path.
4. ASSERT renderer inputs are fully present in StepPlan; on gap STOP route `/aibdd-plan`.

### Phase 6 — RENDER step definitions
> produces: `$$step_defs_touched`

1. LOOP per `$plan` in `$$step_plans`
   1.1 `$step_def` = RENDER step definition from `$plan`, handler doc, variant doc, and runtime step-definition ref.
   1.2 ASSERT matcher string equals matched `L1`.
   1.3 ASSERT body uses only handler/variant rendering slots.
   1.4 ASSERT body has no free-form step-def, raw locator, direct production internal import, inferred endpoint, inferred field, or inferred id.
   1.5 ASSERT body is not empty, `pass`, or `RED-PENDING`.
   1.6 WRITE target step-def path ← `$step_def`.
   1.7 MARK target path in `$$step_defs_touched`.
   END LOOP
2. ASSERT step glob sees all written step definitions.
3. ASSERT duplicate registration guard allows shared steps exactly once.

### Phase 7 — RUN until legal red
> produces: `$$behavior_report`, `$$red_handoff`

1. LOOP until legal red or stop, max 5
   1.1 `$visibility` = TRIGGER runtime dry-run/discovery command from `ACCEPTANCE_RUNNER_RUNTIME_REF`.
   1.2 ASSERT `$visibility` sees every target feature and Scenario; on failure STOP route project BDD stack config.
   1.3 `$$behavior_report` = TRIGGER acceptance runner for `$$runtime_feature_files`.
   1.4 `$failure_class` = CLASSIFY `$$behavior_report.first_failure` using [`references/legal-red-classification.md`](references/legal-red-classification.md).
   1.5 BRANCH `$failure_class`
       `value_difference` → RETURN legal red
       `expected_exception` → RETURN legal red
       `false_red_repairable` → GOTO #6.1
       `false_red_stop` → STOP with routeable false-red reason
       `unknown` → STOP with `unclassified_red_failure`
   END LOOP
2. ASSERT legal red exists; on budget exhaustion STOP with `red_loop_budget_exceeded`.
3. `$$red_handoff` = RENDER schema from [`references/handoff-schemas.md`](references/handoff-schemas.md), `$$behavior_report`, `$$step_plans`, `$$step_defs_touched`, and `$snapshot`.

### Phase 8 — EMIT handoff

1. ASSERT `$$red_handoff.behavior_test_report` contains no DSL mapping fields.
2. ASSERT `$$red_handoff.dsl_mapping` contains entry id, matched L1, preset, source refs, binding keys, and step-def path for every Scenario step.
3. EMIT `$$red_handoff` to caller.

## §3 CROSS-REFERENCES

- `/aibdd-green-execute` — consumes legal Red handoff and writes product code.
- `/aibdd-plan` — repairs DSL, source refs, binding truth, and preset tuple gaps.
- `/aibdd-spec-by-example-analyze` — repairs feature wording, Examples, datatable, and dynamic ID gaps.
