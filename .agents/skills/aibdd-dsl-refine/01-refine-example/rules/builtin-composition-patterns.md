# 內建指令拆解模式

一句業務語句常拆成多條有序 isa_step。判 custom 前必須先過這裡：**能套用下列模式組合表達的，
一律不做 custom**；全部套不上、且落在 [builtin-instruction-usage.md](builtin-instruction-usage.md)
界限總表內，才依 [custom-isa-placement.md](custom-isa-placement.md) 宣告 custom。
符號語法見 [symbol-system-usage.md](symbol-system-usage.md)。

## 基本骨幹（每個 When 的預設拆法）

`When 動作` ＝ `api_call` ＋ `response_validate`（＋ 資料落地時 `entity_validate`）。
API 回 2xx 不等於資料寫對——Then 關心落地就補 entity_validate，不要只驗回應。

## 模式表（語意 → 組合）

| # | 語意 | 拆法 |
|---|------|------|
| P1 | 關聯資料前置（FK） | entity_setup 父表擷取 `>{{alias}}.id` → 子表 setup 以 `${{alias}}.id` 填 FK |
| P2 | 關聯存在驗證 | 兩條 entity_validate：from 端、to 端各自存在（FK 欄位以 `$var` 對上） |
| P3 | 跨表值一致 | 第一條 entity_validate 用 `>`/`<` 從表 A 擷取實際值 → 第二條對表 B 以 `&eq($x)` 比對 |
| P4 | 回應值鏈到下一步（取 id 再查） | api_call 擷取 `>order.id`/`<orderId` → 後續 api_call／entity_validate 以 `$order.id` 引用 |
| P5 | 多使用者交錯操作 | 各 api_call 各自 `UID="$alias.id"`（token 每次重解析，無需額外處理） |
| P6 | 冪等重送 | 同一 api_call 寫兩次，各自接 response_validate（回應槽逐次覆寫） |
| P7 | 分頁 | api_call 帶 `Q:page`/`Q:pageSize` → response_validate 驗陣列（索引定址＋`&size(n)`） |
| P8 | 不存在（count=0） | entity_non_existence_validate（只放等值條件欄位） |
| P9 | 恰好一筆（count=1） | entity_validate 一列——「恰好一筆」是內建語意（0 或 >1 都 fail），免費取得 |
| P10 | 已知 N 筆存在 | entity_validate N 列，每列以欄位組合唯一定位；注意這只證下界（見禁區） |
| P11 | 最新一筆 | 前提：time_control 固定時間、測試自造資料 → 時間欄位值確定，退化為等值定位（P9） |
| P12 | 版本遞增／樂觀鎖 | 前一步擷取 `$oldVersion` → 之後 entity_validate 以 `&gt($oldVersion)` 斷言 |
| P13 | 有限值域的否定不存在 | 對每個不允許的值各一條 entity_non_existence_validate 等值枚舉 |
| P14 | 多步前置流程 | 依序多條 entity_setup（或 api_call 串 P4）鋪狀態；跨 4 表以上或句意為單一配置概念 → 必走 custom（見上限，硬界限） |

## 拆解原則

- 先拆再判：一句 dsl_step 先嘗試以上模式組合；`isa_steps` 本來就是有序多條，拆多條不是失敗。
- 每條 isa_step 必對上 isa.yml 既有 format；拆出來的每一條各自過
  [builtin-instruction-decision-tree.md](builtin-instruction-decision-tree.md) 選型。
- 資料流靠 VAR 串：跨 step 傳值一律 `>`/`<` 擷取＋`$var` 引用，不寫死環境值。
- 唯一定位紀律：entity_validate 每列要能唯一定位（PK 或等值欄位組合）；
  測試資料由 entity_setup 自造，設計時就讓每筆可唯一識別。

## 拆解上限（拆到什麼程度該停）

- 模式內的拆解（P1–P13）不設條數上限——這些是資料流必要步驟，不算過度複雜。
- 多步前置（P14）**硬界限**：跨 4 表以上、或句意是單一 reference data／配置概念
  （例：評分規則配置——選項分數字典＋級距＋審核門檻＋職稱層級；跨多表的申請單含逐關審核紀錄）
  → **必走 custom**（契約宣告見 custom-isa-placement.md）；custom 的 intent 必須寫得出
  「一句 WHAT」，寫不出來代表不該封裝、回頭拆。
  【嚴禁】為了留在 builtin 而縮水句意（少鋪真相蘊含的表）——該句涵蓋幾張表，
  以 DDL／spec 真相判定，不以「目前情境剛好只用到幾張」判定。
- 未達硬界限、但拆到**讀者無法一眼看出「這串 setup 在鋪什麼狀態」**→ 封裝與否為
  可讀性決策，須經 `/clarify-loop` 確認，不是 AI 單方判定。

## 禁區（不可硬拆，直接走 custom 判定）

以下語意沒有組合拆法，硬拆會做出「看似驗了、實際沒驗」的假斷言：

- 精確筆數 N≥2：P10 只證「至少 N 筆」，不能宣稱「恰好 N 筆」；需要恰好 N 時是界限外。
- 聚合值（SUM/AVG/COUNT 比對）：逐筆驗明細＋驗冗餘欄位（如 order.total）是替代設計，
  但「斷言聚合結果」本身界限外。
- 排序斷言：P11 的前提（time_control＋自造資料）不成立時，「最新一筆」界限外。
- 開放值域的否定不存在：P13 只適用有限枚舉。
- 非 JSON 載體（multipart／binary／text 內容）：見 usage 界限總表。

## Good

```yaml
# P4＋P9：下單後取 id 驗落地——一句「下單成功」拆三條
- name: 下單成功
  format: '{buyer} 下單 {qty} 件 {product}'
  isa_steps:
    - instruction: '(UID="${{buyer}}.id") 建立訂單, call table:'
      table:
        '>LastOrder.id': '<orderId'
        'items[0].productId': '${{product}}.id'
        'items[0].quantity': '{{qty}}'
    - instruction: '建立訂單(201)回應, with table:'
      table:
        totalAmount: '&gt(0)'
    - instruction: '應該存在一個訂單, with table:'
      table:
        訂單id: '$LastOrder.id'
        狀態: 'PENDING'
```

## Bad

```yaml
# 有模式可拆卻包 custom（P1 兩條 entity_setup 就能表達）
- name: 建立帶角色的使用者
  format: ^建立帶角色的使用者$
  instruction_type: custom        # ✗ 應拆 entity_setup(使用者)＋entity_setup(使用者角色)
```
```yaml
# 硬拆禁區語意做假斷言：想驗「恰好 2 筆」卻只列 2 列（實際只證下界）
- instruction: '應該存在一個權限關聯, with table:'   # ✗ 第 3 筆多出來也不會 fail
  table: { 角色id: '$r.id', 權限: 'READ' }
- instruction: '應該存在一個權限關聯, with table:'
  table: { 角色id: '$r.id', 權限: 'WRITE' }
```
