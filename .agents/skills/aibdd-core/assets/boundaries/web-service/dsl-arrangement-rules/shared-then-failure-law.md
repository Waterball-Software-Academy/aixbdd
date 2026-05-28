# Shared Then Law (failure) — web-service

1. 本檔是 web-service boundary 中所有 failure polarity rule 的共用 `Then` legislation SSOT。
2. failure polarity 指的是主操作預期失敗的 rule，包含 `前置（狀態）` 與 `前置（參數）`。
3. 本檔同時承載 failure polarity 下各 rule type 的 `Then Delta` 小節；不得把同一份 delta 再散落回獨立 rule 檔。

## Then Block

### Forces
1. `Then` 的第一個 load-bearing assertion 是主操作失敗，且 failure outcome 必須具體對應當前 atomic rule。
2. 若 form 帶有動態 verifier slot，該 slot 用來證明 failure path 沒有偷偷發生不該發生的 side effect。
3. failure path 的延伸驗證，優先選最小、最直接、最少額外推論的 verifier scope。
4. 不得把 response failure 訊號本身誤當成 no-change 或 no-side-effect 的充分證明。
5. 不得選擇與當前 failure path 無直接關聯的 sibling verifier。

### Legality Gate
1. `Then` 必須先證明主操作失敗，且 failure outcome 必須直接對應被測條件。
2. 若存在動態 verifier slot，所選 verifier 必須直接證明 failure path 未偷偷改變既有 persisted state，或未偷偷產生不該有的 side effect。
3. `Then` 不得為了求方便改用過大的 snapshot assertion。
4. `Then` 不得混入與當前 failure path 無關的 sibling verifier、sibling operation，或其他 broad proxy。

### Output Expectation
1. `Then` 應先保留 form 已凍結的 failure sentence，再安排動態 verifier。
2. rule-type-specific `Then Delta` 只負責補充 failure 類型專屬的 verifier selection、veto 與 trace expectation。

## Rule-Type Then Delta

### 前置（狀態）
1. 若當前 form 還帶有 `state-verifier` slot，該 slot 用來證明 failure path 沒有偷偷改變既有 persisted state。
2. `Then` 驗 unchanged state 時，優先選最小且最直接能證明 no-change 的 verifier scope。
3. 不得把 response failure 訊號誤當成 state unchanged 證明。
4. 不得選擇與當前 failure path 無直接關聯的 sibling verifier，也不得為了求方便改用過大的 snapshot assertion。
5. 若存在動態 verifier slot，應選出最小 no-change verifier，並在 `# @decision:` / `# @rationale:` 交代採用原因。

### 前置（參數）
1. `Then` 的 failure outcome 應具體表達為 validation failure，且錯誤訊息必須直接對應被測參數條件。
2. 若未來此 rule type 增加動態 verifier slot，應優先證明 side effect 不得發生。
3. 不得用過大的 state scope 間接猜測 validation failure，也不得把 unrelated state drift 混入 failure path 驗證。
