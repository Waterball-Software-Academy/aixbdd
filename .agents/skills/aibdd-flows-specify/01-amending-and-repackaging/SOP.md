# SOP — 需求變更（鎖定既有 plan package，套用本輪需求增量）

0. 解析 arguments 與 spec root folder structure

  0.0 將本 SOP 引用的變數透過 resolver 綁定，並把 resolver stdout（每行一筆 KEY=value）原樣顯示給用戶。Resolver 非 0 退出時，STOP 並把 stderr 透傳給用戶。Resolver 輸出的 plan package 仍含 <<NNN-plan-slug>> 借位符，由 caller-context 已鎖定的 `$PLAN_PACKAGE_SLUG` 解析為具體路徑；若 caller-context 沒有已鎖定的 slug，STOP 並回報「plan package 未鎖定，請回上下文解析」。

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

1. ASSERT plan package 存在並補建骨架

  1.1 ASSERT `${PLAN_PACKAGES_DIR}/$PLAN_PACKAGE_SLUG/` 存在於 filesystem。

  1.2 若 `${PLAN_SPEC}` 不存在，依據 `aibdd-flows-specify/assets/templates/spec.template.md` CREATE 空骨架，僅含需求描述章節之標題。

  1.3 若 `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 不存在，依據 `aibdd-flows-specify/assets/templates/discovery-sourcing.template.md` CREATE 空骨架，僅含各章節之標題。

  1.4 若 `${IMPACT_MATRIX_YML}` 不存在，紀錄 `$IMPACT_MATRIX_MISSING` = true，不於此步補建。

  1.5 既有產物一律 READ Only 載入，不在本步改寫。

2. UPDATE `${PLAN_SPEC}` 依據 `aibdd-flows-specify/assets/templates/spec.template.md` 之填寫規則 ，將本輪變更敘事追加為新批次。

3. UPDATE `${IMPACT_MATRIX_YML}`，維護本輪 plan impact scope。matrix 以 impact 為單位：為每個本輪要建立／改動的 spec，以 `(owner, spec)` 為鍵冪等 write 一個 impact，owner 一律 `aibdd-flows-specify`，`quotes` 指回 `${PLAN_SPEC}` 原文、`rationale` 寫該 spec 的規格增量；只被讀取對照以界定範圍的 boundary 規格不寫入 matrix。只經本步 CLI command 更新 `${IMPACT_MATRIX_YML}`：

   3.0 READ `aibdd-core::impact-matrix/cli-usage.md`，取得 CLI 通用規則、資料模型、status 語意與冪等 write 各情境應用 command；詳細 flag 用法以該 reference 為準。

   3.1 若 `$IMPACT_MATRIX_MISSING` = true，跑一次 `init` 建立空檔；false 則略過。

   3.2 以 `read`（無 filter）snapshot impact matrix 作為 `$ENTRIES_BEFORE`，並原樣顯示給用戶。

   3.3 依據 `$ENTRIES_BEFORE` 和 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`，REASONING 本輪 plan 建立前 `${DATA_DIR}`、`${CONTRACTS_DIR}`、`${TRUTH_BOUNDARY_PACKAGES_DIR}` 的 baseline 規格狀態；允許 READ／SEARCH `${DATA_DIR}`、`${CONTRACTS_DIR}`、`${TRUTH_BOUNDARY_PACKAGES_DIR}` 以確認規格。

   3.4 依據 `${PLAN_SPEC}` 內全批次需求敘事重新 REASONING 本輪 plan 在 `${DATA_DIR}`、`${CONTRACTS_DIR}`、`${TRUTH_BOUNDARY_PACKAGES_DIR}` 的 baseline 規格狀態下所影響之 scope 作為 `$IMPACT_ENTRIES`。

   3.5 `$IMPACT_ENTRIES` 內本輪本 phase 實際建立／改動的 spec（此 phase 僅產出 skeleton `.feature` 與 `.activity` scope），各 spec owner=`aibdd-flows-specify`、`--quote` 帶其所本之 `${PLAN_SPEC}` 原文句（≥1）、`--rationale` 寫規格增量；以 `read` 依 owner+spec-path 定位後 found 則 `write --id` 取代、否則 `write` 新建（CLI 用法見已載入的 manual）。只被讀取對照之 boundary 規格（contracts／data）不寫入。

   3.6 `$IMPACT_ENTRIES` 內本輪需求明文淘汰、但本步未刪檔的既存 spec，以 `read` 取回 id 後 `transit-status --status inconsistent` 標記為待處理；`remove` 留待真正刪除該檔的步驟與刪檔同時執行，本步不 `remove`。

   3.7 本輪未觸及之既存 impact 保留不動。

   3.8 全部 write／remove 完成後，以 `read`（無 filter）取回狀態作為 `$ENTRIES_AFTER` 並原樣顯示給用戶。

4. UPDATE `${PLAN_REPORTS_DIR}/discovery-sourcing.md`： `aibdd-flows-specify/assets/templates/discovery-sourcing.template.md` 格式就地更新既有章節使其反映全批次淨需求後的當前真相，但先不更新 Function package charters 章節；禁止新增章節（例：每批次的變更紀錄章節）、不保留過期敘述，章節結構與語感對齊 `aibdd-flows-specify/assets/templates/discovery-sourcing.template.md／discovery-sourcing.example.md`；UPDATE `${PLAN_SPEC}`，參照 `aibdd-flows-specify/assets/templates/spec.template.md` 之 Discovery Sourcing Summary 段落確認指向 `discovery-sourcing.md` 的 pointer 存在並更新可選執行摘要。

5. 推理 function package 級影響：

  5.1 READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md`。

  5.2 依據 bottom-up 規則見 `aibdd-flows-specify/rules/function-package-granularity.md`，THINK 需求變更對既存 function packages 造成新增職責或調整邊界之影響作為 `$AFFECTED_FUNTION_PACKAGES` 以及須要新增之 function packages 作為 `$NEW_FUNTION_PACKAGES`，本步不寫檔。留意本 plan 變更型態欄位反映本 plan 對應 baseline 規格狀態之變更，不得因「本批次只是修改」改判 impact-only。

6. CREATE Dirs Only：僅針對 `$NEW_FUNTION_PACKAGES`，於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 建立其 `${TRUTH_FUNCTION_PACKAGE}`，並僅建 `${FEATURE_SPECS_DIR}` 骨架；既有 function package 一律沿用，不重建。禁止建立 `dsl.yml`、`.feature`、`${CONTRACTS_DIR}`、`${DATA_DIR}` 內容或其它規格檔。無需新開則略過。

7. UPDATE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` Function package charters 章節，依據 `aibdd-flows-specify/assets/templates/discovery-sourcing.template.md` 格式將 `$AFFECTED_FUNTION_PACKAGES` 更新至內容；UPDATE `${PLAN_SPEC}` Discovery Sourcing Summary 執行摘要。
