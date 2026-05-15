# REST 命名與 HTTP Method

## Path

- **集合資源**：複數名詞、`kebab-case`（`/orders`、`/room-memberships`）
- **單一資源**：`/orders/{orderId}`
- **巢狀從屬**：子資源掛在父資源之下（`/rooms/{roomId}/players/{playerId}/secret`）
- **避免**在 path 末端塞動詞片語（見 `command-resource.md` 的「允許的命令型 POST」寫法）

## Method 約定（預設對照）

| 意圖 | Method | 典型 path |
|------|--------|-----------|
| 讀取單筆／列表 | `GET` | `/resources` 或 `/resources/{id}` |
| 建立資源 | `POST` | `/resources` |
| 全量取代 | `PUT` | `/resources/{id}`（少用，需推理包明確） |
| 部分更新 | `PATCH` | `/resources/{id}` |
| 刪除 | `DELETE` | `/resources/{id}` |
| **領域命令**（多欄位規則／狀態遷移） | `POST` | 命令所屬之**名詞資源**（見 `command-resource.md`） |

## operationId

- 格式：`<verb><Resource>` camelCase（例如 `createOrder`、`submitPlayerGuess`）
- **注意**：operationId 可以用動詞；**path 仍以名詞片語為主**。兩者分離。

## Tags

- 與推理包 `EndpointGroup.group_id` 對齊，便於產生文件與測試分組。
