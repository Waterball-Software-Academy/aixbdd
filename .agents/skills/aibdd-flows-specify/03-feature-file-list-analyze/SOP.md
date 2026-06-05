# 參數設定

- **Action↔feature 綁定來源（本 phase 的落檔清單）** → 上游 Phase 02（`02-activity-analyze`）萃取之 `$Actions`（每個帶 `binds_feature` 契約路徑）；其已落檔之 `.activity`（Action 節點 `binds_feature`）為持久 SSOT
- **Feature 規格／`.feature` 根目錄** → `${FEATURE_SPECS_DIR}`（= `${TRUTH_FUNCTION_PACKAGE}/features`，per function package 借位解析）
- **影響矩陣（本 phase 回寫新 feature 的 `add` entry）** → `${IMPACT_MATRIX_YML}`；entry `path` 相對 `${TRUTH_BOUNDARY_ROOT}`

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

0. **RESOLVE arguments**——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

   0.1 DERIVE `$action_features` ＝ Phase 02 `$Actions` 的**完整**清單（每筆 = 一個 `binds_feature` 路徑 + 一行業務意圖標題）。**壓縮後還原**：若 in-context 清單已遺失，RECONSTRUCT ＝ 掃描 `${ACTIVITIES_DIR}/**` 各 `.activity` 之 Action 節點 `binds_feature`（取聯集），再對 `${PLAN_SPEC}` 依 [`../02-activity-analyze/rules/apiwise-granularity.md`](../02-activity-analyze/rules/apiwise-granularity.md) 補回**未綁進任何 flow 的純查詢 Action**（其在 Phase 02 仍具 `$Actions` 身分）。ASSERT `$action_features` 非空；為零 → STOP，向使用者回報：「尚未偵測到 Phase 02 的 Action／`.activity` 產物，請先讓 `/aibdd-flows-specify` 跑完 `02-activity-analyze` 再落 feature 骨架。」

1. **WRITE feature-file 骨架（rule-less）** — FOR EACH `$action_features`：在其 `binds_feature` 路徑 CREATE 一個 `.feature`（路徑 = `${FEATURE_SPECS_DIR}/<NN>-<action-slug>.feature`，與 Phase 02 `binds_feature` **完全一致**，以維持 `.activity` Action 節點 → `.feature` 的一一對應）。
    - **內容只寫檔頭骨架**，逐行如下（**不得**寫入任何 `Rule:`、`Background`、`Scenario`、`Examples`、Step；那些留給 `/aibdd-rules-specify` 與後續 SBE 階段）：

      ```gherkin
      # @ignore - 等執行 /aibdd-red-execute 時，會只將 target Feature file 標注的 @ignore 拿掉，透過此手段來控制範疇。
      @ignore
      Feature: <表該 Action 業務意圖的標題>
      ```
    - `Feature:` 標題表**業務意圖**，不得等同實作細節或內部技術步驟名稱（對齊 [`../02-activity-analyze/rules/apiwise-granularity.md`](../02-activity-analyze/rules/apiwise-granularity.md)）。
    - **冪等**：同一 Action 對應之 `.feature` 已存在時**不覆寫、不重建**（保留既有檔頭與任何下游已補的內容）；僅在缺檔時新建。
    - **一致性**：Phase 02 每個 `.activity` Action 節點之 `binds_feature` 都須對應到本步建立（或既存）之 `.feature`；若某 `binds_feature` 路徑非法或無法建立，記錄並交步驟 2。
    - 本步**唯一允許**的 WRITE 是上述 `${FEATURE_SPECS_DIR}` 下之 `.feature` 骨架；**禁止**順手建立 `dsl.yml`、contracts／data、features 目錄以外的任何檔，**亦禁止**改寫 Phase 02 的 `.activity`。

2. 若有無法落檔的 `binds_feature`（步驟 1 記錄）：DELEGATE `/clarify-loop`，帶 `delegated_intake`（`phase`=`aibdd-flows-specify/03-feature-file-list-analyze`、`raw_items`=各問題一句話描述、`anchors`=對應 Action／`.activity`／預期 feature 路徑）。澄清結論若改變檔名或綁定，回步驟 1 修正落檔（如同步改了 `.activity` 的 `binds_feature`，請回 `02-activity-analyze` 重送該 flow）。

3. **WRITEBACK impact matrix（本輪新增之 `.feature` → `add`）** — EXECUTE [`steps/impact-matrix-writeback.md`](steps/impact-matrix-writeback.md)：把步驟 1 **本輪新建**之每個 `.feature` 以其 `binds_feature`（相對 `${TRUTH_BOUNDARY_ROOT}`）`upsert`（`change_type=add`）回寫 `${IMPACT_MATRIX_YML}`，再 `validate`。此為本輪 feature `add` entry 的**唯一**產生點；既有未改寫之 `.feature` 已由 sourcing 寫入對應 entry，**不**在本步重寫。

4. 向使用者說道（語意不變、詞彙可改）：「OK，本輪需求已被拆成下列 feature file 清單（各為 rule-less 骨架，且與 `.activity` 的 Action 節點一一對應），並已將新 feature 以 `add` 回寫影響矩陣：<逐一列出檔案路徑與對應業務意圖>。接著 /aibdd-rules-specify 會為每個 `.feature` 列舉其驗收用的 atomic rules。」
