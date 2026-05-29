針對單一 `.feature` 做 faithful arrangement。

# Task

1. READ 當前 `.feature` 全文，逐一處理其中每個 `Rule`。

2. [LOOP] FOR EACH `Rule`：
    1. READ 該 `Rule` 的 atomic rule 文字，以及其底下的 `Example` / `Scenario Outline` skeleton 區塊。
    2. READ 該 `Rule` 對應的 `When` step 與其前後結構，將本 `Rule` 的 arrangement 視為兩大部位：
        1. `Given` 部位——主操作前的前置建構區塊。
        2. `Then` 部位——主 assertion 與其後續延伸驗證區塊。
    3. READ 本 `Rule` 內各 `# @dsl` block 的 `# rule:`、`# handler-candidate-kinds:` 與 `# candidates:` 三欄位。以該 `Rule` 所指示之 `# rule:` 路徑檔案作為指導最高標準，依據指導來適當編排此 Rule 底下 Example 的 Given and Then DSL Block。
    5. HYDRATE `candidate_specs`——只在 `${CONTRACTS_DIR}`、`${DATA_DIR}`、`${BOUNDARY_SHARED_DSL}` 內解析 `# candidates:` 已列出的名稱，補成 `name`、`handler`、`format`、`target_part_path`、`param_bindings`、`datatable_bindings`；這一步只做 hydration，不做新的 candidate 搜尋。
    6. DERIVE 本 `Rule` 共用的 arrangement input——在 `When` 已固定的前提下，推出本 `Rule` 所需的 `tested_target`、`required_test_values` 與其他最小必要 reasoning context；若資訊不足以唯一決定，組成 `$questions`，交回外層 phase 走 `/clarify-loop`，本 worker 直接 STOP。
    7. ARRANGE `Given` 部位——先消費 shared Given law 的 `Given Block`（Decision Tree、Forces、Optimization、Legality Gate），再疊加 shared Given law 內對應 rule type 不同的 Given 區塊指示進行綜合的 FAITHFUL REASONING；完成前置建構 strategy、legality gate 與 optimization。
    8. ARRANGE `Then` 部位——先消費 shared Then law 的 `Then Block` legislation，再疊加 shared Then law 內對應 rule type 不同的 Then 區塊指示進行綜合的 FAITHFUL REASONING；完成 verifier selection、必要的過濾與取捨、arrangement rules 與 optimization。
    9. WRITE arrangement result：
        1. 將本 `Rule` 底下 `Given` 與 `Then` 部位中的 `<dsl>` placeholder 替換為對應的一條或多條 concrete dsl steps。
        2. 值保留 placeholder，不在此步做 binding。
        3. 依 shared Given law 與 shared Then law 要求輸出。

3. UPDATE FILE: 清理此 Feature file，把那些決策相關的 metadata 註解，如 `# @dsl` meta 註解全部刪掉，Feature File 只留下那些漂亮的 Gherkin。

# Worker hard limits：
1. 不得發明 `# candidates:` 之外的新 DSL。
2. 不得變更 `When` step。
3. 若 `$questions` 非空，本 worker 不做使用者互動，也不做最終寫回。

# Completion contract。
   1. 每個 `.feature` 完成後，該檔內所有 placeholder `# @dsl` block 都應已被 concrete dsl arrangement 取代。
   2. 本步完成後的 feature files 應該每個 Rule 底下都已經至少存在一個 Example，每個Example 都有明確安排 DSL steps。
   3. Feature 中的每一個 Rule/ Example 區塊都不應該決策相關的 metadata 註解（規格領域知識之註解除外），必須只留下 Gherkin arrangement。
   4. 若 `$questions` 非空，worker 回傳 incomplete；外層 phase 需先完成 clarify，然後才可重跑本 worker。
