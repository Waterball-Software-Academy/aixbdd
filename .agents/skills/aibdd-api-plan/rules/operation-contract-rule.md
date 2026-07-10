# operation contract 約束

operation contract 產出須滿足下列約束與驗收標準。

## 約束

1. 切檔視角須反映使用者要驗收的介面視角
   1. 同一批 feature truth 可支撐多種切法（resource-oriented／workflow-oriented／actor-oriented 等）時，採用的視角須有使用者依據，不得由 planner 任選其一鎖定。
   2. 例：同一批需求既可切成 `orders.api.yml`、`payments.api.yml`，也可切成 `checkout.api.yml`。

2. 多套等效設計時須採使用者偏好的優先序
   1. 從 lifecycle、actor handoff、external dependency、auditability 等不同角度都能覆蓋現有需求的設計並存時，採用的設計須符合使用者偏好。

3. domain 歸屬須清楚
   1. 只有對外互動承諾屬 operation contract；執行後須穩定保存的系統狀態不屬本 domain。
   2. 每個需求面向的 operation／state 歸屬須明確，不得混置。
   3. 例：建立訂單成功後的「確認訊息」是 response contract 保證還是 notification state 變化，須有明確歸屬。

4. 本輪範疇須有依據
   1. 納入本輪的 target 須有明確範疇依據；是否納入仍取決於尚未拍板的需求決策者，不算有依據。
   2. 例：是否把促銷套用 API 寫成正式 contract，取決於這輪是否真的支援促銷規則。

5. 需求列舉須逐項納入
   1. 需求上下文內的對外回傳欄位、請求參數、狀態等列舉，須逐項納入契約，不得概括。
   2. 例：需求逐列列出回應要帶的 5 個欄位，contract 不得只寫「回傳訂單資訊」一句帶過。

6. target_path 須合法
   1. `target_path` 為相對 `${CONTRACTS_DIR}` 的 flat 檔案路徑，不得含 `<<NN-functional-module>>` 借位子層、不得與其他 target 重複，路徑語意依 `aibdd-core::references/ssot/spec-package-paths.md`。
   2. OpenAPI 檔副檔名一律 `*.api.yml`，例：單檔 `main.api.yml`、per-resource `<resource>.api.yml`。

7. target 與 pending impact 須雙向對映
   1. 每個 target 須指回驅動它的 pending impact。
   2. 每個 pending impact 的對外互動承諾須有 target 承接。

8. target 不得超出本輪授權範疇
   1. 每個 target 須落在本輪 plan scope 與 pending impact 授權的範圍內。
   2. 例：本輪只涵蓋 checkout package，不得把 account profile 的 contract target 一起切進來。

9. contract 須忠實反映 Discovery 真相
   1. 導出的 operation contract 不得背離 spec.md、feature truth 與 activity truth 明示的行為與結果。
   2. 例：feature truth 是「取消訂單」，不得只導出查詢訂單狀態的 operation。

10. 不得重複拆分
    1. 可由單一 operation contract 表達的能力，不得拆成多個只差細節的重複 target。
    2. 例：同一個查詢能力不得拆成三份只差欄位的 contract 檔。
