# 參數設定

- **需求故事錨點** → `${PLAN_SPEC}`（`${CURRENT_PLAN_PACKAGE}/spec.md`）
- **Discovery 報告** → `${PLAN_REPORTS_DIR}/discovery-sourcing.md`（澄清擱置機讀題組：`${PLAN_REPORTS_DIR}/discovery-clarify-pending.payload.yml`）
- **Activity 規格／`.activity` 根目錄** → `${ACTIVITIES_DIR}`
- **Feature 規格／`.feature` 根目錄** → `${FEATURE_SPECS_DIR}`

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. [LOOP] FOR EACH 上一 Phase 產出的 Feature File - 列舉其中的所有 atomic rules (每一個 Feature File 開設一個 TODO TASK，每個 TASK 進行底下兩步驟）：
   1.1 **FAITHFUL REASONING：FOR EACH 上一 Phase 產出的 Feature File，列舉其中的所有 atomic rules**：
      - **READ** `rules/atomic-rule-granularity.md`，atomic rule 的顆粒度、命名句型、4 種類型前綴、原子化判定、禁止自生**全部**以此檔為準。
      - 對每個 Feature File：依其 Phase 02 已綁定之 Action，到 **`${PLAN_SPEC}`** 找對應的 raw 敘述段落；找不到對應句子 → 該 Feature 不產 rule，列為「來源缺失」交後續步驟澄清。

   1.2 **UPDATE FILES** — **READ** `templates/atomic-rule-format.template.feature`。**FOR EACH** 本 TASK 對應之 `.feature`（路徑須落在 **`${FEATURE_SPECS_DIR}`** 下）：將步驟 **1.1** 為**該檔**推理出之 `$RULES` 子集（僅含鎖定此檔者）依**模板之縮排與區塊結構**寫入同一檔案。
      - **語意、類型前綴、原子化與禁止自生**以 `rules/atomic-rule-granularity.md` 為準；**檔案版面**（`Feature:` 下之縮排、`Rule:` 區塊、選用之 `- ` 補充行、`# TODO - 待 SBE`）以模板為準。
      - **保留**既有檔頭（含 `#` 註解列、`@ignore`、`Feature:` 標題）；**不得**改壞標題語意、**不得**新增 `Background`／`Scenario`／`Examples`／Examples 表格或 Step 綱要。
      - 每一條原子 rule：**一行** `Rule: <類型前綴> - <主詞> 必須／應 <單一條件>`，`<類型前綴>` 僅得為 **前置（狀態）**、**前置（參數）**、**後置（回應）**、**後置（狀態）**；**前置**用「**必須**」、**後置**用「**應**」；**連字號兩側空格**與模板一致。該行之下得依模板加 **`- `** 開頭之補充說明（**不得**塞範例數值表或 Gherkin Steps），並得保留 **`# TODO - 待 SBE`** 占位。
      - 模板中四段 `Rule:` 為**排版示例**；實際檔案只輸出有 raw 證據之 rule，條數與順序不拘，類型可重複。
      - 同一檔內已存在之同一 `Rule:` **主句**不重複寫入；無 rule 可寫（來源缺失等）則**不更動**正文並列澄清隊列。

2. DERIVE **`$FINDINGS = $VIOLATIONS ∪ $AMBIGUITY_FINDINGS`**（含「來源缺失」）。

3. IF **`$FINDINGS` 非空** → **DELEGATE** `/clarify-loop`，**`delegated_intake`**：**`profile`**＝**`aibdd-discovery`**，**`phase`**＝**`atomic-rules`**，`raw_items`←`$FINDINGS` 每筆之 **`text`**，`anchors` 鍵同上 **02** 步驟 **9**。若 **`completed`**：依回傳合流 **`${PLAN_SPEC}`** 與相關 **`.feature`**。

4. 向使用者：**IF **`$FINDINGS` 為空**或步驟 **3** 回傳 `completed`** → 說道（語意不變即可）：「OK，很好，每個 Feature File 對應的規則我想我們是分析完了，現在每個 Feature File 都定義好了你本次需求的所有規則，你的系統的複雜度以及之後的實作將由這些規則的驗收測試所驅動，你明白嗎？」**IF 步驟 **3** 回傳 `unsupported_tooling`** → 唯轉述 **`/clarify-loop`** 回傳（含 **`artefacts.wrote`**），**不得**在聊天重造題組。**END** Sub-SOP。
