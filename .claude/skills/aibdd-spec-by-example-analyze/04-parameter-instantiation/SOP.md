# SOP

上一步已完成 DSL arrangement。

本步針對每個 impacted `.feature` 做 canonical exemplar instantiation：把尚未落地的 placeholder 全部實例化成一版可讀、可跑、可 review 的具體情境；此步不做 coverage enhancement，完成後即可直接銜接 `/aibdd-tasks`。

注意：本 phase 的 instantiation scope 不是只有 `Given` / `Then`。凡是當前 `.feature` 內尚未落地的 placeholder，包含 `Rule` / `Example` / `Scenario Outline` 標題、`Given` / `When` / `Then` / `And` / `But` step 文字、DataTable、DocString 與 assertion payload，全部都要一併實例化。

1. USE `${SCOPED_FEATURE_PATHS}` as bound impacted feature file scope。
   1. `${SCOPED_FEATURE_PATHS}` 由頂層 SOP 步驟 1 綁定。
   2. 若 `${SCOPED_FEATURE_PATHS}` 為空 → STOP 並報錯。

2. [LOOP] FOR EACH `${SCOPED_FEATURE_PATHS}` 內每個 `.feature`：
   1. READ 該 `.feature` 全文。
   2. TRIGGER 一個 canonical exemplar instantiation worker（可用 sub-agent；粒度固定為一個 feature 一個 worker），此 worker 將嚴格執行：`steps/parameter-instantiation.md`
   3. worker 成功完成時的唯一授權 side effect：原地改寫當前 `.feature` 內尚未落地的 placeholder。
   4. worker 完成前必須自檢：`Given` / `When` / `Then` / `And` / `But` 與其附屬 table / payload 內，不得殘留任何未落地 placeholder。
   5. worker 若回傳 `$NEED_TO_CLARIFY`，視為該 `.feature` 尚未完成；外層 phase 不得採納該 worker 的完成宣告。

3. WAIT 所有 feature workers 完成。
   1. COLLECT 全部 worker 回傳的 `$NEED_TO_CLARIFY`。
   2. 若 `$NEED_TO_CLARIFY` 為空：本 phase 完成。
   3. 若 `$NEED_TO_CLARIFY` 非空：依 feature 維度 merge / dedupe，整理成批次 clarify payload，DELEGATE `/clarify-loop`。
   4. WAIT clarify 結果，然後只重新跑受影響的 feature worker。
   5. 回到步驟 3.1，直到 `$NEED_TO_CLARIFY` 為空才可離開本 phase。
