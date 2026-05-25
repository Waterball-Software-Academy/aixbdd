針對單一 `.feature` 做 canonical exemplar instantiation。

# Task

1. READ 當前 `.feature` 全文。

2. ASSUME 本 step 由單 feature worker 執行：
   1. 一個 worker 只處理一個 `.feature`。
   2. worker 只負責 canonical exemplar instantiation，不負責新的 discovery、handler 搜尋、DSL arrangement 或 coverage expansion。

3. INVENTORY 本 `.feature` 內所有尚未落地的 placeholder：
   1. `Rule:` headline、`Example:` / `Scenario Outline:` 標題中的 placeholder。
   2. `Given` / `When` / `Then` / `And` / `But` step 文字中的 placeholder。
   3. DataTable、DocString 與 assertion payload 中的 placeholder。
   4. `<>` 與 `{}` 兩種 placeholder 都要一起盤點；不得只處理其中一種。
   - 請注意！此步驟不像 `03-dsl-arrangement` 的 scope 誤縮只有 `Given` / `Then`，本步驟不只是包含 Given, Then， scope 也明確包含 `When` 的區塊。
   5. `$alias`（例如 `$orderId`、`$paymentId`、`$shipmentId`）不是未落地 placeholder。它是合法最終 artifact 形態，代表 scenario-local runtime handle：值由前序 step 在 runtime 產生，寫入 scenario context，供後續 step 引用。
   6. 盤點時必須把 token 分成兩類：
      1. 仍待本 phase 實例化的 `{...}` / `<...>`。
      2. 已屬最終形態、不得被 concretize 的 `$alias`。

4. DERIVE feature-level canonical binding map：
   1. 先從當前 `.feature` 內已存在的 concrete literals、actor 關係、resource 關係與前序 step 因果，推出哪些 placeholder 應沿用既有值。
   2. 若同一個語意 placeholder 在同一個 `.feature` 內重複出現，優先綁成同一個 concrete exemplar。
   3. 若某 placeholder 尚無既有來源，為它選一個低認知成本、可直接閱讀的 canonical exemplar；此 exemplar 只需支撐當前 scenario，不得藉機擴 coverage。
   4. 若某 `Scenario Outline` 目前只是 skeleton，且尚未承載多組變化，為它落一組 canonical exemplar 即可；不得在此步擴成多組 examples。
   5. 若某值不是 scenario 開始前已知，而是需由前序 step 執行後才會得到（例如 API response id、DB-generated primary key、payment token、timestamp、outbox id），不得把它綁成 concrete exemplar；應改綁成 `$alias`。
   6. `$alias` 一律採 `$camelCase` 命名，依領域語意取名，例如 `$orderId`、`$paymentId`、`$shipmentId`、`$refundId`；不得混用 `$order-id`、`${orderId}`、`$current_order_id` 等多套風格。
   7. 若同一個 runtime value 在同一個 `.feature` 內重複出現，必須沿用同一個 `$alias`；不得前面叫 `$orderId`、後面改叫 `$currentOrder`。

5. INSTANTIATE 當前 `.feature`：
   1. 將步驟 4 得到的 binding map 回寫到 title、steps、tables 與 assertion payload。
   2. 對每一個 token，先決定它屬於哪一類：
      1. static known value → 落成 concrete exemplar。
      2. runtime-produced value → 落成 `$alias`。
   3. 若 concrete exemplar 代表字串參數，落地時一律 resolve 成 Gherkin 內可直接閱讀的 `"..."`；若 concrete exemplar 代表整數參數，優先直接落成裸值，不必額外補引號。
   4. `$alias` 受制於變數格式。它不是 concrete literal，但在 Gherkin artifact 中的外觀仍必須跟隨該參數 slot 的型別：
      1. string slot → `"$orderId"`、`"$paymentId"` 這類帶雙引號寫法。
      2. integer slot → `$retryCount`、`$itemCount` 這類裸 token 寫法。
   5. 若某 step definition 內部需要真正的字串 / 整數值，應先依 slot 型別 parse 外觀，再 resolve `$alias` 成 scenario context 中的 runtime value。
   6. 若某 step 使用 Gherkin DataTable，第一列必須是欄位名稱 header row，第二列開始才是 data row；不得把欄位名和值攤成同一列，也不得改寫成 column-oriented 的 key/value 形狀。
   7. 例：
      1. `Given 使用者以識別碼 "{識別碼}" 查詢資源` 應落成 `Given 使用者以識別碼 "item-123" 查詢資源`。
      2. `And 系統以權杖 "{權杖}" 存取租戶 "{租戶編號}" 並限制為 {上限值} 筆` 應落成 `And 系統以權杖 "credential-abc" 存取租戶 "tenant-01" 並限制為 10 筆`。
      3. `When 顧客以訂單 "{訂單編號}" 申請退款` 應落成 `When 顧客以訂單 "order-123" 申請退款`。
      4. `Then 操作失敗，錯誤為 "{錯誤訊息}"` 應落成 `Then 操作失敗，錯誤為 "訂單不存在"`。
      5. 若前序 step 會在 runtime 產生訂單編號，而這個 slot 是 string slot，後續 consumer step 應落成 `When 顧客查詢訂單 "$orderId"`，不得落成 `When 顧客查詢訂單 "order-id-xyz"` 這種偽 static literal。
      6. 若前序 step 會在 runtime 產生重試次數，而這個 slot 是 integer slot，後續 consumer step 應落成 `Then 付款重試次數應為 $retryCount`，不得落成 `Then 付款重試次數應為 "3"`。
      7. `And 統計結果應如預期：` 加上 data table
         ```
         | 類別 | 項目數 |
         | "{類別}" | {項目數} |
         ```
         應落成
         ```
         | 類別 | 項目數 |
         | "standard" | 2 |
         ```
      8. 若 table cell 指向 runtime-produced value，必須同樣遵守欄位型別。string cell 用 `"$alias"`，integer cell 用裸 `$alias`。例如
         ```
         | 訂單編號 | 狀態   |
         | "$orderId" | "paid" |
         ```
      9. 不得把上例落成
         ```
         | 類別 | "standard" | 項目數 | 2 |
         ```
         這種把欄位名和值攤在同一列的 form。
      10. 若 header row 某欄對應整數 exemplar，不得把 data row 寫成 `"2"` 這類字串字面值；應直接落成 `2`。
   8. 保留 scenario 的原本 intent、assertion shape 與 actor/resource handoff，不得因為換值而改變此 scenario 想證明的事。
   9. 保留 producer / consumer 關係。若前序 step 會產生後續要引用的 runtime value，artifact 必須用 `$alias` 承接，不得把該值偽裝成固定 literal。
   10. 若某 `Scenario Outline` 在 instantiation 後不再需要多組 placeholders，可正規化成單一 `Example`，只保留當前這組 exemplar。
   11. 同一個 `.feature` 內的 naming 要前後一致，避免 `訂單編號`、`訂單號碼`、`付款單編號` 各自掉成不同世界觀。
   12. 完成前必須逐條自檢：凡 `Given` / `When` / `Then` / `And` / `But` 行內原先承載 DSL 參數者，都不得殘留 `{...}` 或 `<...>` 形式的未綁定 placeholder；若仍有殘留，視為本 phase 尚未完成。`$alias` 不算未綁定 placeholder。
   13. 完整電商例子（producer / consumer + static literal + runtime handle 並存）：
      1. 合法成品：
         ```gherkin
         Rule: 後置（狀態） - 付款完成後訂單應標記為已付款
             Example: 顧客完成付款後訂單狀態更新
               Given 顧客 "alice" 建立購物車，並記住購物車編號為 "$cartId"
               And 顧客 "alice" 在購物車 "$cartId" 加入商品 "sku-iphone-15"
               And 顧客 "alice" 送出購物車 "$cartId" 建立訂單，並記住訂單編號為 "$orderId"
               And 金流服務為訂單 "$orderId" 建立付款單，並記住付款單編號為 "$paymentId"
               When 顧客 "alice" 支付付款單 "$paymentId"
               Then 操作成功
               And 驗證 orders 狀態 "$orderId"
                 | 狀態   |
                 | "paid" |
               And 驗證 payments 狀態 "$paymentId"
                 | 狀態        |
                 | "succeeded" |
         ```
      2. 在這個例子裡：
         1. `"alice"`、`"sku-iphone-15"`、`"paid"`、`"succeeded"` 是 static literal，可直接 concretize。
         2. `$cartId`、`$orderId`、`$paymentId` 是 runtime handle，值由前序 step 產生並在 scenario context 中流動。由於它們在這個例子裡佔的是 string slot，所以 artifact 外觀必須寫成 `"$cartId"`、`"$orderId"`、`"$paymentId"`，不得在本 phase 被改寫成 `"cart-123"`、`"order-456"`、`"payment-789"` 之類的假固定值。

6. 若有任一 placeholder 在不改變 spec meaning 的前提下仍無法唯一決定：
   1. 組成 `$NEED_TO_CLARIFY`。
   2. STOP 本 worker。
   3. 交回外層 phase 走 `/clarify-loop`，不得自行發明值。
   4. 若你無法判定某欄位應該是 static known value 還是 runtime-produced value，也視為無法唯一決定；此時必須提問，不得直接把它 concretize 成看似合理的假 id。

7. `$NEED_TO_CLARIFY` += DO FAITHFUL REASONING 針對當前 `.feature` 範疇內所有已落地的 `Example` / `Scenario Outline`，依照 `derive-findings.md` 中的分析切角去進行深度分析，並找到所有需要澄清的地方。

8. 若 `$NEED_TO_CLARIFY` 非空：EMIT 給外層 phase；外層 phase 負責 DELEGATE `/clarify-loop` skill 以單次最多五題的方式來進行提問。

# Worker hard limits
1. 不得變更 `When` step 的行為意圖；若 `When` 內含 placeholder，只能把它落成 concrete exemplar 或符合 slot 型別格式的 `$alias`，不得改寫該操作想表達的業務語意。
2. 不得新增新的 Scenario、不得新增新的 Examples rows。
3. 不得改寫 scope 外的 `.feature`，也不得回頭改寫 `01`、`02`、`03` 已接受的決策。
4. 不得把同一個 `.feature` 內已存在的 concrete 值或 `$alias` 重新發明成另一套 naming；同一語意 token 應盡量落成同一組值 / 同一個 handle。
5. 字串 exemplar 不得去掉引號；凡屬 static string literal，落地時必須保留 `"..."` 形式。
6. 整數 exemplar 不得包成字串；凡屬 static integer literal，落地時不得寫成 `"2"`、`"10"` 這類字串字面值。
7. string slot 中的 `$alias` 必須加雙引號，例如 `"$orderId"`；integer slot 中的 `$alias` 必須保持裸 token，例如 `$retryCount`。
8. 不得把 runtime-produced value 偽裝成 concrete exemplar；例如前序 step 才會得到的 id / token / timestamp，不得硬落成 `"order-id-xyz"`、`"payment-token-abc"` 之類的假固定值。
9. 若某 placeholder 的值無法在不改變 spec meaning 的前提下唯一決定，必須 EMIT `$NEED_TO_CLARIFY` 並提議最根本的解法；不得硬猜。
10. 若 `$NEED_TO_CLARIFY` 非空，本 worker 不做使用者互動、不宣告完成，也不做最終寫回。

# Completion contract
1. 每個 `.feature` 完成後，該檔內所有尚未落地的 placeholder 都應已被 instantiation 成最終 artifact 形態：static known value 變成 concrete exemplar，runtime-produced value 變成 `$alias`。`{...}` 與 `<...>` 不得殘留；`$alias` 合法保留。
2. 若某 `Scenario Outline` 在 instantiation 後只剩單一 exemplar，且不再承載多組變化，可被正規化為單一 `Example`。
3. 同一個 `.feature` 內相同 actor、resource、identifier、runtime handle 與 expected value 的 naming 應保持一致，讓讀者能直接看出誰生出誰、誰沿用誰。
4. 本步完成後的 feature files 應可直接銜接 `/aibdd-tasks`；若要再做 coverage 擴寫、EP / BVA 或額外 examples，屬於 optional enhancement，不屬本 phase。
5. 若 `$NEED_TO_CLARIFY` 非空，worker 回傳 incomplete；外層 phase 完成 clarify 後才可重跑本 worker。
