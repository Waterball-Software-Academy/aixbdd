# Handler: <handler-id>

1. 這份檔記載一個 handler 的 runtime（red-execute 實作期）履約：它讀寫什麼 context、何時該用、不准做什麼。
2. 一個 handler 一個檔，檔名等於 boundary 支援的 handler ID。`handlers/` 目錄有幾個 handler 檔，就代表此 boundary 有幾份 runtime 文件（除非刻意不為某 handler 寫）。
3. 與 plan-time 的分工：`scripts/part_to_dsl.py` 談 plan-time 構造（template 怎麼生），本檔談 runtime 實作（step def 跑起來怎麼讀寫 context）。

## Role

1. 一句話定義此 handler 渲染/負責什麼（例：`<handler-id>` renders persisted backend state setup）。
2. 它屬於哪個 part 與哪些 keyword（與 DSL entry 的 `handler` 一致）：
   1. `part`：`<handler-id>`
   2. `keywords`：`<Given|When|Then|Background>`

## Trigger Contract

1. 描述「句子滿足什麼語意時」該選用這個 handler，讓分類者能據此判斷而不靠猜。

## Context Contract

1. Reads：列出此 handler 會讀的 context 欄位（例：`context.db_session`、`context.repos`、`context.ids`）。
2. Writes：列出它會寫回的 context 欄位與用途（例：寫入 persisted state 與後續步驟需要的 `context.ids`）。

## Forbidden

1. 逐條列出此 handler 不得做的事，每條講清楚 why（例：不得呼叫 backend API、不得發明 truth 以外的欄位、不得省略 required identity 欄位）。
