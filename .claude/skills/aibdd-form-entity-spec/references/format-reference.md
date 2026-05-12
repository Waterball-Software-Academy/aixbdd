# DBML 格式與型別推斷

## 型別對應

| 範例值 | DBML 型別 |
|--------|----------|
| `1`、`42` | `integer` |
| `"Alice"`、`"MacBook"` | `varchar` |
| 長文字（描述、內容） | `text` |
| `true`、`false` | `boolean` |
| `45000.5`、`0.8` | `decimal` |
| `2026-01-01` | `date` |
| `2026-01-01T00:00:00Z` | `timestamp` |
| 有限值域（`待付款`、`已付款`） | `enum` |

## 從 Rule 推導約束

| Rule 內容 | 對應約束 |
|-----------|---------|
| `<欄位>必須大於 0` | `[note: 'must be > 0']` 或 CHECK constraint |
| `<欄位>必須唯一` | `[unique]` |
| `<欄位>不可為空` | `[not null]` |
| `<欄位>長度不超過 N` | `[note: 'max length: N']` |
| 狀態流轉限制 | 在 Table Note 中記錄 |

## erm.dbml 輸出格式

```dbml
Table <table_name> {
  id       integer    [pk, increment]
  <field>  <type>     [<constraints>]

  Note: '<中文資料表說明>'
}

Enum <enum_name> {
  <value1>  [note: '<說明>']
  <value2>
}

Ref: <table_a>.<field> > <table_b>.<field>   // many-to-one
Ref: <table_a>.<field> - <table_b>.<field>   // one-to-one
```

## 便條紙格式

DBML 行尾 comment：`// CiC(<CATEGORY>): ...`

完整格式定義見 `../../aibdd-form-activity/references/cic-format.md`。

| 代碼 | 何時標記 |
|------|---------|
| `GAP` | 無法從 .feature 確定欄位型別或長度 |
| `ASM` | 推斷了 Enum 值域但不確定是否完整 |
| `AMB` | 關聯方向不確定 |
| `CON` | 同欄位跨 Feature 型別不一致 |
