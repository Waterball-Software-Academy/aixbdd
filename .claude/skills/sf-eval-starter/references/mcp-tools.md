# MCP Tools — SpecFormula `sf` server

> Defines the three MCP tools `sf-eval-starter` consumes. Pure declarative — no step flow.
>
> Server-side SSOT: `agent-server/src/services/mcp.service.ts`、`agent-server/src/agents/evaluator.ts`。

---

## §get_next_goal

| 欄位 | 值 |
|---|---|
| Tool name | `mcp__sf__get_next_goal` |
| Input schema | `{ project_path: string (required) }` |
| Output | `string` — 下一個 TDD goal 的 prompt text，或 `all-done` sentinel |
| Idempotency | 在無 `verify_goal` 介入的情況下，連續呼叫回傳同一 goal |
| Side effect | 無（純查詢） |

### `project_path` 參數

Worker 當前 CWD 的 absolute path。MCP `initialize` handshake 只帶 `clientInfo`，不帶 project context；server 用此參數路由到對應 evaluator session。每個 project 至多一個 active evaluator，跨 project 不會互相串台。

支援的形式（server 端 `normalizeProjectPath` 會把後兩種 POSIX-shaped Windows 路徑折回 native Windows 形式後再比對，三種寫法都會匹配到同一個 evaluator session）：

| 來源 shell | 命令 | 範例 |
|---|---|---|
| Windows PowerShell | `(Get-Location).Path` | `C:\Users\foo\proj` |
| POSIX shell（bash / zsh / Git Bash） | `pwd` | `/Users/foo/proj`（macOS / Linux）／ `/c/Users/foo/proj`（Windows Git Bash） |
| WSL | `pwd` | `/mnt/c/Users/foo/proj` |

其他 shell 的格式（cmd `cd` 的 `Microsoft.PowerShell.Core\FileSystem::` provider prefix、Cygwin `/cygdrive/c/...`、UNC `\\server\share\...`、相對路徑、含 `..` segment）一律不支援，server 會回 `INVALID_PROJECT_PATH` tool error。

錯誤碼一覽：
- 缺漏 → `MISSING_PROJECT_PATH`
- 格式不支援（含 ` `、`..`、相對路徑、不認得的 shell 形式）→ `INVALID_PROJECT_PATH`
- 形式合法但該 project 沒有 active evaluator → `NO_ACTIVE_EVALUATOR_SESSION`

### Output 形態

evaluator 回傳的 prompt text 中至少含以下兩個欄位（透過自然語言或 markdown 標頭表達）：
- `file_path` — 目標 `.feature` 檔的相對路徑
- `phase` — `RED` / `GREEN` / `REFACTOR` 之一

### §sentinel

當所有 feature 的所有 phase 都已驗證通過時，evaluator 回傳 `all-done` sentinel。具體 marker：prompt text 以 `all-done` 字樣開頭或包含 `Status: all-done`。Worker 偵測到此 marker 即跳至 SKILL.md Phase 8 (DONE)。

---

## §verify_goal

| 欄位 | 值 |
|---|---|
| Tool name | `mcp__sf__verify_goal` |
| Input schema | `{ command: string (required), project_path: string (required) }` |
| Output | `{ job_id: string, message: string }` — JSON-encoded payload（在 tool result 的 text content 內） |
| Synchronicity | **非同步 dispatch** — tool 立即 return；evaluator 在背景跑驗證 |
| Side effect | dispatch 之後 evaluator 在背景跑驗證；worker 從 `verify_goal_status` 拿 verdict（其餘 server 端的 event / log 為 server-internal，本 skill 不關注） |

### `command` 參數內容

要交給 evaluator 跑的**完整**測試指令，使用 worker project 自己的測試 runner（runner 名稱 / CLI 由 worker project 決定，本 skill 不預設）。**不要使用 placeholder**（`{feature_file}` / `{feature_files}` / glob 萬用字元都不行）— evaluator 直接執行命令原樣，並從命令文字抓 `.feature` token 比對 scope 與內容。

command 的測試範圍**不限於當前 goal 的 feature file**：通常要連已 DONE 的 feature files 一起跑，這樣 evaluator 才能在 raw output 看到 regression（之前綠的 feature 被新改動弄紅）。把 done feature 的相對路徑直接列在 command 內、或用 runner 的多檔 / glob 寫法傳入皆可。

選擇 command 的原則：
- 命令內**明列**當前 goal feature path 與所有已 DONE feature paths（一個不能少、不能多；evaluator 用 aggregate 驗證 scope 與內容）
- 連同已 DONE 的 feature files 一起跑，這樣 raw output 就能反映 regression
- 輸出必須能讓 evaluator 從 raw stdout/stderr 判斷 pass / fail
- 簡潔即可，evaluator 不依賴 worker 端寫 markdown 摘要

### `project_path` 參數

Worker 當前 CWD 的 absolute path；用法與語意同 §get_next_goal §`project_path` 參數段落，server 用此路由到對應 evaluator session。Active goal 由 evaluator 自身追蹤，worker 不需也不能 override。

### TMC gating

當沒有任何 TMC panel 透過 `attach: true` 連到該 project 的 evaluator session 時，server 拒絕 `verify_goal` call 並回 `NO_TMC_OPENED` tool error。Worker 應把這個錯誤 surface 給使用者（建議訊息：「請先打開 Mission Control panel，再讓 worker 繼續」）。

### Concurrency

當前面一次 `verify_goal` 的背景 job 還沒 settle，再呼一次 `verify_goal` 會回 `ALREADY_VERIFYING` tool error，error message 內含前一個 `job_id`。Worker 不應 dispatch 新的，改去 poll 該 `job_id`。

### ⚠️ 重要：tool 非同步語意

`verify_goal` 立即 return `{ job_id, message }`（JSON 字串放在 tool result 的 text content）。worker 必須拿 `job_id` 反覆 poll `mcp__sf__verify_goal_status` 直到 `completed=true` 才能拿到實際 verdict（見 §verify_goal_status）。

→ Worker 不要 sleep / 用 sub-agent 背景輪詢；直接每次 dispatch 後進入 poll loop（cadence 見下方 §verify_goal_status §Polling cadence）。

---

## §verify_goal_status

| 欄位 | 值 |
|---|---|
| Tool name | `mcp__sf__verify_goal_status` |
| Input schema | `{ job_id: string (required), project_path: string (required) }` |
| Output | `{ completed: boolean, message: string }` — JSON-encoded payload（在 tool result 的 text content 內） |
| Synchronicity | 同步、瞬回（讀 server 端記憶體 map） |
| Idempotency | 完全 idempotent — 同一 `job_id` 重 poll 只要 server 還活著就一直回相同結果 |
| Side effect | 無 |

### Output 形態

- `completed=false`：背景 drainer 還在跑。`message` 是「keep polling」的提示字串，可忽略。
- `completed=true`：drainer 已 settle。`message` 是 verdict text — 與舊版 `verify_goal` 同步回的內容相同（含 `passed` / `failed` / 失敗 step 列表）。

收到 `completed=true` 後就停止 poll、把 `message` 當 verdict 用、進下一輪。

### `job_id` 參數

由前一次 `verify_goal` 回傳，type 為 opaque string。Worker 不解析。傳錯 / 過期（server 重啟後）會回 `JOB_NOT_FOUND` tool error。

### `project_path` 參數

同 §verify_goal — worker 當前 CWD absolute path，server 用來路由 evaluator session。

### Polling cadence

固定 20 秒 poll 一次，且必須透過 bash `sleep 20` 達成（不要靠 LLM 內部的 wait / think / 多回合 turn 充當間隔 — 那會讓 cadence 漂掉、也讓 server 看不到 deterministic 的 poll 節奏）。Worker 不要更密（無價值，evaluator 通常跑數分鐘）；不要更疏（拖長整輪 loop 收尾時間）。

Worker 只看 `verify_goal_status` 回的 `completed` flag 來決定是否退出 poll；evaluator 在背景跑哪些 phase / 重試幾次都是 server-internal，不會也不需要從 MCP 介面暴露。
