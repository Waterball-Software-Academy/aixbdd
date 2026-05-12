---
name: aibdd-green-execute
description: Turn a legal Red handoff for target feature files green by verifying drift, editing product code only, detecting failure oscillation, and emitting a Green handoff. TRIGGER when Green execute is requested after aibdd-red-execute. SKIP when no legal Red handoff exists or the request is test, DSL, runtime, or architecture repair.
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-green-execute

Turn the Red target feature-file set green with product-code-only changes.

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
    purpose: Defines target, arguments, core reference, runtime reference, drift, and routing contracts
  - path: references/handoff-schemas.md
    purpose: Defines Red input and Green output schemas plus stable failure signature fields
  - path: references/legal-red-classification.md
    purpose: Defines legal Red evidence required before Green may edit product code
  - path: references/green-oscillation-detection.md
    purpose: Defines strict ping-pong detection, threshold, and STOP payload
```

## §2 SOP

### Phase 1 — RECEIVE red handoff
> produces: `$$payload`, `$$target_feature_files`, `$$red_handoff`, `$$arguments_path`

1. `$$payload` = READ caller payload with `target_feature_files`, `red_handoff`, optional `arguments_path`, optional `task_id`.
2. `$$target_feature_files` = PARSE `$$payload.target_feature_files` as non-empty path list.
3. `$$red_handoff` = PARSE `$$payload.red_handoff` using [`references/handoff-schemas.md`](references/handoff-schemas.md).
4. ASSERT `$$red_handoff.status == completed` and `$$red_handoff.stop_reason == none`.
5. ASSERT `$$red_handoff.target_feature_files` equals `$$target_feature_files`.
6. `$$arguments_path` = DERIVE caller override or `${AIBDD_CONFIG_DIR}/arguments.yml` per [`references/execute-config-contract.md`](references/execute-config-contract.md).
7. ASSERT `$$arguments_path` exists; on failure STOP with `missing_arguments_path`.

### Phase 2 — VERIFY red still valid
> produces: `$$config`, `$$runtime_refs`, `$$baseline_report`

1. `$$config` = PARSE `$$arguments_path` as project config.
2. `$$runtime_refs` = READ project-owned BDD stack runtime refs from `$$config`.
3. ASSERT runtime refs include runner command, feature visibility, step glob visibility, fixture contract, archive behavior, report output, and readable Red Pre-Red hook (`RED_PREHANDLING_HOOK_REF`).
4. `$$baseline_report` = TRIGGER acceptance runner for `$$target_feature_files` through `ACCEPTANCE_RUNNER_RUNTIME_REF`.
5. `$red_kind` = CLASSIFY `$$baseline_report.first_failure` using [`references/legal-red-classification.md`](references/legal-red-classification.md).
6. ASSERT `$red_kind` is `value_difference` or `expected_exception`; on failure STOP route `/aibdd-red-execute`.
7. ASSERT not all target feature files are green; on failure STOP with `red_invalid_already_green`.

### Phase 3 — VERIFY handoff drift
> produces: `$$runtime_snapshot`

1. `$dsl_now` = DERIVE current merged DSL index from `$$config`.
2. `$preset_now` = DERIVE current core preset registry from `$$red_handoff.dsl_mapping`.
3. `$visibility_now` = TRIGGER runtime visibility checks for target features and step globs.
4. ASSERT every handoff `dsl_entry_id`, `matched_l1`, preset tuple, `step_def_path`, and `source_refs` matches current truth.
5. ASSERT `$visibility_now` sees the same target features and step definitions as the Red snapshot.
6. `$$runtime_snapshot` = DERIVE current runtime ref path and content fingerprints including `RED_PREHANDLING_HOOK_REF`.
7. ASSERT `$$runtime_snapshot` does not drift from `$$red_handoff.runtime_refs_snapshot` for this target set; on failure STOP with routeable drift reason.

### Phase 4 — LOOP product code to green
> produces: `$$loop_history`, `$$product_files_modified`, `$$final_report`

1. `$$loop_history` = COMPUTE empty ordered list.
2. `$$product_files_modified` = COMPUTE empty ordered set.
3. LOOP until all target feature files green, max 5
   3.1 `$$final_report` = TRIGGER acceptance runner for `$$target_feature_files`.
   3.2 BRANCH `$$final_report.outcome`
       `passed` → RETURN green
       `failed` → CONTINUE
   3.3 `$signature` = DERIVE stable first-failure signature from `$$final_report` per [`references/green-oscillation-detection.md`](references/green-oscillation-detection.md).
   3.4 MARK `$signature` in `$$loop_history`.
   3.5 `$oscillation` = DETECT strict two-signature ping-pong in `$$loop_history` with default threshold 3.
   3.6 ASSERT `$oscillation` is false; on failure STOP with `oscillation_detected`.
   3.7 `$failure_kind` = CLASSIFY `$$final_report.first_failure` as product gap, test bug, runtime drift, or architecture veto.
   3.8 BRANCH `$failure_kind`
       `product_gap` → CONTINUE
       `test_bug` → STOP route `/aibdd-red-execute`
       `runtime_drift` → STOP route project BDD stack config
       `architecture_veto` → STOP with `architecture_veto`
   3.9 `$patch` = APPLY product-code change only for the first runner failure.
   3.10 ASSERT `$patch` touches no feature, archive, step-def, DSL, core ref, runtime ref, fixture convention, or BDD constitution file.
   3.11 MARK `$patch.files` in `$$product_files_modified`.
   END LOOP
4. ASSERT `$$final_report.outcome == passed`; on budget exhaustion STOP with `loop_budget_exceeded`.

### Phase 5 — EMIT green handoff

1. ASSERT `$$product_files_modified` contains product code only.
2. `$green_handoff` = RENDER schema from [`references/handoff-schemas.md`](references/handoff-schemas.md), `$$red_handoff`, `$$final_report`, `$$loop_history`, `$$product_files_modified`, and `$$runtime_snapshot`.
3. EMIT `$green_handoff` to caller.

## §3 CROSS-REFERENCES

- `/aibdd-red-execute` — produces the legal Red handoff consumed here.
- `/aibdd-refactor-execute` — consumes the Green handoff and performs behavior-preserving cleanup.
- `/aibdd-plan` — resolves source reference, DSL, preset, or architecture veto issues.
