重複底下這個迴圈，直到拿到合法紅燈或必須停止為止，最多 5 次：
   1. 用 `ACCEPTANCE_RUNNER_RUNTIME_REF` 的 dry-run／discovery 指令，先確認可見性。
   2. 確認這次可見性掃到了  target feature 與 Scenario；掃不到就停下來，請對方去檢查專案的 BDD stack 設定。
   3. 對歸檔後的 feature 跑一次正式的 acceptance runner，拿到 behavior report。
   4. 把 behavior report 裡的「第一個失敗」拿去分類（依 `references/legal-red-classification.md`）。
   5. 依分類結果決定下一步：
      1. `value_difference`：這是合法紅燈，結束迴圈。
      2. `expected_exception`：這也是合法紅燈，結束迴圈。
      3. `false_red_repairable`（可修補的假紅燈）：回到步驟 (8) 重新實作 step definition 後，再回到本階段重跑。
      4. `unknown`（無法分類）：停下來，回報 `stop_reason: unclassified_red_failure`。
   6. 確認最後真的拿到了合法紅燈；如果 5 次都用完還沒拿到，就停下來，回報 `stop_reason: red_loop_budget_exceeded`。