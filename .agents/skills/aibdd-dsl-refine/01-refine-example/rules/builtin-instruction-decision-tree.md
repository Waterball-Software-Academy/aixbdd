# 內建指令決策樹

把一條 dsl_step 展開成有序 isa_steps 時，每條 isa_step 先判斷能否用內建指令完成。
一句業務語句常展開成多條 isa_step（例：When「下單」= api_call + response_validate + entity_validate）。
指令 format 與型別一律以專案 `specs/isa.yml`（及各 package `*.isa.yml`）實際定義為準；
本樹只給「該 isa_step 該選哪個內建型別」的選法，不把任何模版 format 當死。

## 六個內建型別（GWT 角色 → 型別）

| GWT | 意圖 | instruction_type | 句型骨幹 |
|-----|------|------------------|----------|
| Given | 設定模擬時間 | `time_control` | 現在時間為 "…" |
| Given | 準備前置資料（寫 DB） | `entity_setup` | 準備一個{entity}, with table:/json: |
| When | 觸發系統操作（呼叫 API） | `api_call` | (UID="$…"/No Actor) {summary}, call table:/JSON: |
| Then | 驗 API 回應（狀態碼＋回傳值） | `response_validate` | {summary}({code})回應, with table:/JSON: |
| Then | 驗 DB 落地（記錄存在＋欄位正確） | `entity_validate` | 應該存在一個{entity}, with table:/json: |
| Then | 驗 DB 不存在（刪除後） | `entity_non_existence_validate` | 應該不存在一個{entity}, with table: |

## 決策流程（per isa_step）

1. 設定時間 → `time_control`。
2. 在系統操作前先把狀態寫進 DB（前置資料）→ `entity_setup`。
3. 觸發一次系統行為、且是 HTTP API → `api_call`（summary 對應 contracts 的 operation summary；
   `UID="$alias.id"` 帶呼叫者身分，無身分用 `No Actor`）。
4. 驗證：
   - 只驗 API 回應（狀態碼／回傳 body）→ `response_validate`（狀態碼寫進句子 `(201)`）。
   - 要確認資料真的落地（API 回 200 不等於有寫進去）→ `entity_validate`。
   - 要確認記錄已被刪除／不存在 → `entity_non_existence_validate`。
5. 以上皆不符（外部資源 mock、非 HTTP 操作、把多步前置語意封裝成一句）→ 不是內建，
   走 custom，見 [custom-isa-placement.md](custom-isa-placement.md)。

## 慣例（忠實對應，填 table 時遵守）

- data_format：扁平欄位用 `table`；巢狀／貼近 request body 用 `json`。輸出 DataTable 或 DocString
  由該 instruction 在 isa.yml 的 `data_format` 決定，不可自選。
- entity 三型（setup / validate / non_existence）：entity 名經 `entity_to_table_mapping.yml` 對到實體表，
  欄位對 DDL；查詢優先用 PK，否則用非 PK 欄位組合 probe。
- `entity_non_existence_validate` 不支援 CAS（`&…`）、VAR 擷取鍵（`>`）、回應來源（`<`）——只放查詢條件欄位。
- api_call 欄位前綴：無前綴＝Request Body（同名自動帶入 Path/Query/Header）；`P:`/`Q:`/`H:` 指定位置；
  `B:` 整包 body；`>`/`<` 擷取回應、`<H:` 擷取回應 header、`<B:` 擷取裸值 body。
- response_validate：欄位值可用 CAS 做條件斷言；要擷取回應供後續引用用 `>`/`<`。

## DataTable 完整性（NOT NULL 預設值）

`entity_setup` 與 `api_call` 寫入的 table，必須讓 NOT NULL／required 欄位都有值，否則違反 DB 約束或 API 回 400：

- NOT NULL 來源：`entity_setup` 看 data DDL（經 entity_to_table_mapping 對表）；`api_call` 看 contracts 的 required。
- 欄位與「當前測試情境」相關（被 Then 斷言、或驅動本例行為）→ 帶真實資料：`{{name}}`／`$alias`／業務值。
- 欄位 NOT NULL 但與當前情境無關 → 填合理預設值（集中放 dsl_step 的 `params`，table 用 `{{name}}` 取），
  別留空、也別硬塞會誤導讀者的值。

## Good

```yaml
# entity_setup：status NOT NULL 但本例不驗它 → 預設 ACTIVE（放 params）；name 是情境主角 → 帶值
- instruction: '準備一個使用者, with table:'
  table:
    '>{{alias}}.id': '<userId'
    name: '{{alias}}'
    email: '{{alias}}@example.com'
    status: '{{defaultStatus}}'      # params.defaultStatus: ACTIVE
# Then 確認落地，不只看 API 回應
- instruction: '應該存在一個訂單, with table:'
  table:
    訂單id: '$order.id'
    狀態: '{{expectedStatus}}'
```

## Bad

```yaml
# 漏填 NOT NULL 的 status → 寫入違反約束 / 測試非預期失敗
- instruction: '準備一個使用者, with table:'
  table:
    name: '{{alias}}'
# 只驗 API 回應就當作資料寫成功（少了 entity_validate）；刪除案例卻用 entity_validate 而非 non_existence
- instruction: '應該存在一個待辦事項, with table:'   # 刪除後應改用「應該不存在一個…」
  table:
    todoId: '$todo1.id'
```
