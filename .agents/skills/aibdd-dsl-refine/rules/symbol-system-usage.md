# 符號系統使用判斷

填 isa_steps 的 table 時，用框架符號表達資料流與斷言。每條 isa_step 的 instruction
須對上專案 `specs/isa.yml`（及各 package 的 `*.isa.yml`）某條 instruction 的 format；
指令型別與 format 一律以該專案 isa.yml 為準，本檔不重抄指令型別。

## 兩個替換層（同格共存，先分清楚）

dsl.yml 的 table 值同時夾雜兩種記號，展開時機不同：

| 記號 | 屬於 | 何時被替換 | 範例 |
|------|------|-----------|------|
| `{{name}}` | dsl 模板 | preprocess 展開 .dsl.feature → .isa.feature 時，用 format 佔位或 params 代入 | `name: '{{alias}}'` |
| `$ > < & @` | ISA 符號 | 不被 dsl 替換，原樣留進展開後 feature，由 ISA backend 執行期解讀 | `'>{{alias}}.id': '<userId'` |

所以 `'>{{alias}}.id': '<userId'`：`{{alias}}` 先被換成 Alice，留下 ISA 的 `>Alice.id / <userId` 捕獲對。

## 三套 ISA 符號（框架 SSOT）

| 系統 | 用途 | 代表語法 |
|------|------|----------|
| VAR | 變數擷取／引用 | `>contextKey` `<executionKey` `$var` `${var}` |
| CAS | 約束斷言 | `&isNum` `&gt(0)` `&between(18,65)` `&oneOf(...)` |
| TIME | 時間表達式 | `@time("now+7d")` `@date("2000-01-15")` |

### VAR — 四種語法

| 語法 | 位置 | 意義 |
|------|------|------|
| `>contextKey` | DataTable 標頭 | 定義要存的變數名 |
| `<executionKey` | DataTable 資料列 | 指定從執行結果擷取哪個欄位（與同欄 `>` 配對） |
| `$var` | 任何值位置 | 引用變數，保留原始型別（Integer/String…） |
| `${var}` | 字串中 | 引用變數並轉字串，可組合多個（`${a},${b}`） |

巢狀路徑用 dot / 索引：`<order.details.id`、`<items[0].name`。`now` 是保留字不可當 context key。
DataTable 中被 `"` 包住的 `"$var"` 視為純字串、不解析。

### CAS — Then 斷言用

只關心條件不關心定值時用 CAS（跨環境穩定）。全部約束：

| 類別 | 約束 |
|------|------|
| 型別檢查 | `&isNum` `&isStr` `&isBool` `&isNull` `&isNotNull` |
| 數值比較 | `&eq(v)` `&ne(v)` `&gt(v)` `&lt(v)` `&ge(v)` `&le(v)` |
| 字串操作 | `&contains(s)` `&startsWith(s)` `&endsWith(s)` `&matches(regex)` `&length(min,max)` |
| 陣列操作 | `&hasItem(x)` `&hasNoItem(x)` `&size(n)` `&isEmpty` `&isNotEmpty` |
| 存在性 | `&hasField(f)` `&noField(f)` |
| 範圍 | `&between(min,max)` `&notBetween(min,max)` `&oneOf(a,b,…)` `&noneOf(a,b,…)` |
| 時間 | `&sameTime(dt)` `&before(dt)` `&after(dt)` `&sameDay(d)` `&timeRange(start,end)` `&withinDays(n)` |

時間約束參數支援 `now` 與相對語法（s/m/h/d 小寫、M 大寫月），以 TimeControl 的 MockTime 為基準。
多約束空格分隔為 AND：`&isNum &gt(0) &lt(100) &ne(50)`。參數可引用變數：`&eq($expected)` `&between($min,$max)`。
CAS 不可與 `>contextKey` 同欄混用。

### TIME — 時間欄位

絕對 `@time("2025-12-25T14:30:00")` / `@date("2000-01-15")`；相對以 TimeControl 的 MockTime 為基準
`@time("now+7d")`，單位 s/m/h/d 小寫、M 大寫（月）。

## Good

```yaml
# When「買家下單」：引用前面捕獲的買家 id 當 UID，製造 orderId 供 Then 引用
- instruction: '(UID="${{buyerAlias}}.id") 建立訂單, call table:'
  table:
    '>LastOrder.id': '<orderId'
    'items[0].productId': '${{productAlias}}.id'
    'items[0].quantity': '{{qty}}'
- instruction: '建立訂單(201)回應, with table:'
  table:
    status: '{{expectedStatus}}'
    totalAmount: '&gt(0)'        # 只在意「有金額」用 CAS
```

## Bad

```yaml
- instruction: '(UID="u_12345") 建立訂單, call table:'   # 寫死真實 id，換環境就壞
  table:
    productId: 7                  # 應為 ${{productAlias}}.id 引用
    totalAmount: 999              # Then 關心「有金額」卻比對定值，脆弱；應 &gt(0)
    createdAt: "2026-01-27..."    # 時間寫死；應 @time/ &sameTime("now")
```
