---
name: aibdd-auto-starter
description: 從 arguments.yml 與 templates 產生 walking skeleton；以 STARTER_VARIANT 分流 frontend / backend。支援 python-e2e（FastAPI + Behave）、java-e2e（Spring Boot 4 + Cucumber）、nextjs-storybook-cucumber-e2e（Next.js 16 + Storybook 10 + playwright-bdd）。TRIGGER when 使用者說初始化前/後端、建前/後端骨架、frontend/backend starter、walking skeleton，或被 kickoff 後續流程委派。SKIP when 需求是 feature-specific 業務頁面/元件/API client/model/service/API/step definition 實作或既有專案重構。
metadata:
  user-invocable: true
  source: project-level dogfooding
  skill-type: utility
---

# aibdd-auto-starter

Generate a walking skeleton from kickoff arguments and starter templates. The variant set covers both backend (`python-e2e` / `java-e2e`) and frontend (`nextjs-storybook-cucumber-e2e`); dispatch is driven entirely by `STARTER_VARIANT` in `arguments.yml`.

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
| R1 | `references/variants/python-e2e.md` | global | 定義 Python E2E backend starter（FastAPI + Behave + Alembic + Testcontainers）的 stack、placeholder、驗證與安全邊界 |
| R2 | `references/variants/java-e2e.md` | global | 定義 Java E2E backend starter（Spring Boot 4 + Cucumber + Flyway + Testcontainers + JdbcClient）的 stack、placeholder、驗證與安全邊界 |
| R3 | `references/variants/nextjs-storybook-cucumber-e2e.md` | global | 定義 Next.js 16 + React 19 + TypeScript 5 + Tailwind 4 + Storybook 10 + Playwright + playwright-bdd + Vitest 4 frontend starter 的 stack、placeholder、驗證與安全邊界 |

## §2 SOP

### Phase 1 — INGEST caller context
> produces: `$$skill_dir`, `$$cwd`, `$$arguments_path`, `$$caller_payload`

1. `$$skill_dir` = COMPUTE current skill directory path
2. `$$cwd` = COMPUTE current workspace directory path
3. `$$caller_payload` = READ caller payload if provided
4. `$payload_args` = MATCH `$$caller_payload.arguments_path`
5. BRANCH `$payload_args` ? GOTO #1.6 : GOTO #1.5.1
   5.1 `$$arguments_path` = COMPUTE `${$$cwd}/.aibdd/arguments.yml`
   5.2 GOTO #1.7
6. `$$arguments_path` = COMPUTE absolute path from `$$caller_payload.arguments_path`
7. `$args_exists` = MATCH path_exists(`$$arguments_path`)
8. BRANCH `$args_exists` ? GOTO #2.1 : GOTO #1.8.1
   8.1 `$missing_msg` = RENDER "`arguments.yml` 不存在；請先執行 /aibdd-kickoff 並選擇對應的 starter 變體"
   8.2 EMIT `$missing_msg` to user
   8.3 STOP

### Phase 2 — RESOLVE starter variant
> produces: `$$args_data`, `$$variant`, `$$variant_kind`, `$$variant_ref`, `$$variant_contract`

1. `$args_text` = READ `$$arguments_path`
2. `$$args_data` = PARSE `$args_text`, schema=`yaml`
3. `$variant_hint` = DERIVE starter variant from `$$args_data.STARTER_VARIANT`
4. BRANCH `$variant_hint`
   python-e2e                    → GOTO #2.10
   java-e2e                      → GOTO #2.10
   nextjs-storybook-cucumber-e2e → GOTO #2.10
   missing                       → GOTO #2.5
   other                         → GOTO #2.7
5. `$legacy_kind` = CLASSIFY `$$args_data` keys → one of {`python-e2e`, `java-e2e`, `none`}
   - prefix `PY_` 出現 → `python-e2e`
   - 含 `BASE_PACKAGE` 或 `GROUP_ID` 鍵 → `java-e2e`
   - 兩者皆無 → `none`
6. BRANCH `$legacy_kind`
   python-e2e → `$variant_hint` = COMPUTE `python-e2e`; GOTO #2.10
   java-e2e   → `$variant_hint` = COMPUTE `java-e2e`; GOTO #2.10
   none       → GOTO #2.6.1
   6.1 `$missing_variant_msg` = RENDER "`arguments.yml` 缺少 `STARTER_VARIANT`；請填 `STARTER_VARIANT: python-e2e` / `STARTER_VARIANT: java-e2e` / `STARTER_VARIANT: nextjs-storybook-cucumber-e2e`，或重新執行 /aibdd-kickoff"
   6.2 EMIT `$missing_variant_msg` to user
   6.3 STOP
7. `$unsupported_msg` = RENDER "目前 starter 支援 `python-e2e` / `java-e2e` / `nextjs-storybook-cucumber-e2e`；其他 variant 尚未實作。請改填其中之一，或重新執行 /aibdd-kickoff。"
8. EMIT `$unsupported_msg` to user
9. STOP
10. `$$variant` = COMPUTE `$variant_hint`
11. `$$variant_kind` = CLASSIFY `$$variant` →
    python-e2e                    → `backend`
    java-e2e                      → `backend`
    nextjs-storybook-cucumber-e2e → `frontend`
12. `$$variant_ref` = COMPUTE `references/variants/${$$variant}.md`
13. `$$variant_contract` = READ `$$variant_ref`
14. `$templates_dir` = COMPUTE `${$$skill_dir}/templates/${$$variant}`
15. `$templates_exist` = MATCH path_exists(`$templates_dir`)
16. BRANCH `$templates_exist` ? GOTO #3.1 : GOTO #2.16.1
    16.1 `$tmpl_msg` = RENDER "starter templates 不存在：`${$templates_dir}`"
    16.2 EMIT `$tmpl_msg` to user
    16.3 STOP

### Phase 3 — COLLECT project inputs
> produces: `$$project_dir`, `$$project_name`

1. `$payload_dir` = MATCH `$$caller_payload.project_dir`
2. BRANCH `$payload_dir` ? GOTO #3.3 : GOTO #3.2.1
   2.1 [USER INTERACTION] `$$project_dir` = ASK "專案要建立在哪個目錄？預設為目前工作目錄。"
   2.2 GOTO #3.4
3. `$$project_dir` = COMPUTE absolute path from `$$caller_payload.project_dir`
4. `$payload_name` = MATCH `$$caller_payload.project_name`
5. BRANCH `$payload_name` ? GOTO #3.6 : GOTO #3.5.1
   5.1 [USER INTERACTION] `$$project_name` = ASK "專案名稱？用於專案配置檔（pyproject.toml / pom.xml / package.json）與容器／scenario 命名。"
   5.2 GOTO #3.7
6. `$$project_name` = COMPUTE string from `$$caller_payload.project_name`
7. `$dir_ok` = MATCH `$$project_dir` is absolute path
8. ASSERT `$dir_ok`
9. `$name_ok` = MATCH length(`$$project_name`) > 0
10. ASSERT `$name_ok`
11. `$expected_args_path` = COMPUTE `${$$project_dir}/${$$args_data.AIBDD_ARGUMENTS_PATH}`
12. `$same_repo_args` = MATCH normalized_path(`$$arguments_path`) == normalized_path(`$expected_args_path`)
13. BRANCH `$same_repo_args` ? GOTO #4.1 : GOTO #3.13.1
    13.1 `$repo_role_label` = DERIVE label from `$$variant_kind`
        backend  → `backend`（kickoff layout = `${PROJECT_ROOT}/${BACKEND_SUBDIR}`）
        frontend → `frontend`（kickoff layout = `${PROJECT_ROOT}/${FRONTEND_SUBDIR}`）
    13.2 `$repo_msg` = RENDER "starter 只讀同 repo 內既有 AIBDD project config；請在已 kickoff 的 ${$repo_role_label} root 執行，且 arguments.yml 必須位於 `${project_dir}/${AIBDD_ARGUMENTS_PATH}`。若 layout 不對，請重跑 /aibdd-kickoff 並選擇正確的根目錄。"
    13.3 EMIT `$repo_msg` to user
    13.4 STOP

### Phase 4 — GENERATE skeleton
> produces: `$$generate_out`, `$$files_written`

1. `$cmd` = RENDER `uv run ${$$skill_dir}/scripts/generate-skeleton.py --project-dir "${$$project_dir}" --project-name "${$$project_name}" --variant "${$$variant}" --arguments "${$$arguments_path}"`
2. `$$generate_out` = TRIGGER `$cmd`
3. `$gen_ok` = MATCH `$$generate_out.exit_code == 0`
4. BRANCH `$gen_ok` ? GOTO #4.5 : GOTO #4.4.1
   4.1 `$gen_msg` = RENDER generation failure summary from `$$generate_out`
   4.2 EMIT `$gen_msg` to user
   4.3 STOP
5. `$$files_written` = PARSE `$$generate_out`, schema=`files-written-count`
6. `$skip_found` = MATCH `$$generate_out` contains `SKIP (exists)`
7. IF `$skip_found`:
   7.1 `$skip_msg` = RENDER "部分檔案已存在，generator 已依安全規則跳過覆蓋。"
   7.2 EMIT `$skip_msg` to user
   END IF

### Phase 5 — VERIFY starter health
> produces: `$$dry_run_passed`, `$$verification_out`

1. `$verify_cmd` = DERIVE dry-run command for `$$variant` from `$$variant_contract`
2. `$$verification_out` = TRIGGER `$verify_cmd` in `$$project_dir`
3. `$$dry_run_passed` = MATCH `$$verification_out.exit_code == 0`
4. BRANCH `$$dry_run_passed` ? GOTO #6.1 : GOTO #5.4.1
   4.1 `$verify_msg` = RENDER dry-run failure summary from `$$verification_out`
   4.2 EMIT `$verify_msg` to user
   4.3 STOP

### Phase 6 — REPORT

1. `$report` = DRAFT report with fields:
   - `status`: `completed`
   - `variant`: `$$variant`
   - `variant_kind`: `$$variant_kind`
   - `files_written`: `$$files_written`
   - `project_dir`: `$$project_dir`
   - `specs_location`: `${$$project_dir}/${$$args_data.SPECS_ROOT_DIR}`
   - `dry_run_passed`: `$$dry_run_passed`
2. EMIT `$report` to caller
3. `$post_install_hint` = DERIVE post-install / next-command hint for `$$variant` from `$$variant_contract`「完成後引導」section
4. `$summary` = DRAFT plain-language summary from `$report`，並附帶：下游 `/aibdd-discovery` 必須以 `project_dir` 為工作目錄（`cwd`），使 `AIBDD_ARGUMENTS_PATH` / `BDD_CONSTITUTION_PATH` / `DEV_CONSTITUTION_PATH` 相對路徑與 `.aibdd/arguments.yml` 同框解析；starter 不產生、不改寫 `specs/`。並附上 `$post_install_hint`（依 variant 提示對應的 dependency install / dev-server 指令）。
5. EMIT `$summary` to user

## §3 CROSS-REFERENCES

- `/aibdd-kickoff` — 上游產生 `arguments.yml` 與專案邊界設定（含 `STARTER_VARIANT`）
- `/aibdd-discovery` — walking skeleton 完成後的下一個需求探索入口
- `/aibdd-auto-frontend-msw-api-layer` — frontend variant 後續以 OpenAPI 生成 MSW handlers + API client（Stage 1）
- `/aibdd-auto-frontend-nextjs-pages` — frontend variant 後續逐 frame 落 Next.js 動態頁面（Stage 2）
