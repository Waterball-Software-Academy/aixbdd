# Truth Delta: 004-room-game-chat

**Plan Package**: `specs/plans/004-room-game-chat`
**Truth Root**: `specs/truth`

## /technical-research

| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| MODIFY | `specs/truth/techstack.md` -> `測試與驗證` | 補上前端 BDD 會驗證聊天區塊。 | 本輪新增準備頁與對戰頁聊天驗收。 |

## /api-plan

| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| ADD | `specs/truth/contracts/openapi.yaml` -> `POST /rooms/{roomId}/messages` | 新增送出房間訊息 API。 | 聊天需要獨立命令入口。 |
| MODIFY | `specs/truth/contracts/openapi.yaml` -> `RoomSnapshot.messages` | 房間快照新增 `messages` 欄位。 | 前端用同一輪詢入口取得訊息。 |

## /data-plan

| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| ADD | `specs/truth/data/data-model.dbml` -> `Table chat_messages` | 新增房間內訊息模型。 | 訊息生命週期需綁定房間與在場狀態。 |

## /dsl-refine

| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| ADD | `specs/truth/features/backend/房間聊天/雙方在場寫入房間對話.feature` | 新增雙方在場互傳的後端介面 feature。 | 承接 acceptance journey 的後端責任。 |
| MODIFY | `specs/truth/features/backend/房間聊天/dsl.md` -> `When: "{玩家}" 送出訊息 "{內容}"` | 明定送訊需落地 store 並回寫聊天列表。 | 後續 BDD step 需要一致驗證語意。 |
