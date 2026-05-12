---
name: skill-family-consistency-analyze
description: Analyze any skill-set for broken references, unclear SSOT ownership, dead cross-skill targets, obsolete links, and unreachable artifacts. TRIGGER when user asks for skill family consistency, reference integrity, SSOT audit, or /skill-family-consistency-analyze. SKIP when the request is to validate one generated artifact rather than a skill-set.
metadata:
  user-invocable: true
  source: project-level dogfooding
  skill-type: utility
---

# skill-family-consistency-analyze

Analyze a skill family and report consistency problems before they become hidden contract drift.

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
  - path: references/problem-taxonomy.md
    purpose: Define supported consistency problem classes and severity defaults.
  - path: references/scope-and-ownership.md
    purpose: Define generic skill-set scope, artifact ownership, and ignored paths.
  - path: references/report-schema.md
    purpose: Define JSON and Markdown report shape emitted by the analyzer.
```

## §2 SOP

### Phase 1 — BIND analysis scope
> produces: `$$target_roots`, `$$report_paths`, `$$scan_options`

1. `$$target_roots` = READ caller payload `roots` or current skill-set path.
2. `$roots_exist` = MATCH every path in `$$target_roots` exists.
3. BRANCH `$roots_exist` ? GOTO #1.4 : GOTO #1.3.1
   3.1 STOP with missing root paths and request corrected input.
4. `$$scan_options` = DERIVE include-tests, output paths, and ignored paths per [`references/scope-and-ownership.md`](references/scope-and-ownership.md).
5. `$$report_paths` = DERIVE JSON and Markdown output paths from caller payload or default `.skill-family-consistency/`.

### Phase 2 — DISCOVER skill inventory
> produces: `$$skills`, `$$artifact_index`

1. `$script` = READ [`scripts/python/analyze_skill_family.py`](scripts/python/analyze_skill_family.py).
2. `$discovery_out` = TRIGGER `python3 scripts/python/analyze_skill_family.py ${$$target_roots}` with `--json-out ${$$report_paths.json}` and `--md-out ${$$report_paths.md}`.
3. `$$artifact_index` = PARSE `$discovery_out`, schema=json.
4. `$$skills` = DERIVE skill inventory from `$$artifact_index.skills`.
5. `$has_skills` = MATCH count(`$$skills`) > 0.
6. BRANCH `$has_skills` ? GOTO #3.1 : GOTO #2.6.1
   6.1 STOP with "no SKILL.md discovered in target roots".

### Phase 3 — CLASSIFY consistency findings
> produces: `$$findings`, `$$status`

1. `$$findings` = PARSE `$$artifact_index.findings`, taxonomy=[`references/problem-taxonomy.md`](references/problem-taxonomy.md).
2. `$schema_ok` = MATCH `$$artifact_index` satisfies [`references/report-schema.md`](references/report-schema.md).
3. BRANCH `$schema_ok` ? GOTO #3.4 : GOTO #3.3.1
   3.1 STOP with "analyzer report schema invalid".
4. `$deduped` = DERIVE unique findings by `(problem, file, target)`.
5. `$$status` = DERIVE final status per [`references/report-schema.md`](references/report-schema.md) status rules.

### Phase 4 — REVIEW semantic risk
> produces: `$$semantic_notes`

1. `$ambiguous` = MATCH `$$findings` where problem in `{duplicate_ssot, ambiguous_ssot_ownership, conflicting_rule_definitions, over_broad_reference_file, under_specified_reference_contract}`.
2. `$$semantic_notes` = CLASSIFY `$ambiguous` into likely owner issue, likely obsolete issue, likely split-reference issue, or needs human review.
3. `$hard_conflict` = MATCH `$$semantic_notes` contains contradictory owner or rule definitions.
4. BRANCH `$hard_conflict` ? GOTO #4.4.1 : GOTO #5.1
   4.1 MARK `$$status` as `fail`.
   4.2 GOTO #5.1

### Phase 5 — EMIT report
> produces: (none)

1. `$md_report` = READ `$$report_paths.md`.
2. `$json_report` = READ `$$report_paths.json`.
3. `$summary` = DRAFT concise user-facing summary from `$md_report`, `$$status`, `$$semantic_notes`.
4. EMIT `$summary` to user with report paths and top findings.
5. BRANCH `$$status == "fail"` ? GOTO #5.5.1 : GOTO #5.6
   5.1 STOP with non-zero quality gate verdict.
6. RETURN success.

## §3 CROSS-REFERENCES

- `/programlike-skill-creator` — Creates and validates program-like skills that this analyzer can audit.
