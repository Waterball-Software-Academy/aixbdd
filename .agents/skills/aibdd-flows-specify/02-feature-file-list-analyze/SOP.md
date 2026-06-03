# 參數設定

- **需求故事錨點** → `${PLAN_SPEC}`（`${CURRENT_PLAN_PACKAGE}/spec.md`）
- **Discovery 報告（function package charters 來源）** → `${PLAN_REPORTS_DIR}/discovery-sourcing.md`
- **Feature 規格／`.feature` 根目錄** → `${FEATURE_SPECS_DIR}`（= `${TRUTH_FUNCTION_PACKAGE}/features`，per function package 借位解析）

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

0. **RESOLVE arguments**——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

   0.1 READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 `## Function package charters` 與 `## Packaging decision`，DERIVE `$function_packages[]`（本輪涉及的 `packages/NN-<slug>` 與各自職責／納入／排除）。後續每個萃取出的 Feature File 都要綁定到其中**一個** function package，據以決定落檔目錄（該 package 的 `${FEATURE_SPECS_DIR}` = `packages/NN-<slug>/features/`）。

1. THINK: 拆解 `${PLAN_SPEC}` 中需求敘述的每一段話，進行段落流程建模分析。標註每一段話為 $P，所有話的集合為 all $P。

2. FAITHFUL REASONING: FOR EACH $P，萃取此段落句子中的 RESTful-API-like 業務動作，請勿捕捉句子中不存在的元素，因此捕捉過程針對每一個捕捉物都要明確指出他對應的證據（指回 `${PLAN_SPEC}` 原文段落）。
    - $FeatureFiles = 嚴格遵照 [`rules/apiwise-granularity.md`](rules/apiwise-granularity.md) 的顆粒度定義來萃取：一個 Action ＝一次由 Actor 主動觸發、可獨立驗收業務結果的完整業務行動；流程編排／系統自動推進／內建處理**不**獨立成 Action。
    - `$GAPS` = 當你發現底下現象時，將此現象記錄起來儲存於內部推理思考的 GAPS 空間中，留待步驟 4 澄清：
        - 針對某個 Feature File 不確定他的顆粒度是否正確、是否應該被列為獨立 Feature File（例：疑似把系統自動推進誤收成 Action，或同一使用者意圖被拆成多個技術步驟）。
        - 某段需求暗示了業務動作，但證據不足以判定 Actor、觸發點或可驗收結果。
        - 某個 Action 無法明確歸屬到任一既有 `$function_package`。

3. **WRITE feature-file 骨架（rule-less）** — FOR EACH `$FeatureFiles` 中**證據充足**之 Action（落入 `$GAPS` 者不在本步落檔，交步驟 4）：在其綁定 function package 的 `${FEATURE_SPECS_DIR}`（= 該 `packages/NN-<slug>/features/`）下 CREATE 一個 `.feature` 檔。
    - **檔名**：`<NN>-<action-slug>.feature`，`<NN>` 為該 package 內兩位數序號，`<action-slug>` 以 `$package_naming_language` 表業務意圖（例：`01-會員登入.feature`）。**檔名須 Windows-safe**：不得含 `\ / : * ? " < > |` 及結尾空白／點號。
    - **內容只寫檔頭骨架**，逐行如下（**不得**寫入任何 `Rule:`、`Background`、`Scenario`、`Examples`、Step；那些留給 `/aibdd-rules-specify` 與後續 SBE 階段）：

      ```gherkin
      # @ignore - 等執行 /aibdd-red-execute 時，會只將 target Feature file 標注的 @ignore 拿掉，透過此手段來控制範疇。
      @ignore
      Feature: <表該 Action 業務意圖的標題>
      ```
    - `Feature:` 標題表**業務意圖**，不得等同實作細節或內部技術步驟名稱（對齊 `rules/apiwise-granularity.md`）。
    - **冪等**：同一 Action 對應之 `.feature` 已存在時**不覆寫、不重建**（保留既有檔頭與任何下游已補的內容）；僅在缺檔時新建。
    - 本步**唯一允許**的 WRITE target 是上述 `${FEATURE_SPECS_DIR}` 下之 `.feature` 骨架；**禁止**順手建立 `dsl.yml`、contracts／data、或 features 目錄以外的任何檔。

4. 若 `$GAPS` 非空（**至少要逐項處理**）：DELEGATE `/clarify-loop`，帶 `delegated_intake`（`phase`=`aibdd-flows-specify/02-feature-file-list-analyze`、`raw_items`=各 GAP 一句話描述、`anchors`=對應 `${PLAN_SPEC}` 段落與候選 function package）。澄清結論若改變 Action 顆粒度或歸屬，回步驟 2／3 修正落檔。

5. 向使用者說道（語意不變、詞彙可改）：「OK，本輪需求已被拆成下列 feature file 清單（各為 rule-less 骨架）：<逐一列出檔案路徑與對應業務意圖>。接著 /aibdd-rules-specify 會為每個 `.feature` 列舉其驗收用的 atomic rules。」
