---
name: programlike-skill-creator
description: Author a new Claude skill whose SKILL.md follows the AIBDD program-like 規章 v1 — phase SOP, D/S/I verbs, SSA bindings, BRANCH flow, self-contained artifact closure, and SOP SSOT. Output a fully 規章-compliant skill directory ready for /skill-creator package_skill.py. TRIGGER when user says 寫一個新 skill / scaffold skill / 建一個 program-like skill / programlike-skill-creator. SKIP for legacy multi-section skill style — use /skill-creator instead.
metadata:
  user-invocable: true
  source: user-scope
---

# programlike-skill-creator

Scaffold + populate a 規章-v1-compliant skill directory from user intake.

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
  - path: references/spec.md
    purpose: 規章 SSOT v1 — SKILL.md layout / verb 三閉集 / SSA grammar / scope sigils / BRANCH / cognitive-type audit / reasoning artifacts
  - path: references/intake-questions.md
    purpose: Phase 1 訪談題庫（name / description / phases / refs / scripts / assets / reasoning）
  - path: assets/templates/skill-md.template.md
    purpose: SKILL.md 骨架樣板 v1（含 `$var = VERB args` SSA 範例 + placeholder for Phase 4 instantiation）
  - path: references/verb-whitelist.md
    purpose: §5 三閉集速查表（D-verbs / S-verbs / I-verbs）
  - path: references/compliance-checklist.md
    purpose: §15 C1–C16/C25 + reasoning quality gate checklist
  - path: references/references-vs-assets.md
    purpose: references/ vs reasoning/ vs scripts/ vs assets/ 抉擇參考表 + 決策樹
  - path: DESIGN_PURPOSE.md
    purpose: 規章設計北極星：D/S 區隔、script 抽取、S-density 演化方向
  - path: references/modeling-element-definition-schema.md
    purpose: Modeling Element Definition YAML schema；element vs field 邊界與 forbidden keys
```

## §2 SOP

### Phase 1 — INTAKE 使用者意圖
> produces: `$$name`, `$$desc`, `$$lang`, `$$phase_outline`, `$$rough_steps`, `$$resources`, `$$reasoning_plan`, `$$reasoning_resources`

1. [USER INTERACTION] `$$name`          = ASK skill name per [`references/intake-questions.md`](references/intake-questions.md) §1
2. [USER INTERACTION] `$$desc`          = ASK description per [`references/intake-questions.md`](references/intake-questions.md) §2
3. [USER INTERACTION] `$$lang`          = ASK skill prose language per [`references/intake-questions.md`](references/intake-questions.md) §3
4. [USER INTERACTION] `$$phase_outline` = ASK phase outline per [`references/intake-questions.md`](references/intake-questions.md) §4
5. [USER INTERACTION] `$$rough_steps`   = ASK per-phase rough steps per [`references/intake-questions.md`](references/intake-questions.md) §5
6. [USER INTERACTION] `$$resources`     = ASK references / scripts / assets / reasoning needed per [`references/intake-questions.md`](references/intake-questions.md) §6
7. [USER INTERACTION] `$$reasoning_plan` = ASK reasoning pipeline per [`references/intake-questions.md`](references/intake-questions.md) §7
8. `$$reasoning_resources` = DERIVE RP artifact list from `$$reasoning_plan`
9. [USER INTERACTION] `$confirm` = ASK "intake summary OK?"
10. BRANCH `$confirm` ? GOTO #2.1 : GOTO #1.1

### Phase 2 — VALIDATE intake against 規章
> produces: `$$verb_map`

1. `$name_ok` = MATCH `$$name`, /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/ ∧ length(`$$name`) ≤ 64
2. BRANCH `$name_ok` ? GOTO #2.3 : GOTO #2.2.1
   2.1 `$name_msg` = RENDER "skill name 必須是 kebab-case、≤64 字元、不可含空白 / 大寫 / underscore"
   2.2 EMIT `$name_msg` to user
   2.3 GOTO #1.1
3. `$desc_ok` = MATCH length(`$$desc`) ≤ 1024 ∧ no_angle_brackets(`$$desc`)
4. BRANCH `$desc_ok` ? GOTO #2.5 : GOTO #2.4.1
   4.1 `$desc_msg` = RENDER "description 必須 ≤1024 字元且不可含尖括號"
   4.2 EMIT `$desc_msg` to user
   4.3 GOTO #1.2
5. LOOP per `$ph` in `$$phase_outline`
   5.1 `$imperative` = JUDGE `$ph.name` against refs/spec.md §4.1 imperative-form criteria
   5.2 BRANCH `$imperative` ? GOTO #2.5.3 : GOTO #1.4
   5.3 ASSERT `$imperative`
   END LOOP
6. `$$verb_map` = CLASSIFY `$$rough_steps` per [`references/verb-whitelist.md`](references/verb-whitelist.md) D/S/I 三閉集
7. LOOP per `$step` in `$$rough_steps`
   7.1 IF `$$verb_map[$step]` == "unclassifiable":
       7.1.1 [USER INTERACTION] `$rephrased` = ASK "step `$step` 無法分類；請改寫"
       7.1.2 GOTO #2.6
   END LOOP
8. `$branch_ok` = JUDGE `$$rough_steps` 內 branching 已拆 IF/ELSE sub-step (per spec.md §7.1)
9. IF `$$reasoning_plan.enabled`:
   9.1 ASSERT every RP has id / context / slot / name / consumes / produces
   9.2 ASSERT every RP id is unique
   9.3 ASSERT Required Axis names cover `consumes[*].kind == required_axis`
   9.4 ASSERT polymorphic slots have selector + variants + shared contract
   9.5 ASSERT ASK-capable RP has Material Reducer output traceability
   9.6 ASSERT every RP Modeling Element Definition uses [`references/modeling-element-definition-schema.md`](references/modeling-element-definition-schema.md) and lists output model elements only, per [`references/spec.md`](references/spec.md) §28.4.1
10. `$self_contained_ok` = JUDGE `$$resources` and `$$rough_steps` contain no runtime gate / rubric / contract dependency on external research/eval/plan files, per [`references/spec.md`](references/spec.md) §4.7.7
11. IF `$self_contained_ok` == false:
    11.1 `$closure_msg` = RENDER "runtime gate / rubric / contract 必須 inline、放入本 skill directory，或 promote 到 stable hub；不得引用 research/eval/plan 草稿"
    11.2 EMIT `$closure_msg` to user
    11.3 GOTO #1.6
12. BRANCH `$branch_ok` ? GOTO #3.1 : GOTO #2.12.1
    12.1 `$branch_msg` = DRAFT auto-dispatched form for branching-heavy rough steps
    12.2 EMIT `$branch_msg` to user
    12.3 GOTO #2.6

### Phase 3 — SCAFFOLD directory tree
> produces: `$$skill_dir`, `$$buckets`

1. `$$skill_dir` = COMPUTE `${HOME}/.claude/skills/${$$name}/` (or project-level if user specified)
2. `$exists` = MATCH path_exists(`$$skill_dir`)
3. IF `$exists`:
   3.1 [USER INTERACTION] `$choice` = ASK "overwrite or rename?"
   3.2 BRANCH `$choice`
       rename    → GOTO #1.1
       overwrite → CONTINUE
       cancel    → STOP
4. CREATE `$$skill_dir`
   4.1 IF CREATE permission denied:
       4.1.1 `$mkdir_msg` = RENDER "無法建立 skill directory；請檢查目標路徑權限"
       4.1.2 EMIT `$mkdir_msg` to user
       4.1.3 STOP
5. CREATE `${$$skill_dir}/references/`
6. `$$buckets` = THINK per [`references/references-vs-assets.md`](references/references-vs-assets.md) decision tree → classify each `$res` in `$$resources` into one of {references, reasoning, scripts, assets-template, assets-other}
7. ASSERT every `$res` in `$$resources` lands in exactly one bucket
8. IF `$$reasoning_plan.enabled` ∨ `$$buckets.reasoning` non-empty:
   8.1 CREATE `${$$skill_dir}/reasoning/`
   8.2 LOOP per `$ctx` in `$$reasoning_plan.contexts`
       8.2.1 CREATE `${$$skill_dir}/reasoning/${$ctx.id}/`
       8.2.2 LOOP per `$slot` in `$ctx.polymorphic_slots`
             8.2.2.1 CREATE `${$$skill_dir}/reasoning/${$ctx.id}/${$slot.dir}/`
             END LOOP
       END LOOP
9. IF `$$buckets.scripts` non-empty:
   9.1 LOOP per `$lang` in `$$buckets.scripts.langs`
       9.1.1 CREATE `${$$skill_dir}/scripts/${$lang}/`
       END LOOP
10. IF `$$buckets.assets-template` ∨ `$$buckets.assets-other` non-empty:
   10.1 CREATE `${$$skill_dir}/assets/`
   10.2 IF `$$buckets.assets-template` non-empty: CREATE `${$$skill_dir}/assets/templates/`

### Phase 4 — POPULATE SKILL.md per 規章 layout
> produces: `$$skill_md_path`

1. `$tmpl`           = READ [`assets/templates/skill-md.template.md`](assets/templates/skill-md.template.md)
2. `$frontmatter`    = RENDER `$tmpl` §frontmatter, vars={name=`$$name`, desc=`$$desc`, lang=`$$lang`}
3. `$title`          = RENDER one-line imperative role sentence ← `$$desc`
4. `$refs_yaml`      = RENDER `$tmpl` §1 REFERENCES YAML, refs=`$$buckets.references`
5. `$$skill_md_path` = COMPUTE `${$$skill_dir}/SKILL.md`
6. WRITE `$$skill_md_path` ← `$frontmatter` + `$title` + `$refs_yaml`
   6.1 IF WRITE partially succeeds then fails:
       6.1.1 DELETE `$$skill_md_path`
       6.1.2 `$write_msg` = RENDER "SKILL.md 寫入失敗；已刪除部分檔案"
       6.1.3 EMIT `$write_msg` to user
       6.1.4 STOP

7. LOOP per `$ph` in `$$phase_outline`
   7.1 `$ph_header`   = RENDER `### Phase ${$ph.n} — ${$ph.imperative_name}`
   7.2 `$produces`    = DERIVE `$$<vars>` produced by this phase from `$$rough_steps[$ph.n]`
   7.3 `$produces_ln` = RENDER `> produces: ${$produces}` (or skip if empty)
   7.4 `$step_block`  = DRAFT SSA-formatted SOP body ← `$$rough_steps[$ph.n]`, `$$verb_map`, assets/templates/skill-md.template.md §SSA-範例
   7.5 `$rp_cites`    = DERIVE inline RP cite steps from `$$reasoning_plan`, if this phase invokes RP
   7.6 `$step_block`  = RENDER `$step_block` plus `$rp_cites`
   7.7 ASSERT every RP cite uses `reasoning/.../*.md` inline and not §1 REFERENCES
   7.8 ASSERT every productive step in `$step_block` 起首 `$var = ` (per spec.md §23.1)
   7.9 ASSERT cross-phase `$$var` 已列在 `$produces` (per spec.md §24.2)
   7.10 ASSERT jump target 為 `#phase.step` literal (per spec.md §4.8)
   7.11 IF #4.7.10 assertion fails:
       7.11.1 `$goto_msg` = RENDER "jump target 未定義；重寫目前 phase 的 SOP body"
       7.11.2 EMIT `$goto_msg` to user
       7.11.3 GOTO #4.7.4
   7.12 WRITE `$$skill_md_path` ← append(`$ph_header`, `$produces_ln`, `$step_block`)
   END LOOP

8. IF `$$resources.cross_skills` non-empty:
   8.1 `$cross_section` = RENDER §3 CROSS-REFERENCES ← `$$resources.cross_skills`
   8.2 WRITE `$$skill_md_path` ← append(`$cross_section`)

9. TRIGGER `python3 ${PROGRAMLIKE_SKILL_DIR}/scripts/python/render_verb_glossary.py ${$$skill_dir}`  # inject canonical verb glossary block per spec.md §27
10. ASSERT block exists between H1 and `## §1 REFERENCES` (regex `<!-- VERB-GLOSSARY:BEGIN`)

### Phase 5 — POPULATE knowledge artifacts (references / assets)

1. LOOP per `$res` in `$$buckets.references`
   1.1 `$path`    = COMPUTE `${$$skill_dir}/references/${$res.filename}.md`
   1.2 `$content` = DRAFT declarative content stub ← `$res.purpose`, lang=`$$lang`
   1.3 ASSERT no_step_flow(`$content`) ∧ no_quality_gate_rubric(`$content`) per spec.md §4.7 SSOT 原則 + §4.7.6 gate rubric inline 規則
   1.4 IF `$res.purpose` 含 quality gate / rule_id checklist / pass criteria 字眼: STOP, EMIT「rubric 必 inline 於 SOP，不可進 references/」, GOTO #4.7.4 重寫 SOP body
   1.5 ASSERT `$content` contains no runtime gate / rubric / contract dependency on `research/`, `.cursor/plans/`, `*-outcome-eval.md`, external `eval.md`, or external `proposal.md`, per spec.md §4.7.7
   1.6 WRITE `$path` ← `$content`
   END LOOP

2. LOOP per `$res` in `$$buckets.assets-template`
   2.1 `$path`     = COMPUTE `${$$skill_dir}/assets/templates/${$res.filename}`
   2.2 `$skeleton` = DRAFT template skeleton ← `$res.purpose`, with `<!-- INSTRUCT: ... -->` per region (refs/references-vs-assets.md §"Inline-instruction template")
   2.3 ASSERT every region has `<!-- INSTRUCT: ... -->` marker
   2.4 IF #5.2.3 assertion fails:
       2.4.1 `$marker_msg` = RENDER "template skeleton 缺少 inline INSTRUCT marker；重寫此 template"
       2.4.2 EMIT `$marker_msg` to user
       2.4.3 GOTO #5.2.2
   2.5 WRITE `$path` ← `$skeleton`
   END LOOP

3. LOOP per `$res` in `$$buckets.assets-other`
   3.1 `$path` = COMPUTE `${$$skill_dir}/assets/${$res.subdir}/${$res.filename}`
   3.2 WRITE `$path` ← `$res.content`
   END LOOP

4. IF `$$resources.step_local_refs` non-empty:
   4.1 LOOP per `$ref` in `$$resources.step_local_refs`
       4.1.1 `$bucket`  = THINK per refs/references-vs-assets.md → classify `$ref`
       4.1.2 `$path`    = COMPUTE bucket-resolved path
       4.1.3 `$content` = DRAFT stub for `$ref.purpose`
       4.1.4 WRITE `$path` ← `$content`
       END LOOP

### Phase 6 — POPULATE reasoning/ artifacts and scripts/ stubs

1. IF `$$reasoning_plan.enabled`:
   1.1 `$rp_tmpl` = READ [`assets/templates/reasoning-phase.template.md`](assets/templates/reasoning-phase.template.md)
   1.2 `$poly_tmpl` = READ [`assets/templates/reasoning-polymorphism.template.md`](assets/templates/reasoning-polymorphism.template.md)
   1.3 LOOP per `$rp` in `$$reasoning_plan.rps`
       1.3.1 `$rp_path` = COMPUTE `${$$skill_dir}/reasoning/${$rp.context}/${$rp.slot}-${$rp.slug}.md`
       1.3.2 `$rp_doc`  = RENDER `$rp_tmpl`, vars=`$rp`
       1.3.3 ASSERT `$rp_doc` has frontmatter and `### 1.1 Required Axis`
       1.3.4 WRITE `$rp_path` ← `$rp_doc`
       END LOOP
   1.4 LOOP per `$slot` in `$$reasoning_plan.polymorphic_slots`
       1.4.1 `$poly_path` = COMPUTE `${$$skill_dir}/reasoning/${$slot.context}/${$slot.dir}/POLYMORPHISM.md`
       1.4.2 `$poly_doc`  = RENDER `$poly_tmpl`, vars=`$slot`
       1.4.3 WRITE `$poly_path` ← `$poly_doc`
       1.4.4 LOOP per `$variant` in `$slot.variants`
             1.4.4.1 `$variant_path` = COMPUTE `${$$skill_dir}/reasoning/${$slot.context}/${$slot.dir}/${$variant.path}`
             1.4.4.2 `$variant_doc`  = RENDER `$rp_tmpl`, vars=`$variant`
             1.4.4.3 WRITE `$variant_path` ← `$variant_doc`
             END LOOP
       END LOOP
2. IF `$$buckets.scripts` non-empty:
   2.1 LOOP per `$script` in `$$buckets.scripts`
       2.1.1 `$lang_ok` = MATCH `$script.lang` in {python, bash, node}
       2.1.2 IF `$lang_ok` == false:
             2.1.2.1 `$lang_msg` = RENDER "script.lang 僅支援 python / bash / node"
             2.1.2.2 EMIT `$lang_msg` to user
             2.1.2.3 STOP
       2.1.3 `$path`    = COMPUTE `${$$skill_dir}/scripts/${$script.lang}/${$script.name}.${$script.ext}`
       2.1.4 `$shebang` = DERIVE shebang line for `$script.lang`
       2.1.5 `$body`    = RENDER stub-template, vars={purpose=`$script.purpose`, raises="NotImplementedError"}
       2.1.6 WRITE `$path` ← `$shebang` + `$body`
       END LOOP

### Phase 7 — VALIDATE 規章 compliance
> produces: `$$validator_verdict`, `$$reasoning_graph_verdict`, `$$reasoning_eval_verdict`

1. `$validator_out` = TRIGGER `python3 ${PROGRAMLIKE_SKILL_DIR}/scripts/python/validate_skill_spec.py ${$$skill_dir}`  # includes C25 self-contained artifact closure
   1.1 IF validator script errors out:
       1.1.1 EMIT `$validator_out` to user
       1.1.2 STOP
2. `$$validator_verdict` = PARSE `$validator_out`, schema=findings-list
3. IF `$$validator_verdict.exit` ≠ 0:
   3.1 [USER INTERACTION] `$action` = ASK "violations 偵測：${$$validator_verdict.violations}；auto-remediate or manual fix?"
   3.2 BRANCH `$action`
       auto   → GOTO #4.7 (re-write affected SOP body)
       manual → WAIT for user fix; GOTO #7.1
       skip   → CONTINUE
4. `$graph_out` = TRIGGER `python3 ${PROGRAMLIKE_SKILL_DIR}/scripts/python/eval_reasoning_graph.py ${$$skill_dir}`
   4.1 IF reasoning graph eval script errors out:
       4.1.1 EMIT `$graph_out` to user
       4.1.2 STOP
5. `$graph_report` = READ `${$$skill_dir}/.quality/reasoning-graph-report.json`
6. `$$reasoning_graph_verdict` = PARSE `$graph_report`, schema=reasoning-graph-report
7. IF `$$reasoning_graph_verdict.ok` ≠ true:
   7.1 [USER INTERACTION] `$graph_action` = ASK "RP derivation graph violations 偵測；auto-remediate or ship as draft?"
   7.2 BRANCH `$graph_action`
       auto  → GOTO #4.7 (re-write affected RP/SOP handoff)
       draft → CONTINUE
       stop  → STOP
8. `$reasoning_eval_out` = TRIGGER `python3 ${PROGRAMLIKE_SKILL_DIR}/scripts/python/eval_reasoning_quality.py ${$$skill_dir}`
   8.1 IF reasoning eval script errors out:
       8.1.1 EMIT `$reasoning_eval_out` to user
       8.1.2 STOP
9. `$reasoning_eval_report` = READ `${$$skill_dir}/.quality/reasoning-eval-report.json`
10. `$$reasoning_eval_verdict` = PARSE `$reasoning_eval_report`, schema=reasoning-eval-report
11. IF `$$reasoning_eval_verdict.ok` ≠ true:
   11.1 [USER INTERACTION] `$reasoning_eval_action` = ASK "Reasoning Eval violations 偵測；auto-remediate or ship as draft?"
   11.2 BRANCH `$reasoning_eval_action`
       auto  → GOTO #4.7 (re-write affected RP body)
       draft → CONTINUE
       stop  → STOP

### Phase 8 — REPORT

1. `$summary` = DRAFT plain-language summary (≤3 sentences, lang=`$$lang`) ← `$$skill_dir`, count(`$$phase_outline`), count(`$$buckets.references`), count(`$$buckets.reasoning`), count(`$$buckets.scripts`), `$$validator_verdict`, `$$reasoning_graph_verdict`, `$$reasoning_eval_verdict`
2. EMIT `$summary` to user
   2.1 IF EMIT fails:
       2.1.1 WRITE `${$$skill_dir}/.scaffold-report.md` ← `$summary`
       2.1.2 STOP

## §3 CROSS-REFERENCES

- `/skill-creator` (Anthropic stock) — 既有 skill 創建 skill；本 skill 是其 program-like 變體；package_skill.py / quick_validate.py 互通
- `/aibdd-reinforce` — 本 skill 產出的 skill 違反規章時，可走 reinforce log 流程改善
- `aibdd-core::skill-spec.md`（未來） — 規章 v1 可能 promote 到 plugin reference hub
