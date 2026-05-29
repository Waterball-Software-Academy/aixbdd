# Rule: 移除動作就刪除，不留殘影禁令

- 移除某動作時，必須直接從該步把它刪掉；不得把它改寫成散落在其他步驟的「不要做 X」「不要回到舊流程」禁令。
- 同一條約束僅在一處宣告；不得把同一份禁令清單在多個步驟重複抄寫。
- 刪掉某句後若 skill 的合法行為集合不變，該句即為噪音，必須刪。
- 真正跨步驟、長期有效的 invariant 必須提升為獨立 PRINCIPLE 條款，不得寄生在某個局部步驟的括號裡假裝臨時提醒。

## Good

- 需求改為不再 `CREATE scaffold`：直接刪掉「CREATE scaffold」那一步，其餘步驟不動。
- 「只准改產品程式碼」在 `## PRINCIPLE` 區宣告一次，後續 loop 步驟與 handoff 步驟都不再複述這份禁令清單。

## Bad

- 需求改為不再 `RUN validation`，卻在 `UPDATE feature` 步驟補一句「更新後不要自己跑 validation」。
- 把同一份「不准動 feature／DSL／step-def／runtime ref…」清單，在 PRINCIPLE、loop、handoff 三個地方各抄一遍，讀者每處都要重讀一次相同禁令。

# Rule: 只 instruct 會驅動產出的閱讀（read ≠ use）

- 僅當某檔的內容會驅動後續某個決策或產出時，才得 instruct 讀它。
- 不得保留「讀了卻不影響任何下游步驟」的 read／assert／指紋；存在性檢查不等於使用。
- 一條 read instruction 若拿掉後 skill 的產出不變，該 instruction 必須刪。

## Good

- 因為渲染 step definition 需要 handler 履約與 variant 機制，才 `READ handler doc` 與 `READ variant doc`。
- 因為 drift 判定需要比對 runtime 來源指紋，才去算 runtime ref 的指紋。

## Bad

- SOP 寫「讀進 BDD 憲章」，但後續沒有任何步驟取用它 §5.1／§5.2 的值，只拿它的存在做一次 assert 與指紋——讀了等於沒用。
- green 階段對 `RED_PREHANDLING_HOOK_REF` 做存在性 assert 並納入指紋，但 green 從不執行 pre-red hook，該檢查對 green 的產出毫無影響。

# Rule: 不留 dangling 或無人消費的 reference

- instruction 內引用的每個檔案／變數 key 必須存在，且確實被某步驟消費。
- 刪除某 artifact 時，必須連帶 scrub 所有指向它的 inbound 引用（manifest 列、`*_REF` key、步驟內路徑指標），不得留懸空指標。

## Good

- 刪掉 `report-contract.md` 時，同步拿掉各 sibling skill 內 `aibdd-core::report-contract.md` 的 manifest 列與步驟指標。

## Bad

- 刪了 `red-usable-flat-entry.md`，卻留著 `arguments.yml` 的 `DSL_OUTPUT_CONTRACT_REF: .../red-usable-flat-entry.md`，以及 SOP 內「讀進 DSL_OUTPUT_CONTRACT_REF」這條指向已不存在檔的 read。

# Rule: scope 與輸入由 caller 明確傳入，不從旁路資料源自行重建

- skill 的處理 scope 必須取自 caller 明確傳入的 handoff／payload；不得從旁路全域資料源（如整包 impact matrix）自行重建出更大的 scope。
- 僅當 caller 未傳該輸入、且發現該輸入本就是此 skill 的職責時，才得自行推導。
- 同時持有 caller scope 與旁路來源時，必須以 caller scope 為準，並用旁路來源做交叉驗證而非取代。

## Good

- green-execute 直接以「上游指定的 target feature files」作為 `$SCOPE_FEATURE_FILES`，再與 `red_handoff.target_feature_files` 交叉驗證一致。

## Bad

- green-execute 改用 impact-matrix query 撈出整個 plan 的 features 當 scope，導致它以為整個 plan 都要轉綠，而不是只處理 caller 這次點名的子集。

# Rule: 文件路徑用 inline-code 標注，不用 markdown 連結

- instruction 內引用任何檔案／資料夾／sub-SOP 路徑，必須用純 inline-code `` `<path>` `` 標注。
- 不得用 markdown 連結語法 `[text](path)`：它 render 後才看得到 target，raw 形式下同一路徑被寫兩遍純屬裝飾噪音，而 skill 文本是給 LLM 讀 raw 的。

## Good

- `EXECUTE \`steps/verify-no-drift.md\``
- 依 `references/handoff-schemas.md` 解析 red handoff。

## Bad

- 把子 SOP 引用寫成 `EXECUTE [steps/verify-no-drift.md](steps/verify-no-drift.md)`（markdown 連結）。
- 把 reference 引用寫成 `依 [references/handoff-schemas.md](references/handoff-schemas.md) 解析`。
