# kind: api — truth 取得、testability、entry 填寫規定

適用 SOP step 7 對 kind 為 api 的依賴。entry 樣板：assets/dependencies.template.yml（api 條目）；kind 常數：.claude/skills/aibdd-core/references/kind-constants/api.yml。

## 測試範圍（先於一切）

1. api kind 的測試面為契約測試句式：Given 設定 api 預期回應（stub，含成功／業務結果體，以及
   HTTP 錯誤狀態「回應狀態 N」以模擬外部故障、測 SUT 韌性——外部業務否決如 rejected 用同一 stub 句式
   換回應體、非新句式）、Then 驗證請求正確送達或特定條件下不該發送（互動驗證正反面）；當 feature 明文要驗
   「SUT 送給外部服務的 payload 內容」（如「送簽資料包含下列欄位」）時，Then 用
   payload-bearing 互動驗證變體（應被呼叫並送出, with table:）把送出欄位值以 DataTable 斷言，
   而非退回只驗次數的 count-only。
2. SUT 自身行為的觸發與斷言不在此——那是 builtin api_call／response_validate 的事。
3. 上述 custom step 模版與行為契約屬 kind 級常數，內建於
   .claude/skills/aibdd-core/references/kind-constants/api.yml——registry 不收句式素材，下游依 kind 查表；
   不得為 api 依賴發明 kind-constants 以外的句型。

## truth 取得分流（依序嘗試，取得即停）

1. user-provided：SEARCH `${DEPENDENCIES_DIR}/<name>/` 既有 spec 檔
   （openapi／swagger yml/json）。有則優先採用，`acquisition: user-provided`；
   檔案為唯讀輸入不得改寫，格式非 OpenAPI 者記為 `format` 實值。
2. web-official：SEARCH 該服務的官方開發者文件，取得 OpenAPI 或可轉譯的
   API 說明。`acquisition: web-official`、`origin_url` 必填；官方僅有敘述文件
   （非 OpenAPI）而由本 skill 轉譯者，`evidence: derived`。
3. 皆無：不得憑印象撰寫 API 契約，收進 `$ASK_BATCH` 請使用者提供 spec 或指路。

## testability 與 wiring

1. testability 預設（generic-stub／WireMock 3.x／programmable true）住
   .claude/skills/aibdd-core/references/kind-constants/api.yml，entry 不重抄；僅當偏離預設（如該服務有
   官方模擬器 stripe-mock）才填 entry 的 testability_overrides。
2. `sut_property_overrides` 必填：SUT 指向該服務 base URL 的 config key，
   紅燈前置據此把 SUT 改指 stub。找不到該 key 時收進 `$ASK_BATCH`。

## truth 檔內容（surface 由 truth 檔承載，entry 不抄）

1. user-provided 的 openapi 原檔唯讀整包保留；本批次相關的 operation 由
   feature truth 判定，不另立清單。
2. web-official 轉譯自官方敘述文件時，operations 只收 SUT 會呼叫、且本批次
   feature truth 有出現者，不整包照抄 vendor 文件。
3. 簽章／認證資訊住 truth 檔（openapi security schemes）；簽章算法有獨立
   官方文件時一併取得落於 <name>/ 資料夾。
4. webhook 回打：payload 真相屬本依賴的 truth 檔；callback endpoint 歸
   api-plan 的 contracts 檔，不在此重定義。
