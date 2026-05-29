# Example residual finding 分析切角

1. 目的
   1. 本檔只列出在 `04-parameter-instantiation` 中，對當前 `.feature` 內所有已落地 `Example` / `Scenario Outline` 成品做整體 residual audit 時，可能需要進一步澄清的分析切角。
   2. 本檔只產出 `$NEED_TO_CLARIFY`；不在此步驟內做寫檔修正。
   3. `$NEED_TO_CLARIFY` 必須是 cross-example、feature-level 的題目，不得退化成逐 placeholder 的零碎提問。
   4. `$NEED_TO_CLARIFY` 依 downstream impact 排序後，最多保留 5 題交給外層 `/clarify-loop`。

## $NEED_TO_CLARIFY
1. static exemplar 與 runtime handle 邊界不清
   1. 要看什麼：同一語意 token 橫跨多個 examples 時，是否無法唯一判定該值應落成 concrete exemplar，還是應保留為 `$alias`。
   2. 需求訪談重點：要確認該值在 scenario 語意中是事前已知、由使用者明確提供，還是執行後才產生的 runtime value。
   3. 例：某些 examples 把訂單編號落成 `"order-123"`，另一些 examples 則寫成 `"$orderId"`，但上游規格不足以判定哪種才是正確形態。
2. cross-example naming policy 不明
   1. 要看什麼：同一 actor、resource、identifier、error label 或 runtime handle 在不同 examples 間是否存在兩種以上都合理的命名方案。
   2. 需求訪談重點：要確認整個 feature 應採用哪一套 canonical naming，避免 reviewer 讀到像是不同世界觀。
   3. 例：同一 feature 有的 example 用 `訂單編號`，有的用 `訂單號碼`；有的用 `$paymentId`，有的用 `$currentPaymentId`。
3. assertion 視角不確定
   1. 要看什麼：當前 examples 合起來看，是否無法唯一判定驗證焦點應落在 response、state、error wording、read model 或其他結果面向。
   2. 需求訪談重點：要確認使用者真正想驗收的是哪個結果面向，避免 examples 各自驗不同東西卻看似都合理。
   3. 例：一組 examples 對付款失敗驗 `錯誤訊息`，另一組則驗 `orders 狀態未改變`，但需求沒有說主驗收焦點是哪一個。
4. examples 之間缺少共享前提
   1. 要看什麼：只有把所有 examples 放在一起看才看得出某個必要前提、共享政策或 producer / consumer handoff 尚未被明說。
   2. 需求訪談重點：要確認哪些前提是整個 feature 共通的真相，哪些則只是單一 example 的局部設定。
   3. 例：所有 examples 都隱含玩家必須先進入房間，但沒有任何地方能判定這是否是 feature 的硬前提。
5. slot type 與 exemplar format 邊界不清
   1. 要看什麼：同一類參數 slot 在不同 examples 間，是否無法唯一判定應落成字串字面值、整數裸值、帶引號 `$alias` 或裸 `$alias`。
   2. 需求訪談重點：要確認該參數在 Gherkin artifact 中的最終外觀與型別語意，避免 step-definition 對 parse 規則無所適從。
   3. 例：重試次數在某些 examples 被寫成 `3`，另一些則寫成 `"3"`，而需求與上游 DSL 都不足以判定應採哪種格式。
6. scenario 邊界與 example 分工不清
   1. 要看什麼：多個 examples 合起來看，是否暴露出 scenario 邊界仍有兩種以上都合理的切法，導致 exemplar policy 無法唯一決定。
   2. 需求訪談重點：要確認哪些變化應留在同一 scenario family，哪些其實應拆成不同驗收情境。
   3. 例：同一 feature 內把「成功建立訂單」與「成功建立訂單並發送通知」都寫成 canonical exemplar，但需求沒說通知是否屬於同一情境的必然結果。
7. error wording precision 不清
   1. 要看什麼：錯誤訊息、提示文字或回應文案在不同 examples 間是否存在精確文案版與語意摘要版兩套都合理的寫法。
   2. 需求訪談重點：要確認此 feature 需要驗收的是精確 wording，還是只需保留語意級別的錯誤類型。
   3. 例：某些 examples 寫 `Then 操作失敗，錯誤為 "訂單不存在"`，另一些則寫成 `Then 操作失敗，錯誤為 "查無訂單"`。
8. examples 之間存在未拍板的 policy 衝突
   1. 要看什麼：從 ambiguous / gap / violations / brainstorm-different-aspect 四種角度綜合檢查後，是否仍存在一個上層 policy 未拍板，導致多個 examples 的最終長相都可能合法。
   2. 需求訪談重點：要確認真正需要拍板的是哪個上層政策，而不是逐題修補表面 token。
   3. 例：表面上看起來是三個不同 placeholder 問題，但根因其實是「本 feature 對所有 runtime-produced id 是否一律保留成 `$alias`」這個 policy 尚未決定。

---
3. 使用提醒
   1. 一個 finding 可以同時命中多個切角；不要因為它已歸類，就停止從其他角度檢查。
   2. 問題要先做 merge / dedupe，再輸出成 `$NEED_TO_CLARIFY`；同一上層政策只問一次。
   3. `$NEED_TO_CLARIFY` 必須依 downstream impact 由高到低排序，只保留前 5 題；其餘留待 clarify 後重跑再決定。
