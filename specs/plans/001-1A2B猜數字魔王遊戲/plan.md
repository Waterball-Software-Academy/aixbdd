# Plan — 001-1A2B猜數字魔王遊戲

## 範圍

- Plan package：`001-1A2B猜數字魔王遊戲`
- Function packages：`01-遊戲大廳`、`02-魔王戰鬥`
- Boundary：`web-service`（Python FastAPI + PostgreSQL E2E）

## 對外契約

| 資源 | 檔案 |
|------|------|
| OpenAPI 共用 schema | `specs/contracts/common.yml` |
| OpenAPI 操作 | `specs/contracts/game.api.yml` |
| 持久化狀態 | `specs/data/domain.dbml` |
| Dispatch 覆寫 | `specs/boundary-map.yml` |

## 設計決策（ASM，待產品確認）

| 項目 | 採用值 |
|------|--------|
| 玩家對魔王傷害 | `damage = A×100 + B×50`；15% 爆擊 ×2 |
| 玩家 HP | 1000 / 人 |
| 魔王 HP 上限 | 開局存活玩家數 × 1000 |
| 魔王對玩家傷害 | 以玩家密碼做 1A2B，同一套加權公式 |
| 魔王行動機率 | 群傷 40%／單體 30%／自療 20%／改密碼 10%；本輪曾 4A 則下一動 100% 改密碼 |

## 內部模組

- `RoomService` — 開房／加入／準備／開始
- `GameService` — 密碼設置、猜測回合、魔王回合編排
- `GuessCalculator` — 1A2B 純函式
- `DamageCalculator` — 加權與爆擊
- `BossAi` — 機率選行動與目標
- Repositories — `rooms`、`players`、`games`、`bosses` 持久化

## 下游

- `/aibdd-spec-by-example-analyze` — 為 rule-only feature 填 Examples
- `/aibdd-auto-starter` — 若尚未有 walking skeleton，需先產出 `app/` 與 Behave 測試樹
