# SOP

0. READ [`rules/specs-root-layout.md`](rules/specs-root-layout.md) 作為本 sub-SOP 內所有 `${PLAN_PACKAGES_DIR}` / `${TRUTH_BOUNDARY_ROOT}` / `${TRUTH_BOUNDARY_PACKAGES_DIR}` / `${CONTRACTS_DIR}` / `${DATA_DIR}` 路徑解析與 `Impact matrix` 第一欄路徑的 SSOT。

0.1 DERIVE `$package_naming_language`：從 ${DSL_KEY_LOCALE} 直接決定使用目錄名稱之語系。若無慣例則依需求原文主體用字決定。後續 slug 須與該語系一致，禁止無理由中英檔名混拼。若無法判斷則 /clarify-loop 詢問用戶。

1. ANCHOR + SEARCH（本步僅 READ／SEARCH／WRITE `${PLAN_SPEC}`；`${TRUTH_BOUNDARY_ROOT}` 下 truth 不寫入；`arguments.yml` 不寫入）
   - 1.1 若當前 plan slug 尚未由 caller-context 提供：DERIVE `$plan_package_slug`（`NNN-<slug>`）→ CREATE `${PLAN_PACKAGES_DIR}/$plan_package_slug/` 於 filesystem → 將 `$plan_package_slug` 作為 return value 回傳上層 orchestrator，後續解析 `${CURRENT_PLAN_PACKAGE}` 借位時以此 slug override → 回到 1.2。`arguments.yml` 中 `CURRENT_PLAN_PACKAGE` 永遠保持 `<<NNN-plan-slug>>` 借位形態，本步**不**改寫 yaml。
   - 1.2 將本輪整理後的需求敘事全文寫入 `${PLAN_SPEC}`；不得以單句摘要取代全文。
   - 1.3 依 1.2 敘事在 `${TRUTH_BOUNDARY_ROOT}` 下 READ／SEARCH boundary truth（含 `${CONTRACTS_DIR}`、`${DATA_DIR}`、`${TRUTH_BOUNDARY_PACKAGES_DIR}` 等；Impact matrix 欄位義務見 `assets/templates/discovery-sourcing.template.md`）。
   - 1.4 若掃描根下無可對照契約／資料：步驟 3 須明列「未找到」與補洞方式；不得以 repo 外私有路徑充當 truth，亦不得順手新建 contracts／data／shared／dsl／`.feature` 來補洞。

2. CREATE DIR：若 1.1 已建立則 ASSERT `${PLAN_PACKAGES_DIR}/$plan_package_slug/` 存在並略過；否則在鎖定 `$package_naming_language` 後 DERIVE `$plan_package_slug`、CREATE `${PLAN_PACKAGES_DIR}/$plan_package_slug/` 於 filesystem，並將 `$plan_package_slug` 作為 return value 回傳上層 orchestrator。**不**改寫 `arguments.yml`（`CURRENT_PLAN_PACKAGE` 保持借位形態）。本步不在 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下新建 functional module 目錄，除非本輪明確要新開 function package。

3. WRITE `${PLAN_REPORTS_DIR}/discovery-sourcing.md`（章節與 placeholder 以 `assets/templates/discovery-sourcing.template.md` 為準；語感對照 `assets/templates/discovery-sourcing.example.md`）。同步 UPDATE `${PLAN_SPEC}`：保留 1.2 需求全文，追加指向該報告的 pointer 與可選執行摘要；不重複貼報告全文。本步僅允許 WRITE 該報告與 UPDATE `${PLAN_SPEC}`。
   - Impact matrix：凡本輪將寫入或列為計畫產物之規格檔（尤其 `${FEATURE_SPECS_DIR}` 下 `.feature`）各一列且變更類型必填；禁止以 glob 代替逐檔展開，除非 Notes 明定下游採 glob 閉包並載明落差風險。

4. THINK：在鎖定 `$package_naming_language` 下拆解 function package 數量（1..*）；bottom-up 規則見 `rules/function-package-granularity.md`。每個 `$function_package_slug`（`NN-<slug>`）須在報告 `## Function package charters` 有職責一句、納入、排除、本輪變更型態。本步只產出判斷，不寫檔。

5. CREATE DIRS ONLY：於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 建立或沿用各 `${TRUTH_FUNCTION_PACKAGE}`，僅建 `${FEATURE_SPECS_DIR}` 骨架。禁止建立 `activities/`、`dsl.yml`、`.feature`、`${CONTRACTS_DIR}`／`${DATA_DIR}` 內容或其它規格檔。目錄示意見 example 內 Spec structure。

6. UPDATE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 與 `${PLAN_SPEC}`（維持 1.2 需求全文與 pointer／摘要；句型對齊 example）。覆核 Impact matrix 符合步驟 3（每規格檔至多一列、`.feature` 逐檔、變更類型已填）；不一致則本步修正。本步僅允許 UPDATE 上述兩檔。
