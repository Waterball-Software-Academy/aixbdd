# Subagent Prompt Templates

Phase 4 用此檔提供的兩段 prompt（backend / frontend）並行 spawn 兩條 `general-purpose` subagent。

## 共通通過條件（兩條都適用）

```
PASS = HTTP 200 from `curl -fsS http://localhost:<port>/<path>` 三次連續成功（避免 transient）。
FAIL = 達到 max_iterations 仍未通過，或 iteration 過程中遇到 docker daemon 無回應 / build context 超 1 GB / unrecoverable port 衝突且無權釋放。
```

## 共通失敗排查清單（subagent 必讀）

1. **Port 衝突**：先 `lsof -ti:<port> | head` 與 `docker ps --filter "publish=<port>"` 看誰佔用。若是其他 docker container 且不屬於本 compose 專案，**改用 `expose: "<port>"` 並只在 internal docker network 通訊**（不對 host publish）；frontend 透過 service name 連 backend 即可。
2. **build context 過大**：檢查 `.dockerignore` 是否漏列 `.venv` / `node_modules` / `.next`。
3. **alpine 上 libc 缺失**：node-alpine 加 `libc6-compat`。
4. **next standalone 缺檔**：`messages/`、`public/` 在 builder stage `mkdir -p` 並 COPY。
5. **alembic 啟動失敗**：DATABASE_URL 必須走 service name (`postgres`) 而非 `localhost`。
6. **healthcheck 無 curl/wget**：image 內必須有其中一個（python-slim 已有 curl；node-alpine 已有 wget）。

---

## Backend subagent prompt template

```
你是 backend Docker 容器化測試 subagent，**只**負責驗證 backend service 能 build + up + 通過 health 檢查。

## 上下文
- repo_root: {repo_root}
- backend_dir: {backend_dir}
- backend service name in compose: backend
- backend container port: {backend_port}
- backend health path: {health_path}
- max_iterations: {max_iterations}

## 你的權限
- 可讀 / 改：{backend_dir}/ 之內任何檔（含 Dockerfile、app/、alembic/、requirements.txt、pyproject.toml）
- 可讀 / 改：{repo_root}/docker-compose.yml 的 `services.backend` 與 `services.postgres` 區段（不准動 frontend 區段）
- 不准改：{frontend_dir}/ 的任何檔
- 不准 push 到 git；不准 docker prune；不准 docker system prune

## 迭代規則
For iteration in 1..{max_iterations}:
  1. `docker compose build backend`
     - 失敗：讀錯誤 → 改 backend Dockerfile 或 requirements / 程式碼 → 進下一次迭代
  2. `docker compose up -d postgres backend`
     - 失敗：讀 `docker compose logs backend --tail=200` → 修 → 進下一次迭代
  3. 等 backend healthcheck 變綠（最多 60 秒；用 `docker inspect aixbdd-backend --format '{{.State.Health.Status}}'` 輪詢）
  4. 進容器內探測：`docker compose exec -T backend curl -fsS http://localhost:{backend_port}{health_path}`
     - 連續 3 次成功 → PASS、跳出迴圈
     - 任何一次失敗或 timeout → 讀 logs → 修 → 進下一次迭代

## 通過後回報（JSON）
```json
{
  "status": "pass",
  "iterations": <N>,
  "last_curl_status": 200,
  "last_curl_body": "<前 200 字元>",
  "summary": "在第 N 次迭代通過 / 修了哪些檔"
}
```

## 失敗回報（JSON）
```json
{
  "status": "fail",
  "iterations": {max_iterations},
  "last_curl_status": <code or "timeout">,
  "fail_reason": "<最具體 root cause；含關鍵 log 摘要>",
  "files_touched": ["..."]
}
```

## 不要做
- 不要動 frontend 服務或 frontend Dockerfile。
- 不要 `docker compose down -v`（會炸掉 postgres volume）；要重啟服務用 `docker compose restart backend` 或 `docker compose up -d --force-recreate backend`。
- 不要為了通過 test 假造 health endpoint；只能修 build / startup / migration。
```

---

## Frontend subagent prompt template

```
你是 frontend Docker 容器化測試 subagent，**只**負責驗證 frontend service 能 build + up + curl 通過。

## 上下文
- repo_root: {repo_root}
- frontend_dir: {frontend_dir}
- frontend service name in compose: frontend
- frontend container port: {frontend_port}
- frontend healthcheck path: /
- backend service name (依賴): backend, 透過 docker network 連 http://backend:{backend_port}
- max_iterations: {max_iterations}

## 你的權限
- 可讀 / 改：{frontend_dir}/ 之內任何檔（含 Dockerfile、src/、package.json、next.config.mjs）
- 可讀 / 改：{repo_root}/docker-compose.yml 的 `services.frontend` 區段（不准動 backend / postgres 區段）
- 不准改：{backend_dir}/ 的任何檔
- 不准 push 到 git；不准 docker prune

## 迭代規則
For iteration in 1..{max_iterations}:
  1. 確保 backend & postgres 已起：`docker compose up -d postgres backend`，等 backend health 變綠（若已綠則跳過等待）
  2. `docker compose build frontend`
     - 失敗：讀錯誤 → 改 frontend Dockerfile 或 package.json / next.config.mjs / src → 進下一次迭代
  3. `docker compose up -d frontend`
     - 失敗：讀 `docker compose logs frontend --tail=200` → 修 → 進下一次迭代
  4. 等 frontend healthcheck 變綠（最多 60 秒）
  5. 從 host 探測：`curl -fsS -o /tmp/fe-probe.html -w "%{http_code}" http://localhost:{frontend_port}/`
     - 200 → PASS（連續 3 次成功）
     - 任何一次失敗或 timeout → 讀 logs → 修 → 進下一次迭代

## 通過後回報（JSON）
```json
{
  "status": "pass",
  "iterations": <N>,
  "last_curl_status": 200,
  "last_curl_body_size": <bytes>,
  "summary": "通過 / 修了哪些檔"
}
```

## 失敗回報（JSON）
```json
{
  "status": "fail",
  "iterations": {max_iterations},
  "last_curl_status": <code or "timeout">,
  "fail_reason": "<最具體 root cause>",
  "files_touched": ["..."]
}
```

## 不要做
- 不要動 backend / postgres 服務。
- 不要把 frontend 預設 port 改成跟 backend 一樣或跟 postgres 一樣（會自找麻煩）。
- 不要 `docker compose down -v`。
- 不要為了過 test 把 healthcheck 路徑改成 trivially-200 的 stub；只能修 build / startup。
```

---

## Spawn 寫法（給 SKILL.md Phase 4 step 3 看的範例）

在 SKILL.md 內，這兩個 Agent 呼叫**必須**放在同一個 tool-use block：

```
<tool_use_block>
  Agent({
    description: "docker backend smoke",
    subagent_type: "general-purpose",
    prompt: <RENDERED backend template>,
  })
  Agent({
    description: "docker frontend smoke",
    subagent_type: "general-purpose",
    prompt: <RENDERED frontend template>,
  })
</tool_use_block>
```

兩個 tool call 寫在同一個 message → 並行；分開寫在兩個 message → sequential（**禁止**）。
