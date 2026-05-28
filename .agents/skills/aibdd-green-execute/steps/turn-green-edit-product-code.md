# SOP

重複底下這個迴圈，直到所有 target feature 轉綠或必須停止為止，最多 5 次：

1. 用 `${ACCEPTANCE_RUNNER_RUNTIME_REF}` 對這組 target feature 跑一次 acceptance runner，拿到最新 behavior report。
2. report 結果是 `passed`：所有 target 轉綠，結束迴圈。
   - 例外：若這是第一圈、且一進來就已經全綠（還沒改任何產品碼就全過），停下來，回報 `stop_reason: red_invalid_already_green`。
3. 依 `../references/green-oscillation-detection.md`，從 report 算出一個穩定的「第一個失敗」簽章，記進 loop 紀錄；偵測 loop 紀錄裡有沒有「兩個簽章嚴格來回擺盪」（預設門檻 3）。一旦偵測到擺盪，停下來，回報 `stop_reason: oscillation_detected`。
4. 把這個「第一個失敗」分類（依 `../references/legal-red-classification.md` 與失敗性質），依分類決定下一步：
   1. 產品缺口（合法紅燈：`value_difference`／`expected_exception`／`product_gap`）：往下做，這是 green 該修的。
   2. 測試 bug（`test_bug`／可修補的假紅燈）：停下來，請對方回到 `/aibdd-red-execute`。
   3. runtime 飄移（`runtime_drift`）：停下來，請對方去檢查專案的 BDD stack 設定。
   4. 架構否決（`architecture_veto`）：停下來，回報 `stop_reason: architecture_veto`。
5. 只針對這個「第一個失敗」改產品程式碼，且只寫剛好讓它通過的最小改動；把這次改到的產品檔記進「動過的產品檔」集合。

迴圈結束後：確認最新 report 是 `passed`；如果 5 次都用完還沒全綠，就停下來，回報 `stop_reason: loop_budget_exceeded`。
