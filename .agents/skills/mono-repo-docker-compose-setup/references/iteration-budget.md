# Iteration Budget

每條 subagent 的迭代預算與 fail-stop 條件。

## Hard limits

| Limit | Value | Rationale |
|---|---|---|
| `max_iterations` per subagent | **5** | 經驗值：build / log-read / fix 三步約 2-3 min；5 次 ≈ 12-15 min 上限 |
| Single `docker compose build` timeout | 8 min | 大型 image 第一次抓基底要 ~5 min；8 min 足夠 |
| Single `docker compose up -d` timeout | 90 s | 含 postgres healthcheck waiting；超過代表 stuck |
| Healthcheck wait per iteration | 60 s | 服務啟動到 health 綠燈的合理時間 |
| `curl` retry within one iteration | 3 次連續 200 才算 pass | 避免 transient |

## Fail-stop 條件（subagent 必須立即停止並回報，不再迭代）

- `docker daemon not running` 或 `Cannot connect to the Docker daemon`
- `no space left on device`（磁碟滿）
- 連續兩次迭代修同一個檔但錯誤訊息完全沒變（代表沒 root-cause、瞎改沒用）
- Build context 上傳超過 1 GB（八成是 `.dockerignore` 漏列大資料夾）
- `port is already allocated` 且已嘗試切換到 `expose:` only 仍失敗（host 環境不可控）

## Skill-level fail-stop（Phase 5 用）

- 任一 subagent 回報 `status: fail` → skill 整體 fail-stop（不重新派送），由 user 接手。
- 任一 subagent 在 30 min 內未回報任何結果 → skill 主流程也 STOP（防 runaway）。

## Soft guardrails

- 鼓勵 subagent 在每次迭代開頭先**讀**前一次失敗的 log 至少 100 行才動手改；不讀 log 就改 Dockerfile 屬無 root-cause 行為。
- 鼓勵 subagent 使用 `docker compose logs --tail=200 <service>` 取代 `docker logs <container>`（compose 知道 service name 對應）。
