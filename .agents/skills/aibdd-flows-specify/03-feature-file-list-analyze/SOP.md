# SOP

0. 解析 arguments

  0.0 將本 SOP 引用的變數透過 resolver 綁定，並把 resolver stdout（每行一筆 KEY=value）原樣顯示給用戶。Resolver 非 0 退出時，STOP 並把 stderr 透傳給用戶。

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

  0.1 取 `$ACTION_FEATURES`（本輪每個 action 之 binds_feature path）；若 `$ACTION_FEATURES` 不可考，READ `$ENTRIES_AFTER` 中 activity entries 對應之 `.activity`，將其 action 節點 binds_feature 取聯集，並依 `aibdd-flows-specify/02-activity-analyze/rules/apiwise-granularity.md` 對 `${PLAN_SPEC}` 補回未綁進任何 flow 的純查詢 action 重建。
  
  0.2 ASSERT `$ACTION_FEATURES` 非空；為空則 STOP，向使用者回報尚未偵測到任何 activity entry，請先完成 activity diagram 建模再建構 feature 骨架。

1. 決定本輪落檔範圍：

  1.1 若 `$MODE` 為 RECONCILE，`$ACTION_FEATURES` 限縮為 `$ENTRIES_BEFORE` 與 `$ENTRIES_AFTER` 有差異所涉及之 action（新增者新建、既有者不動）。

  1.2 本輪需求已不再涵蓋（無任何 `.activity` action 節點 binds_feature 指向、或需求明文淘汰）且 `.feature` 已落地之既存 spec，記入 `$OBSOLETE_FEATURES` 待 DELETE。無法確證來源者記入 `$BLOCKED` 待澄清。

2. WRITE feature-file 骨架（rule-less）：

  2.1 針對 `$ACTION_FEATURES` 每個 action 的 binds_feature path（`${FEATURE_SPECS_DIR}/<NN>-<action-slug>.feature`），在該 path CREATE `.feature`，維持 `.activity` action 節點與 `.feature` 一一對應；同一 action 對應之 `.feature` 已存在時不覆寫、不重建，僅在缺檔時新建。

  2.2 `.feature` 內容只寫檔頭骨架，逐行如下（不得寫入任何 Rule:、Background、Scenario、Examples、Step）：

    ```gherkin
    # @ignore - 等執行 /aibdd-red-execute 時，會只將 target Feature file 標注的 @ignore 拿掉，透過此手段來控制範疇。
    @ignore
    Feature: <表該 action 業務意圖的標題>
    ```

  2.3 Feature: 標題填該 binds_feature 對應 action 之業務意圖，不得等同實作細節或內部技術步驟名稱。

  2.4 一致性確認：每個 `.activity` action 節點之 binds_feature 都須對應到本步建立或既存之 `.feature`；某 binds_feature path 非法或無法建立則記入 `$BLOCKED`。

3. DELETE `$OBSOLETE_FEATURES`：若 `$OBSOLETE_FEATURES` 非空，各刪除目標須先 ASSERT 已無任何 `.activity` action 節點 binds_feature 指向（仍被綁定者不刪、記入 `$BLOCKED` 待澄清），確認後 DELETE `${FEATURE_SPECS_DIR}` 下該些 `.feature`，實際刪除者記為 `$DELETED_FEATURES`；刪除清單於結尾報告列出。

4. WRITE `${IMPACT_MATRIX_YML}`，回寫本輪新建之 `.feature`。為每個本輪建立的 `.feature` spec，以 `(owner, spec)` 為鍵冪等 write 一個 impact，owner 一律 `aibdd-flows-specify`，`quotes` 指回 `${PLAN_SPEC}` 原文、`rationale` 寫該 `.feature` 的規格增量。只經本步 CLI command 更新 `${IMPACT_MATRIX_YML}`：

  4.0 READ `aibdd-core::impact-matrix/cli-usage.md`，取得 CLI 通用規則、資料模型、status 語意與冪等 write 各情境應用 command；詳細 flag 用法以該 reference 為準。

  4.1 針對本輪新建之每個 `.feature`，取其 binds_feature 相對 `${TRUTH_BOUNDARY_ROOT}` 路徑（即 `packages/<NN-slug>/features/<NN>-<action-slug>.feature`）為 spec，owner=`aibdd-flows-specify`、`--quote` 帶其所本之 `${PLAN_SPEC}` 原文句（≥1）、`--rationale` 寫規格增量、spec status 以 `inconsistent` 落地；以 `read` 依 owner+spec-path 定位後 found 則 `write --id` 取代、否則 `write` 新建（CLI 用法見已載入的 manual）。

  4.2 對 `$DELETED_FEATURES` 之每個 `.feature`，以 `read` 取回其 impact id 後 `remove --id`（matrix `remove` 對應實際刪檔）。

5. 釐清 `$BLOCKED`：若 `$BLOCKED` 非空，逐項 DELEGATE /clarify-loop 釐清，每項附其對應 action、`.activity` 或預期 feature 路徑作 anchor；澄清結論若改變檔名或綁定，回對應步驟重新依序執行；若須調整 `.activity` 的 binds_feature，則重新執行 activity diagram 建模流程。

6. 向使用者說道（語意不變、詞彙可改）：「OK，本輪需求已被拆成下列 feature file 清單（各為 rule-less 骨架，且與 `.activity` 的 action 節點一一對應），並已將新 feature 以 add 回寫影響矩陣：<逐一列出檔案路徑與對應業務意圖>。」
