---
name: skill-rca
description: >
  Perform Skill Root Cause Analysis for defective skill outputs; trace the earliest faulty
  skill artifact, classify the defect, propose the smallest corrective patch, and optionally
  apply it after approval. TRIGGER when request says 覆盤, skill RCA, 為什麼 skill 會產出這個錯誤,
  追蹤根因, or consistency analysis finds a skill-level issue. SKIP when the defect is only
  in generated product implementation and no skill artifact caused it.
metadata:
  user-invocable: true
  source: user-scope
  skill-type: planner
---

# skill-rca

Perform root cause analysis on defective skill behavior and land the smallest safe skill-artifact correction.

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

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `references/defect-types.md` | global | 定義 skill 缺陷分類與向後驗證規則 |
| R2 | `references/process-detail.md` | global | 定義 RCA 輸出格式、Program-like 偵測契約與整合規則 |

## §2 SOP

### Phase 1 — INTAKE defect context
> produces: `$$defect`, `$$target_skill_path`, `$$mode`, `$$issue_id`

1. $$mode = PARSE request invocation flags, enum={proposal-first, auto}
2. $$defect = PARSE incoming request for defective artifact, observed problem, expected behavior
3. $$target_skill_path = PARSE incoming request for source skill path or skill name
4. $$issue_id = PARSE incoming request for optional issue id
5. $has_target = JUDGE $$target_skill_path is present
6. BRANCH $has_target ? GOTO #1.8 : GOTO #1.7
7. [USER INTERACTION] $$target_skill_path = ASK "哪個 skill 產出了這個缺陷？請提供 skill 名稱或路徑。"
8. ASSERT $$defect includes artifact, problem, and expected behavior

### Phase 2 — READ target skill structure
> produces: `$$skill_dir`, `$$artifact_set`, `$$artifact_graph`, `$$lifecycle_signals`, `$$step_index`, `$$public_contract`

1. $$skill_dir = COMPUTE canonical directory from $$target_skill_path
2. $skill_md = READ `${$$skill_dir}/SKILL.md`
3. $refs = READ `${$$skill_dir}/references/**` if directory exists
4. $assets = READ `${$$skill_dir}/assets/**` if directory exists
5. $reasoning = READ `${$$skill_dir}/reasoning/**` if directory exists
6. $scripts = READ `${$$skill_dir}/scripts/**` if directory exists
7. $manifest = READ `${$$skill_dir}/artifact-manifest.yml` if exists else empty manifest
8. $$artifact_set = PARSE collected files into skill artifact map
9. $$artifact_graph = DERIVE artifact nodes and consumer edges from $$artifact_set and $manifest
10. $$lifecycle_signals = DERIVE lifecycle drift signals from $$artifact_graph per `references/process-detail.md` §Artifact lifecycle detection contract
11. $$step_index = PARSE $skill_md into ordered SOP or legacy step index
12. $$public_contract = PARSE $skill_md frontmatter and trigger-facing behavior
13. ASSERT $$artifact_set includes SKILL.md
14. ASSERT every $$lifecycle_signals item cites an artifact node or explicit manifest expectation

### Phase 3 — TRACE earliest faulty artifact
> produces: `$$trace`, `$$root_cause`

1. $trace_bundle = THINK per [`reasoning/skill-rca/00-trace-root-cause.md`](reasoning/skill-rca/00-trace-root-cause.md), input={$$defect, $$artifact_set, $$artifact_graph, $$lifecycle_signals, $$step_index}
2. $$trace = DERIVE RootCauseTrace.TraceNode set from $trace_bundle
3. $$root_cause = DERIVE RootCauseTrace.RootCause from $trace_bundle
4. ASSERT $$trace cites concrete file paths and line ranges
5. ASSERT $$root_cause identifies the earliest faulty skill artifact

### Phase 4 — CLASSIFY defect type
> produces: `$$defect_types`

1. $classification_bundle = THINK per [`reasoning/skill-rca/01-classify-defect.md`](reasoning/skill-rca/01-classify-defect.md), input={$$trace, $$root_cause, $$artifact_set, $$artifact_graph, $$lifecycle_signals}
2. $$defect_types = DERIVE DefectClassification.DefectType type names from $classification_bundle
3. $program_like_gap = DERIVE DefectClassification.ProgramLikeGap from $classification_bundle
4. ASSERT $$defect_types contains at least one Traditional Chinese type name

### Phase 5 — DRAFT minimal correction proposal
> produces: `$$proposal`, `$$backward_verdict`

1. $proposal_bundle = THINK per [`reasoning/skill-rca/02-propose-correction.md`](reasoning/skill-rca/02-propose-correction.md), input={$$trace, $$root_cause, $$defect_types, $$artifact_graph, $$lifecycle_signals, $$public_contract}
2. $$proposal = DERIVE CorrectionProposal.CorrectionProposal from $proposal_bundle
3. $$backward_verdict = DERIVE CorrectionProposal.VerificationResult from $proposal_bundle
4. ASSERT $$proposal names every target file and explains root-cause elimination
5. ASSERT $$backward_verdict includes public contract and original-defect replay results

### Phase 6 — APPROVE or APPLY correction
> produces: `$$applied_changes`

1. BRANCH $$mode
   auto           → GOTO #6.4
   proposal-first → GOTO #6.2
2. [USER INTERACTION] $approval = ASK "是否套用這份 skill 修復提案？請回覆 apply / revise / cancel。"
3. BRANCH $approval
   apply  → GOTO #6.4
   revise → GOTO #5.1
   cancel → GOTO #6.8
4. $$applied_changes = EDIT $$artifact_set per $$proposal
5. $clarify_log = MATCH path_exists(`${$$skill_dir}/Clarify Log`)
6. IF $clarify_log == true and $$issue_id is present:
   6.1 $entry = RENDER `{issue_id}-RCA` log entry from $$trace, $$defect_types, $$applied_changes
   6.2 WRITE `${$$skill_dir}/Clarify Log` ← append($entry)
7. GOTO #7.1
8. $$applied_changes = RENDER "not applied"
9. GOTO #8.1

### Phase 7 — REFORMULATE program-like structure
> produces: `$$reformulate_result`

1. $reformulate_bundle = THINK per [`reasoning/skill-rca/03-reformulate-decision.md`](reasoning/skill-rca/03-reformulate-decision.md), input={$$defect_types, $$proposal, $$applied_changes}
2. $migration_needed = DERIVE ReformulateDecision.MigrationNeed from $reformulate_bundle
3. BRANCH $migration_needed ? GOTO #7.6 : GOTO #7.4
4. $$reformulate_result = RENDER "not needed"
5. GOTO #8.1
6. $payload = DERIVE ReformulateDecision.ReformulatePayload from $reformulate_bundle
7. BRANCH $$mode
   auto           → GOTO #7.8
   proposal-first → GOTO #7.10
8. $$reformulate_result = DELEGATE `/programlike-skill-creator` with $payload
9. GOTO #8.1
10. $$reformulate_result = RENDER migration recommendation with $payload

### Phase 8 — REPORT RCA result

1. $summary = DRAFT readable RCA report from $$trace, $$defect_types, $$proposal, $$applied_changes, $$reformulate_result
2. EMIT $summary to requester
3. MARK skill completed

### Phase 9 — HANDLE fallback

1. $failure_kind = CLASSIFY runtime failure into known fallback categories
2. BRANCH $failure_kind
   missing-defect-context       → GOTO #9.3
   target-skill-unresolved      → GOTO #9.5
   target-skill-invalid         → GOTO #9.7
   trace-not-concrete           → GOTO #2.8
   classification-ambiguous     → GOTO #9.9
   verification-failed-twice    → GOTO #9.11
   edit-conflict                → GOTO #9.13
   reformulate-unavailable      → GOTO #9.15
   emit-failed                  → GOTO #9.17
3. [USER INTERACTION] $defect_detail = ASK "請提供壞掉的輸出、問題現象與期待行為。"
4. GOTO #1.2
5. $missing_target_msg = RENDER missing target skill guidance
6. EMIT $missing_target_msg to requester
7. $invalid_target_msg = RENDER "目標不是可分析的 skill directory"
8. EMIT $invalid_target_msg to requester
9. $$defect_types = DERIVE multiple matching Traditional Chinese type names
10. GOTO #5.1
11. $failed_proposal_msg = RENDER failed proposal with scope-change request
12. EMIT $failed_proposal_msg to requester
13. $conflict_msg = RENDER conflict paths and confirmation request
14. EMIT $conflict_msg to requester
15. $$reformulate_result = RENDER manual migration recommendation with $payload
16. GOTO #8.1
17. WRITE `${$$skill_dir}/.skill-rca-report.md` ← $summary
18. MARK fallback handled

## §3 CROSS-REFERENCES

- `/programlike-skill-creator` — converts or repairs skills into Program-like SKILL.md format.
- `/aibdd-reinforce` — dogfooding loop for AIBDD plugin skill failures when the defect is reinforcement signal.
- `/wb` — consultant router that may delegate skill RCA for broader Waterball workflows.
