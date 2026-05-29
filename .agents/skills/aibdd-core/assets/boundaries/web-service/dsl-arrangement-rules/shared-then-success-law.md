# Shared Then Law (success) — web-service

1. 本檔是 web-service boundary 中所有 success polarity rule 的共用 `Then` legislation SSOT。
2. success polarity 指的是主操作預期成功的 rule，包含 `後置（回應）` 與 `後置（狀態）`。
3. 本檔同時承載 success polarity 下各 rule type 的 `Then Delta` 小節；不得把同一份 delta 再散落回獨立 rule 檔。

## Then Block

### Forces
1. `Then` 的第一個 load-bearing assertion 是主操作成功。
2. `Then` 的主驗證來源是成功後的 direct effect，不是 `Then 操作成功` 本身。
3. direct effect 可以是 response surface，也可以是 persisted state／external effect／resource delta；具體 verifier 類型由 rule-type-specific `Then Delta` 決定。
4. verifier scope 應優先選最小、最直接、最少額外推論的 assertion。
5. 若 direct owner verifier 可用，優先 direct owner；只有在 rule-type-specific `Then Delta` 明確允許時，才退到最小可證明的 proxy verifier。

### Legality Gate
1. `Then` 不得拿 `Then 操作成功` 單獨充當 expected effect 的證明。
2. `Then` 不得選擇與當前 success path 無直接關聯的 sibling verifier、sibling operation，或 broad snapshot assertion。
3. `Then` 的 dynamic verifier 必須直接對應 atomic rule 的 tested target 與 expected effect。
4. 不得把 response surface 與 persisted state 互相冒充；若 rule-type-specific `Then Delta` 要求其一，另一者不得拿來替代。

### Output Expectation
1. `Then` 應先保留 form 已凍結的 success sentence，再安排動態 verifier。
2. rule-type-specific `Then Delta` 只負責補充 success 類型專屬的 verifier family、tie-break、veto 與 trace expectation。

## Rule-Type Then Delta

### 後置（回應）
1. `Then` 的 direct-effect source 是 response surface，不是 persisted state。
2. 在 `Then 操作成功` 之後，應驗與 atomic rule 直接對應的 response field。
3. 優先選 assertion scope 最小、最少額外推論的 response verifier。
4. 不得拿 DB row、readmodel 或其他 persisted state 來替代 response verification。
5. 拒絕需要先偷看 persisted state 才能判定 response 正確的 verifier。
6. 拒絕與當前 response field 無直接對應的 broad snapshot assertion。
7. 拒絕與 success path 無關的 sibling operation 或 sibling verifier。
8. `Then` 應選出最小 response verifier，並在 `# @decision:` / `# @rationale:` 交代採用原因與主要淘汰理由。

### 後置（狀態）
1. `Then` 的 direct-effect source 是 changed state，不是 response success。
2. `Then` 應依 `後置（狀態）` 子類選 verifier：
   1. `資料`：優先 persisted row / entity state verifier。
   2. `外發`：優先 external stub / outbox / inbox / emission record verifier。
   3. `資源`：優先餘額、額度、鎖、庫存等 resource-facing verifier。
   4. `行為`：優先能直接證明指定行為或冪等差異的 verifier。
3. 若 direct owner verifier 可用，優先 direct owner；不可用時，才退到最小可證明變化的 proxy verifier。
4. 不得拿 `Then 操作成功` 或 response payload 充當 state change 證明。
5. 拒絕無法提供明確 before-state baseline 的 `Given`。
6. 拒絕只能證明「操作成功」卻不能證明「狀態改變」的 verifier。
7. 拒絕與當前 `tested_target` 無直接關聯的 sibling verifier。
8. `Then` 應選出最小 changed-state verifier，並在 `# @decision:` / `# @rationale:` 交代採用原因與主要淘汰理由。
