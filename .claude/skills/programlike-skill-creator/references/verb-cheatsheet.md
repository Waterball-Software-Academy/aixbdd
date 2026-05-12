<!-- canonical verb cheatsheet — SSOT for the SKILL.md verb glossary blockquote.
     Injected verbatim (each line prefixed with `> `) by `scripts/python/render_verb_glossary.py`.
     Slim version. Full reference (examples / rationale / change history): `verb-whitelist.md`.
     Edit here ONCE → re-run render_verb_glossary.py per skill → all SKILL.md sync. -->

**Program-like SKILL.md — self-contained notation**

**3 verb classes** (type auto-derived from verb name):
- **D** = Deterministic — no LLM judgment required; future scripting candidate
- **S** = Semantic — LLM reasoning required
- **I** = Interactive — yields turn to user

**Yield discipline** (executor 鐵律): **ONLY** `I` verbs yield turn to the user. `D` and `S` verbs MUST NOT pause for user reaction. In particular:
- `EMIT $x to user` is **fire-and-forget** — continue immediately to the next step; do not wait for acknowledgment.
- `WRITE` / `CREATE` / `DELETE` are side effects, **not** phase boundaries — execution continues to the next sub-step.
- Phase transitions (Phase N → Phase N+1) and sub-step transitions are **non-yielding**.
- Mid-SOP messages of the form 「要繼續嗎？」/「先 review 一下？」/「先 checkpoint？」/「先停下來確認？」/「want me to proceed?」/「should I continue?」are **FORBIDDEN**. The ONLY way to ask the user is an `[USER INTERACTION] $reply = ASK ...` step.
- `STOP` / `RETURN` are terminations, not yields — no next step follows.

**SSA bindings**: `$x = VERB args` (productive steps name their output);
`$x` is phase-local; `$$x` crosses phases (declared in phase header's `> produces:` line).

**Side effect**: `VERB target ← $payload` — `←` arrow = "write into target".

**Control flow**: `BRANCH $check ? then : else` (binary) or indented arms (multi);
`GOTO #N.M` = jump to Phase N step M (literal `#phase.step`).

**Canonical verb table** (T = D / S / I):

| Verb | T | Meaning |
|---|---|---|
| READ | D | 讀檔 → bytes / text |
| WRITE | D | 寫檔（內容已備好） |
| CREATE | D | 建立目錄 / 空檔 |
| DELETE | D | 刪檔（rollback） |
| COMPUTE | D | 純運算 |
| DERIVE | D | 從既定規則推算 |
| PARSE | D | 字串 → in-memory 結構 |
| RENDER | D | template + vars → string |
| ASSERT | D | 斷言 invariant；fail-stop |
| MATCH | D | regex / pattern 比對 |
| TRIGGER | D | 啟動 process / subagent / tool / script；output 可 bind |
| DELEGATE | D | 呼叫其他 skill |
| MARK | D | 紀錄狀態（譬如 TodoWrite） |
| BRANCH | D | 分支（吃 `$check` / `$kind` binding） |
| GOTO | D | 跳 `#phase.step` literal |
| IF / ELSE / END IF | D | 條件 sub-step |
| LOOP / END LOOP | D | 迴圈（必標 budget + exit） |
| RETURN | D | 提前結束 phase |
| STOP | D | 終止整個 skill |
| EMIT | D | 輸出已生成資料（fire-and-forget；**不 yield**，continue 下一 step） |
| WAIT | D | 等待已 spawn 的 process |
| THINK | S | 內部判斷（不印 user） |
| CLASSIFY | S | 多類別分類 → enum 之一 |
| JUDGE | S | 二元語意判斷 |
| DECIDE | S | 從 user reply / context 推結論 |
| DRAFT | S | 生成 prose / 訊息 |
| EDIT | S | LLM 推 patch 改既有檔 |
| PARAPHRASE | S | 改寫 / 翻譯 prose |
| CRITIQUE | S | 批評 / 建議 |
| SUMMARIZE | S | 抽取重點 |
| EXPLAIN | S | 對 user 解釋 why |
| ASK | I | 問 user 等回應（仍配 `[USER INTERACTION]` tag）；**唯一允許 yield turn 給 user 的 verb**。**Planner-level skill** 對 user 的提問**必須 `DELEGATE /clarify-loop`**，不得直接 `ASK`（其他角色的 skill 自決）。 |
