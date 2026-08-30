# Rule 1 - 每個 truth owner 必須各自維護一張表

- Level: `MUST`
- `truth-delta.md` 必須為每個 truth owner 保留獨立 section：`/technical-research`、`/api-plan`、`/data-plan`、`/dsl-refine`。
- 每個 section 只記錄該 owner 負責的 truth 規格，不得把 API、data、techstack、interface feature 的變更混在同一張表。
- 每張表固定使用 `動作`、`Truth 規格`、`改動摘要`、`原因` 四欄。

## Good Example

- 這個例子是好的，因為 API 變更只出現在 `/api-plan` section。

```md
## /api-plan

| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| ADD | `specs/truth/contracts/openapi.yaml` -> `POST /rooms/{roomId}/messages` | 新增送出房間訊息 API。 | 聊天需要獨立命令入口。 |
```

## Bad Example

- 這個例子是壞的，因為把不同 owner 的 truth 變更混在一起。

```md
## Truth Updates

| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| ADD | `specs/truth/contracts/openapi.yaml` -> `POST /messages` | 新增 API。 | 聊天需要。 |
| ADD | `specs/truth/data/data-model.dbml` -> `Table chat_messages` | 新增資料表。 | 聊天需要。 |
```

# Rule 2 - 動作分類必須使用 ADD、MODIFY、DELETE 或 NOOP

- Level: `MUST`
- `ADD` 表示新增既有 truth 中不存在的語意單元。
- `MODIFY` 表示改變既有 truth 語意單元的欄位、行為、生命週期、驗證條件、輸出內容或測試契約。
- `DELETE` 表示從 current truth 移除既有語意單元，或明確宣告某個既有行為不再成立。
- `NOOP` 表示該 truth owner 已檢查其負責 truth 範圍，但本輪不需要修改。
- 不得使用 `UPDATE`、`CHANGE`、`NEW`、`REMOVE` 等未定義動作。

## Good Example

- 這個例子是好的，因為動作值可被下游穩定解讀。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| MODIFY | `specs/truth/contracts/openapi.yaml` -> `RoomSnapshot.messages` | 將 `messages` 加入房間快照必回欄位。 | 前端用同一快照輪詢聊天訊息。 |
| NOOP | `specs/truth/contracts/openapi.yaml` -> `GET /rooms/{roomId}` | 已檢查讀取入口，不需新增端點。 | 現有快照入口足以承接。 |
```

## Bad Example

- 這個例子是壞的，因為動作值模糊。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| UPDATE | `openapi.yaml` | 改了一些東西。 | 需求變了。 |
```

# Rule 3 - Truth 規格必須記到語意單元層級

- Level: `MUST`
- `Truth 規格` 不應只寫檔案路徑，還要用 `->` 指到可被下游定位的語意單元。
- API truth 的語意單元可為 operation、schema、field、error code 或 response shape。
- Data truth 的語意單元可為 table、enum、ref、field、index 或 lifecycle note。
- Feature truth 的語意單元可為 feature file、Rule、Example 或 DSL 句型。
- Techstack truth 的語意單元可為分類、採用技術、排除技術或測試驗證策略。

## Good Example

- 這個例子是好的，因為下游可直接知道要讀哪個 truth 部分。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| ADD | `specs/truth/data/data-model.dbml` -> `Table chat_messages` | 新增房間內訊息模型。 | 訊息需綁定房間生命週期。 |
| MODIFY | `specs/truth/features/backend/房間聊天/dsl.md` -> `When: "{玩家}" 送出訊息 "{內容}"` | 新增送訊後必須落地 store 的驗證語意。 | Then 不能只信 API 回應。 |
```

## Bad Example

- 這個例子是壞的，因為只寫檔案，沒有語意定位。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| MODIFY | `specs/truth/data/data-model.dbml` | 更新資料模型。 | 聊天功能。 |
```

# Rule 4 - 高影響 MODIFY 或 DELETE 必須已有 clarify 依據

- Level: `MUST`
- 若變更會移除 API、改變既有 request/response 語意、刪除資料欄位、改寫既有 feature 行為或削弱 DSL 驗證契約，truth owner 必須先完成 `/clarify` 或在 handoff 中提供明確使用者決策。
- `/truth-delta` 不替 truth owner 做產品決策；若缺少確認依據，應停止寫入並要求回到 owner skill 的 clarify gate。
- 低風險新增、補充描述或不改外部語意的細節整理，可直接記錄。

## Good Example

- 這個例子是好的，因為 DELETE 有明確決策依據。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| DELETE | `specs/truth/contracts/openapi.yaml` -> `POST /rooms/{roomId}/messages` | 移除獨立送訊端點。 | 使用者於 clarify 決定改用既有 command channel。 |
```

## Bad Example

- 這個例子是壞的，因為直接刪除既有契約卻沒有確認依據。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| DELETE | `specs/truth/contracts/openapi.yaml` -> `POST /rooms/{roomId}/messages` | 移除端點。 | 我覺得用不到。 |
```

# Rule 5 - DSL 僅搬移權威位置時必須記為 MODIFY

- Level: `MUST`
- DSL row 若句型、參數、DataTable、預設值與實作契約都未改變，只是從模組 DSL 升格到介面根共用 DSL，或從根 DSL 下放到模組 DSL，必須記為一筆 `MODIFY`。
- `Truth 規格` 必須同時列出舊位置、新位置與 DSL 句型，摘要明示「權威位置搬移，語意不變」。
- 不得拆成 `DELETE + ADD`；這會讓下游誤判為移除舊行為並新增另一個行為。
- 若搬移同時改變契約，仍使用 `MODIFY`，但摘要必須另列實際語意改動，不得宣稱語意不變。

## Good Example

- 這個例子是好的，因為同一句型只是由單模組升格為跨模組共用，不會觸發錯誤的移除與新增任務。

```md
| 動作 | Truth 規格 | 改動摘要 | 原因 |
| --- | --- | --- | --- |
| MODIFY | `specs/truth/features/backend/房間聊天/dsl.md` → `specs/truth/features/backend/dsl.md` -> `Then: 這次操作被拒絕` | 權威位置搬移，語意不變。 | 第二個模組開始使用完全相同契約。 |
```

## Bad Example

- 這個例子是壞的，因為純搬移被拆成兩種行為變更，下游會產生錯誤的 BDD-REMOVE 與 BDD-RED。

```md
| DELETE | `specs/truth/features/backend/房間聊天/dsl.md` -> `Then: 這次操作被拒絕` | 刪除舊句型。 | 搬家。 |
| ADD | `specs/truth/features/backend/dsl.md` -> `Then: 這次操作被拒絕` | 新增共用句型。 | 搬家。 |
```
