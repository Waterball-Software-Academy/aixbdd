# 反模式（撰寫 OpenAPI 時避免）

## Path 與 RPC 氣味

- **Path 出現動詞**：`/joinRoom`、`/startGame`、`/setReady`。改成名詞集合或從屬資源（見 `rest-naming.md`、`command-resource.md`）。
- **萬用動詞 bucket**：`/execute`、`/action`、`/do` 接上模糊名詞，卻未在 schema 描述領域語意。

## 狀態與流程

- **純狀態 API**：只接受目標狀態字串、不做其他領域效果。應併入具名業務操作或改由後台專用 contract。
- **過細流程**：可由單一命令完成的動作拆成多個無讀模型之中間步驟，導致前端易壞、難測。

## 讀模型

- **大量 `204 No Content`** 且無對應 **GET** 或實體 **snapshot**，迫使客戶端拼本地狀態或狂刷不存在的讀取路徑。
- **回應欄位與狀態機不一致**：例如 `gameEnded: true` 但無從得知 `outcome`（勝負）；應在 schema `description` 或 `required` 組合中消除矛盾。

## 錯誤處理

- **同類失敗**混用 `403` 與 `422` 卻未定義專案判準。
- 各 operation 引入**不同**錯誤 schema 形狀（有的只有 `message`，有的多 `details` 卻未共用）。

## 安全與職責

- 把**只可後端裁定**的結果放在 request（例如隨機抽樣結果、對手底牌、作弊級參數），卻標為正式 API 的一部分。
- **path 上的 `{playerId}`** 與實際呼叫端身分無驗證關聯，卻假設「知道 UUID 即可代操」— 若推理包未定 auth model，應 **GAP** 明示風險與預設假設。

## 技術形狀

- `responses.'200': { $ref: '#/components/schemas/X' }` 這類**省略 `content`** 的寫法（無效 OpenAPI）。
- `$ref` 指向不存在的檔案或錯誤的 fragment，導致 bundler 失敗。
