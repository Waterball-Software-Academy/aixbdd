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
   其中**外部資源／外部依賴語意**（快取、外部 API stub、MQ、外部儲存等）不得直接自創句式：
   先查主 SOP step 4 載入的 dependency registry——
   - 有對應 entry → custom 契約依 entry.kind 的 kind-constants 句式模版填空
     （見 custom-isa-placement.md「外部依賴 custom」節）；
   - 無對應 entry（或無 registry）→ 缺上游真相，不得憑空發明契約，依 [DISCUSS]
     帶完整 Example 澄清並指回 `/aibdd-dependency-plan` 先盤點登記。

判 custom 前先過 [builtin-composition-patterns.md](builtin-composition-patterns.md)：
一句常拆多條有序 isa_step，有模式可組合表達的不做 custom。

選定型別後怎麼填：各型用法、填 table 慣例（data_format、NOT NULL 預設）與能力界限見
[builtin-instruction-usage.md](builtin-instruction-usage.md)；符號語法見
[symbol-system-usage.md](symbol-system-usage.md)。本檔只管選型。
