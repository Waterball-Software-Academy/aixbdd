---
name: sf-eval-starter
description: Worker 連線 SF MCP 後接管全自動 RED→GREEN→REFACTOR 循環。每輪呼 mcp__sf__get_next_goal 拿下一個 TDD goal，DELEGATE 對應的 aibdd-{red,green,refactor}-execute sub-skill；組好 test command 後**先在本地 dry-run 一次確認 runner launchable**（環境準備是 worker 責任，evaluator 不會幫忙裝相依），再呼 mcp__sf__verify_goal 拿 job_id（非同步 dispatch），最後用 mcp__sf__verify_goal_status 透過 bash `sleep 20` 每 20 秒 poll 一次直到 completed=true 取出 verdict，再進下一輪 — 直到 evaluator 回 all-done。期間僅以 AssistMessage 單向回報進度，禁止 AskUserQuestion / ExitPlanMode。TRIGGER when /sf-eval-starter, 跑 SF eval, 進入 SF 全自動模式. SKIP when SF MCP 未啟動 / 已在另一個 SF skill 內運行 / user 想要 step-by-step.
metadata:
  user-invocable: true
  source: project-level
---

# sf-eval-starter

驅動 SpecFormula MCP 全自動跑完 AIBDD RED→GREEN→REFACTOR 循環，直到 evaluator 回 all-done。

<!-- VERB-GLOSSARY:BEGIN — auto-rendered from programlike-skill-creator/references/verb-cheatsheet.md by render_verb_glossary.py; do not hand-edit -->
> **Program-like SKILL.md — self-contained notation**
>
> **3 verb classes** (type auto-derived from verb name):
> - **D** = Deterministic — no LLM judgment required; future scripting candidate
> - **S** = Semantic — LLM reasoning required
> - **I** = Interactive — yields turn to user
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
> | EMIT | D | 輸出已生成資料 |
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
> | ASK | I | 問 user 等回應（仍配 `[USER INTERACTION]` tag） |
<!-- VERB-GLOSSARY:END -->

## §1 REFERENCES

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `references/mcp-tools.md` | Phase 1 / 2 / 7 | Defines `mcp__sf__get_next_goal` / `mcp__sf__verify_goal` / `mcp__sf__verify_goal_status` input-output schema, all-done sentinel format, async dispatch+poll contract |
| R2 | `references/sub-skill-mapping.md` | Phase 1 / 5 | Maps goal phase (RED / GREEN / REFACTOR) to DELEGATE target slash command and sub-skill location |
| R3 | `references/announce-format.md` | Phase 3 | Defines the AssistMessage progress-report markdown format for ANNOUNCE phase |
| R4 | `references/evidence-format.md` | Phase 6 | Defines the `command`-string format passed to `verify_goal`, with `{feature_file}` placeholder |

## §2 SOP

> **Global INVARIANT — Compact-conversation guard**：任何時候 worker 若偵測到 context 遺失、剛被 compact、或不確定當前 goal 是哪個，FIRST ACTION MUST BE Phase 2 (`mcp__sf__get_next_goal`)，禁止憑記憶猜測下一個 phase。
>
> **Global INVARIANT — Automated mode**：本 skill 一旦進入 main loop，禁止 `AskUserQuestion`、禁止 `ExitPlanMode`、禁止任何「請確認」「要不要繼續」字樣。對 user 唯一互動方式為 `AssistMessage` 單向進度回報。

### Phase 1 — BOOT
> produces: `$$boot_ok`, `$$cwd`

1. `$tools_visible` = MATCH `mcp__sf__get_next_goal` ∧ `mcp__sf__verify_goal` ∧ `mcp__sf__verify_goal_status` 三個皆在當前 tool list 中 per [`references/mcp-tools.md`](references/mcp-tools.md).
2. BRANCH `$tools_visible`
   `true`  → GOTO #1.4
   `false` → GOTO #1.3
3. STOP with EMIT "SF MCP 未就緒（reason: MCP tools 不在當前 tool list），請先啟動 SpecFormula Desktop App 並確認 Mission Control 顯示綠燈再重試".
4. `$sub_skills_present` = MATCH 三個 sub-skill `aibdd-red-execute` / `aibdd-green-execute` / `aibdd-refactor-execute` 皆存在於 worker project 的 `.claude/skills/` per [`references/sub-skill-mapping.md`](references/sub-skill-mapping.md).
5. BRANCH `$sub_skills_present`
   `true`  → GOTO #1.7
   `false` → GOTO #1.6
6. STOP with EMIT "SF MCP 未就緒（reason: aibdd-*-execute sub-skill 不存在於 worker project 的 .claude/skills/）".
7. `$$cwd` = TRIGGER 取得 worker CWD 的 absolute path（後續 phases 重用）。依當前 shell 選對應命令：
   - POSIX shell（bash / zsh / Git Bash / WSL）→ `pwd`
   - Windows PowerShell → `(Get-Location).Path`

   ASSERT 結果為下列三種 absolute path 形式之一（server 端 `normalizeProjectPath` 會把後兩種折回 native Windows 形式，三種寫法都可被 MCP 路由）：
   - POSIX 絕對路徑 `/...`（macOS / Linux pwd、或 Windows Git Bash pwd 的 `/c/...` 形式）
   - Windows 原生 `${letter}:\...`（PowerShell `(Get-Location).Path`）
   - WSL `/mnt/${letter}/...`（WSL pwd）

   on failure STOP with EMIT "SF MCP 未就緒（reason: 取得 worker CWD 失敗，無法路由到對應 evaluator session）".
8. `$$boot_ok` = COMPUTE `true`.

### Phase 1.5 — DOCKER_ENV_PREP
> produces: `$$docker_env_written`
>
> **WHY**：當 test runner 使用 docker（testcontainers / docker-compose / 直呼 docker SDK 預設值）時，host 上 docker runtime 的 socket 路徑會因為 Colima / OrbStack / Rancher Desktop / Podman 等而落在非 `/var/run/docker.sock` 的位置。把當前 docker context 的 endpoint 寫到 `$$cwd/.env`，讓 runner 自家 dotenv loader 帶入 `DOCKER_HOST` — test command 內**不需要**也**不應該**再帶 docker 相關 prefix。

1. `$docker_endpoint` = TRIGGER bash `docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null || true`（取當前 docker context 的 endpoint；找不到 docker CLI 或無 active context 時回空字串）。
2. BRANCH `$docker_endpoint`
   `空` → `$$docker_env_written` = COMPUTE `false`；RETURN（沒有 docker CLI 或沒設 active context；當前 goal 的 runner 若不需要 docker 即可繼續，需要時會在 Phase 6.5 preflight 直接失敗）
   `非空` → GOTO #1.5.3（不論是預設 socket 還是自訂 endpoint，下一步都要先確認 daemon 真的活著）
3. `$daemon_probe` = TRIGGER bash `docker info --format '{{.ServerVersion}}' 2>&1`（`docker context inspect` 只讀 CLI 設定，不會碰 daemon；必須額外打一次 `docker info` 才知道 Docker Desktop / Colima / OrbStack / Rancher Desktop / Podman daemon 是否真的在跑）。
4. `$daemon_up` = MATCH `$daemon_probe` 為純版本字串（例如 `27.3.1`）且**不含**任何下列字樣：`Cannot connect to the Docker daemon` / `Is the docker daemon running` / `error during connect` / `connection refused` / `permission denied while trying to connect` / `request returned ... Internal Server Error for API route` — 出現任一即視為 daemon down。
5. BRANCH `$daemon_up`
   `false` → STOP with EMIT「Docker engine 未啟動（reason: `docker info` 無法連線到 daemon；當前 context endpoint=${$docker_endpoint}；輸出：${$daemon_probe}）— 請手動啟動 Docker Desktop / Colima / OrbStack / Rancher Desktop / Podman machine 等 docker runtime，並等到 `docker info` 能成功回 ServerVersion 後再重跑 /sf-eval-starter。本 skill 不會代為啟動 docker daemon，因為啟動方式因 runtime 而異且通常需要 GUI 互動 / sudo / 額外授權」
   `true`  → GOTO #1.5.6
6. BRANCH `$docker_endpoint`
   `unix:///var/run/docker.sock` → `$$docker_env_written` = COMPUTE `false`；RETURN（daemon 已確認活著且在預設 socket，runner 用預設值即可，不需寫 .env）
   `其他值` → GOTO #1.5.7
7. TRIGGER bash 在 `$$cwd` 將 `DOCKER_HOST=$docker_endpoint` 寫入 `.env`（若已有舊 `DOCKER_HOST` 行則覆蓋，其他行原樣保留）：
   ```bash
   touch .env
   { grep -v '^DOCKER_HOST=' .env 2>/dev/null; printf 'DOCKER_HOST=%s\n' "$docker_endpoint"; } > .env.__sf_tmp && mv .env.__sf_tmp .env
   ```
8. `$$docker_env_written` = COMPUTE `true`.
9. ASSERT 若 `$$cwd/.env` 不在 git ignore 範圍 worker 必須提示使用者（避免 commit secrets）；本 skill 不自動寫 `.gitignore`。

### Phase 2 — GET_NEXT_GOAL
> produces: `$$current_goal`

1. `$$current_goal` = TRIGGER `mcp__sf__get_next_goal({ project_path: $$cwd })` per [`references/mcp-tools.md`](references/mcp-tools.md) §get_next_goal.
2. `$is_done` = MATCH `$$current_goal` 為 `all-done` sentinel per [`references/mcp-tools.md`](references/mcp-tools.md) §sentinel.
3. BRANCH `$is_done`
   `true`  → GOTO #8.1
   `false` → GOTO #2.4
4. ASSERT `$$current_goal` 含 `file_path` 與 `phase` 欄位；on failure STOP with EMIT "SF MCP 回傳格式異常（reason: missing file_path/phase）".

### Phase 3 — ANNOUNCE
> produces: (none — pure side effect)

1. `$summary` = DRAFT progress markdown per [`references/announce-format.md`](references/announce-format.md), input=`$$current_goal`.
2. EMIT `$summary` to user as AssistMessage.
3. ASSERT 此 EMIT 不暫停 worker（不等 user reply、不 sleep）；CONTINUE 即進 Phase 4.

### Phase 4 — ANALYZE_AND_PLAN
> produces: `$$plan`

1. `$related_files` = READ files referenced by `$$current_goal.file_path` 與相關 source / test 檔案（in-head exploration）.
2. `$$plan` = THINK phase-specific 策略 ← `$$current_goal.phase`, `$related_files`.
3. ASSERT `$$plan` 為 in-memory 推理結果，不 WRITE 至任何檔案。
4. ASSERT 本 phase 不呼叫 `ExitPlanMode`、不呼叫 `AskUserQuestion`；ambiguity 自行做合理推論。

### Phase 5 — EXECUTE_SUBSKILL
> produces: `$$execute_outcome`
>
> **派發 / 等待 / 接續邊界**：
> - **派發點**：Phase 5.2 的 `DELEGATE /aibdd-{red,green,refactor}-execute` — 把 RED/GREEN/REFACTOR 該寫的程式碼工作整包丟給 sub-skill 處理。Worker 自己**不要**在這層動測試檔、step def、product code。
> - **等待點**：DELEGATE 是同步呼叫；sub-skill 跑完會把 execution report 物件**直接回傳**到 `$$execute_outcome`。Worker 在此 phase **不要 sleep、不要 poll、不要問 user、不要開背景 process** — 拿到回傳即繼續往下。
> - **接續點（不是退出點）**：sub-skill 回傳 = 階段檢查點 ≠ 整個 skill 結束。即使 `$$execute_outcome` 是 error，Phase 6 仍要組命令、Phase 7 仍要 dispatch verify_goal 讓 evaluator 收 fail。唯一允許 STOP 的條件已在 Phase 5.2 unknown 分支與 Phase 1 boot 檢查中列舉。

1. `$delegate_target` = DERIVE slash command per [`references/sub-skill-mapping.md`](references/sub-skill-mapping.md), input=`$$current_goal.phase`.
2. BRANCH `$$current_goal.phase`
   `RED`      → `$$execute_outcome` = DELEGATE `/aibdd-red-execute` ← `$$current_goal`, `$$plan`
   `GREEN`    → `$$execute_outcome` = DELEGATE `/aibdd-green-execute` ← `$$current_goal`, `$$plan`
   `REFACTOR` → `$$execute_outcome` = DELEGATE `/aibdd-refactor-execute` ← `$$current_goal`, `$$plan`
   *unknown*  → STOP with EMIT "未知 phase（reason: ${$$current_goal.phase} 不在 RED/GREEN/REFACTOR）"
3. ASSERT `$$execute_outcome` 為 sub-skill 同步回傳的 execution report 物件或 error 物件。
4. ASSERT 拿到回傳即進 Phase 6，不在此 phase 做任何 polling / wait / user confirm。
5. error 不導致 STOP — Phase 6 仍組命令、Phase 7 仍 dispatch verify_goal，讓 evaluator 收 fail 與診斷訊息。

### Phase 6 — PREPARE_TEST_COMMAND
> produces: `$$test_command`

1. `$$test_command` = DRAFT 一行**完整**的 shell command，內含「當前 goal 的 feature file 路徑」+「所有已 DONE 的 feature files 路徑」**全部明列**（不可使用 placeholder、不可用 glob / 萬用字元代替；evaluator 會直接從命令文字抓 `.feature` token 並比對涵蓋範圍與內容）。跑進 done 是為了讓 evaluator 從 raw output 看到 regression（之前綠的 feature 被新改動弄紅）。
2. command 用當前 worker project 自己的測試入口（package.json script、Makefile target、直接呼叫 runner binary 等都可以） — 本 skill 不預設 runner 名稱或 monorepo 慣例；組裝原則見 [`references/evidence-format.md`](references/evidence-format.md)。
3. ASSERT `$$test_command` 為非空字串、本輪 scope（goal + 所有 DONE）的 `.feature` 路徑**逐一**出現、長度 ≤ 4000 字元。

### Phase 6.5 — ENV_PREFLIGHT
> produces: `$$env_ok`
>
> **WHY**：evaluator session 跑在 worker project CWD 但**不會**幫忙裝相依、不會 \`cd\` 進子目錄、也不會替 worker 修專案檔。命令不能直接 launch 起來時，evaluator 會丟 \`env_error\` 並把 verdict 設為 'failed'，整輪白跑。Phase 6.5 把這層責任明確壓給 worker — 把命令在 worker session 本地先 dry-run 一次，確認 runner 真的會啟動（哪怕測試本身 fail）。

1. `$preflight_cmd` = COMPUTE `$$test_command` 原樣（已為完整命令，無 placeholder 需替換）。
2. `$preflight_output` = TRIGGER bash 在 `$$cwd` 執行 `$preflight_cmd`（允許 fail — 我們只在乎 runner 是否 launch 成功）。
3. `$launch_failed` = CLASSIFY `$preflight_output` 為以下其一：
   - `launch_ok` — runner 起得來、看得到 step 結果（pass、fail、undefined 都算 launch_ok）
   - `launch_failed` — 看到下列 env-level 訊號：`command not found` / `pnpm: No projects found` / `ModuleNotFoundError` / `ImportError`（fixture 載入前）/ `Cannot find package` / `behave: error: ...config not found` / `Makefile:* No rule` / `permission denied: ...binary` 等
4. BRANCH `$launch_failed`
   `launch_ok`     → `$$env_ok` = COMPUTE `true`；GOTO #6.7.1
   `launch_failed` → GOTO #6.5.5
5. `$prep_steps` = THINK 必要的環境準備動作（最常見：`pnpm install` / `pnpm -r install` / `uv sync` / `pip install -e .` / 啟動 dev server / 建 fixture DB / 加 \`PATH\` 環境變數）。**絕對不要**靠 evaluator 幫忙；這是 worker 的責任。
6. TRIGGER `$prep_steps` 透過 bash 在 `$$cwd` 執行；同類錯誤連續重試上限 2 次，避免 `pnpm install` 之類重複跑。
7. GOTO #6.5.2（再 dry-run 一次）；若仍 `launch_failed` 兩輪以上 → MARK 環境級失敗、`$$env_ok` = COMPUTE `false`、仍 GOTO #6.7.1（讓 evaluator 走 env_error 回報，verdict 自然 fail，但保留可診斷的痕跡 — 跳過下面的 local sanity check）。

### Phase 6.7 — LOCAL_SANITY_CHECK
> produces: `$$sanity_ok`
>
> **WHY**：Phase 5 的 sub-skill（aibdd-{red,green,refactor}-execute）即使沒實作完整、回 error，也不會 STOP 整個 skill。若 worker 沒 local 驗證就直接 dispatch verify_goal，evaluator 會花數分鐘跑一個註定 failed 的 case，浪費整輪 turn + LLM tokens。本 phase 在 GREEN / REFACTOR 對「Phase 6.5 已執行的 preflight output」加一條期待性檢查，不通過就回 Phase 5 重 DELEGATE，最多兩輪；兩輪都沒過才放手讓 evaluator 收 fail。
>
> RED phase **跳過本 phase** — RED 預期測試 fail（沒實作的端點該回 404 / step 該紅），先 evaluator legality check 再說。
>
> 注意：本 phase 重用 Phase 6.5 已產生的 `$preflight_output`，不重跑 bash。

1. BRANCH `$$current_goal.phase`
   `RED`      → `$$sanity_ok` = COMPUTE `true`；GOTO #7.1（跳過 sanity check）
   `GREEN`    → GOTO #6.7.2
   `REFACTOR` → GOTO #6.7.2
2. BRANCH `$$env_ok`
   `false` → `$$sanity_ok` = COMPUTE `false`；GOTO #7.1（環境失敗，sanity 無意義，直接讓 evaluator 收 env_error）
   `true`  → GOTO #6.7.3
3. `$tests_all_pass` = MATCH `$preflight_output` 為「runner 報告 all tests pass」的訊號（依 runner 而定，常見 signal：`X scenarios passed, 0 failed, 0 skipped` / `X passed, 0 failed` / `Took ... — 0 failed` / 沒有 `Failing scenarios:` 區塊 / exit code = 0；同 runner 多訊號取交集）。
4. BRANCH `$tests_all_pass`
   `true`  → `$$sanity_ok` = COMPUTE `true`；GOTO #7.1
   `false` → GOTO #6.7.5
5. `$sanity_retry_count` = COMPUTE 本 goal 的 sanity retry 計數（首次進本 phase 為 0）；ASSERT 上限為 **2**。
6. BRANCH `$sanity_retry_count < 2`
   `true`  → 增量計數，GOTO #6.7.7
   `false` → `$$sanity_ok` = COMPUTE `false`；EMIT AssistMessage「local sanity check 兩輪都沒通過，仍 dispatch verify_goal 讓 evaluator 收 fail 與診斷訊息」；GOTO #7.1
7. EMIT AssistMessage「Phase 6.5 preflight 顯示測試仍未全綠，sub-skill 可能沒實作完成；回 Phase 5 重 DELEGATE（第 ${sanity_retry_count + 1} 輪 / 上限 2 輪）」。
8. GOTO #5.1（重跑 EXECUTE_SUBSKILL → Phase 6 → Phase 6.5 → Phase 6.7；test_command 已是完整命令、Phase 6 重組是冪等的）。

### Phase 7 — VERIFY_AND_LOOP
> produces: `$$last_verdict`

1. `$dispatch_payload` = TRIGGER `mcp__sf__verify_goal({ command: $$test_command, project_path: $$cwd })` per [`references/mcp-tools.md`](references/mcp-tools.md) §verify_goal.
2. `$dispatch` = PARSE `$dispatch_payload` 取出 `$dispatch.job_id` (string)；ASSERT 非空字串，on failure STOP with EMIT "verify_goal dispatch 回傳缺 job_id（reason: ${$dispatch_payload}）".
3. LOOP — poll until completed（budget: 90 次 ≈ 30 分鐘上限；exit on `completed=true`）:
   1. `$status_payload` = TRIGGER `mcp__sf__verify_goal_status({ job_id: $dispatch.job_id, project_path: $$cwd })` per [`references/mcp-tools.md`](references/mcp-tools.md) §verify_goal_status.
   2. `$status` = PARSE `$status_payload` 取出 `$status.completed` (boolean) 與 `$status.message` (string).
   3. BRANCH `$status.completed`
      `true`  → `$$last_verdict` = COMPUTE `$status.message`；EXIT LOOP
      `false` → TRIGGER bash `sleep 20`（單一指令，禁止用 LLM 內部 wait/think 充當 sleep — 必須是 deterministic 的 bash sleep call，evaluator MCP server 才能拿到固定 20 秒節奏的 poll 流量）後 GOTO #7.3.1
4. ASSERT `$$last_verdict` 為非空字串。
5. ASSERT 本 phase 未開啟 sub-agent、純粹用 dispatch + bash-sleep + poll；verdict 從最後一次 status `completed=true` 的 message 取得。
6. CLEANUP — 進下一輪前把本輪 polling 殘留的非同步資源全部收掉，避免下一個 goal 的 turn 收到陳舊事件：
   1. `$bg_shells` = enumerate background bash list；對任何還在 running（特別是包 `verify_goal_status` 或 `sleep` 的）TRIGGER `KillShell`。
   2. `$monitors` = MATCH 本 phase 是否曾呼叫 `Monitor` / `ScheduleWakeup` / `CronCreate`；若有 TRIGGER 對應 cancel / `CronDelete`。
   3. ASSERT background process 清單為空、無 pending wakeup、無 active Monitor。
7. GOTO #2.1.

### Phase 8 — DONE
> produces: (none — terminal)

1. `$completion` = DRAFT 完成摘要 ← `$$current_goal` (last all-done sentinel), `$$last_verdict`.
2. EMIT `$completion` to user as AssistMessage（建議格式：`🎉 全部 phase 完成` + 簡短統計）。
3. RETURN.

