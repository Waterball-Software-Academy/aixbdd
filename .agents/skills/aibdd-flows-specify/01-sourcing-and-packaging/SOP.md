# SOP

0. 解析 arguments 與 spec root folder structure
  
  0.0 將本 SOP 引用的變數透過 resolver 綁定，並把 resolver stdout（每行一筆 KEY=value）原樣顯示給用戶。Resolver 非 0 退出時，STOP 並把 stderr 透傳給用戶。

    ```bash
    python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
    CONTRACTS_DIR=${CONTRACTS_DIR}
    CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
    DATA_DIR=${DATA_DIR}
    FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
    IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
    PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
    PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
    PLAN_SPEC=${PLAN_SPEC}
    PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
    TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
    TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
    TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
    EOF
    ```

  0.1 READ `aibdd-flows-specify/rules/specs-root-layout.md` 作為本 sub-SOP 內所有 `${PLAN_PACKAGES_DIR}` / `${TRUTH_BOUNDARY_ROOT}` / `${TRUTH_BOUNDARY_PACKAGES_DIR}` / `${CONTRACTS_DIR}` / `${DATA_DIR}` 目錄結構路徑的 SSOT。

1. Derive plan package 並 CREATE Dir：若 `$PLAN_PACKAGE_SLUG` 已由 caller-context 提供，ASSERT `${PLAN_PACKAGES_DIR}/$PLAN_PACKAGE_SLUG/` 於 filesystem 存在並沿用；否則依據本輪需求敘事與 slug 命名規則 PRINCIPLE derive `$PLAN_PACKAGE_SLUG`（NNN-<slug>）、CREATE `${PLAN_PACKAGES_DIR}/$PLAN_PACKAGE_SLUG/` 於 filesystem。

2. SEARCH 並錨定 Scope（本步僅 READ／SEARCH／WRITE `${PLAN_SPEC}`；`${TRUTH_BOUNDARY_ROOT}` 下 truth 不寫入；`arguments.yml` 不寫入）

   2.1 依 `aibdd-flows-specify/assets/templates/spec.template.md` 之填寫規則，將使用者本輪需求敘事寫入 `${PLAN_SPEC}`（初始批次）。

   2.2 依本輪需求敘事在 `${DATA_DIR}`、`${CONTRACTS_DIR}`、`${TRUTH_BOUNDARY_PACKAGES_DIR}` 下 READ／SEARCH 規格。本步只讀取並蒐集受影響的 scope 作為 `$IMPACT_ENTRIES`。

3. WRITE `${IMPACT_MATRIX_YML}`，收斂本輪 plan impact scope。matrix 以 impact 為單位：為每個本輪要建立／改動的 spec，以 `(owner, spec)` 為鍵冪等 write 一個 impact，owner 一律 `aibdd-flows-specify`，`quotes` 指回 `${PLAN_SPEC}` 原文、`rationale` 寫該 spec 的規格增量；只被讀取對照以界定範圍的 boundary 規格不寫入 matrix。只經本步 CLI command 更新 `${IMPACT_MATRIX_YML}`：

   3.0 READ `aibdd-core::impact-matrix/cli-usage.md`，取得 CLI 通用規則、資料模型、status 語意與冪等 write 各情境應用 command；詳細 flag 用法以該 reference 為準。

   3.1 首批 sourcing 一次 `init` 建立空檔。

   3.2 `$IMPACT_ENTRIES` 內本輪本 phase 實際建立／改動的 spec（此 phase 僅產出 skeleton `.feature` 與 `.activity` scope），各 spec owner=`aibdd-flows-specify`、`--quote` 帶其所本之 `${PLAN_SPEC}` 原文句（≥1）、`--rationale` 寫規格增量；以 `read` 依 owner+spec-path 定位後 found 則 `write --id` 取代、否則 `write` 新建（CLI 用法見已載入的 manual）。只被讀取對照之 boundary 規格（contracts／data）不寫入。

   3.3 `$IMPACT_ENTRIES` 內本輪需求明文淘汰、但本步未刪檔的既存 spec，以 `read` 取回 id 後 `transit-status --status inconsistent` 標記為待處理；`remove` 留待真正刪除該檔的步驟與刪檔同時執行，本步不 `remove`。

   3.4 本輪未觸及之既存 impact 保留不動。

   3.5 全部 write／remove 完成後，以 `read`（無 filter）取回狀態作為 `$ENTRIES_AFTER` 並原樣顯示給用戶；`$ENTRIES_BEFORE` 為空集合。

4. WRITE `${PLAN_REPORTS_DIR}/discovery-sourcing.md`，格式以 `aibdd-flows-specify/assets/templates/discovery-sourcing.template.md` 為準，語感參照 `aibdd-flows-specify/assets/templates/discovery-sourcing.example.md`，但 Function package charters 章節先不紀錄任何 function packages；UPDATE `${PLAN_SPEC}`，參照 `aibdd-flows-specify/assets/templates/spec.template.md` 之 Discovery Sourcing Summary 段落加上指向 `discovery-sourcing.md` 的 pointer 與可選執行摘要。

5. THINK 拆解 function package 數量（1..*）並決定各 package 職責；bottom-up 規則見 `aibdd-flows-specify/rules/function-package-granularity.md`，`$FUNCTION_PACKAGE_SLUG`（`NN-<slug>`）依據 slug 命名規則 PRINCIPLE 命名。本步只產出判斷，不寫檔。

6. CREATE Dirs Only：於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 建立或沿用各 `${TRUTH_FUNCTION_PACKAGE}`，並僅建 `${FEATURE_SPECS_DIR}` 骨架。禁止建立 `dsl.yml`、`.feature`、`${CONTRACTS_DIR}`、`${DATA_DIR}` 內容或其它規格檔。

7. UPDATE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` Function package charters 章節，依據 `aibdd-flows-specify/assets/templates/discovery-sourcing.template.md` 格式紀錄每個 `$FUNCTION_PACKAGE_SLUG` 職責；UPDATE `${PLAN_SPEC}` Discovery Sourcing Summary 執行摘要。
