# 參數設定

- **產出錨點** → 與上層 `research/discovery-拆解/SKILL.md` **PRINCIPLE: CWD 為產出錨點**一致：本 sub-SOP 所有 **CREATE / WRITE / UPDATE** 產物**僅**得置於當次 **`CWD`** 可向內解析之路徑；下列 `${…}` 均相對／錨定於 **`CWD`**。
- **boundary truth（掃描根）** → `${TRUTH_BOUNDARY_ROOT}`（其下 contracts／data／shared／packages 等細節不在此展開；**truth 指 boundary 層級的規格樹**，不指 `packages/NN-…` 資料夾本身）
- **plan package** → `$plan_package_slug`（`NNN-<slug>`）；目錄：`${CURRENT_PLAN_PACKAGE}`
- **discovery report** → `${PLAN_REPORTS_DIR}/discovery-sourcing.md`；**需求敘事全文**與摘要／pointer：`${PLAN_SPEC}`（證據表、Impact matrix、目錄樹以 discovery 報告為 SSOT；**不重複**整份貼回 spec）
- **function package** → `$function_package_slug`（`NN-<slug>`）；根：`${TRUTH_FUNCTION_PACKAGE}`（位於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 之下）；綁定後子目錄：`${ACTIVITIES_DIR}`、`${FEATURE_SPECS_DIR}`
- **package 命名語言** → `$package_naming_language`（例如 `zh-Hant`、`en`；**由**需求原文主體用字 **或** `${SPECS_ROOT_DIR}` 下既有 plan／function package 目錄與 `spec.md` 標題慣例 **DERIVE**；本輪 `$plan_package_slug` / `$function_package_slug` 的 **slug 段**必須與該語言可讀詞彙一致，**禁止**無理由中英混拼）

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

# SOP

0. **DERIVE `$package_naming_language`（命名語系錨點）**
   - **輸入**：本輪需求原文；若 repo 內已存在相關 `specs/**/spec.md`、`specs/**/reports/`、或 `packages/` 下既有目錄名／檔名慣例，一併掃描。
   - **規則**：**優先**對齊既有 specs 樹裡「已出現的命名語系」；若無可對齊慣例，則以需求原文主體用字（腳本與自然語言）決定。
   - **輸出**：鎖定 `$package_naming_language`；後續步驟 **2**、**4**、**5** 在產出 `$plan_package_slug` / `$function_package_slug` 時 **必須**遵守（必要時在 `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 的 `Packaging decision` 或 `Notes` **寫一句**語系決策，避免執行器遺忘）。

1. ANCHOR + SEARCH & THINK

   - **1.1** 分支：`${PLAN_SPEC}` 是否已可解析為可寫入路徑？
     - **否** → `GOTO` 步驟 2（只建立 `${CURRENT_PLAN_PACKAGE}` 並 DERIVE `$plan_package_slug`；**仍不在** `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下新建 `${TRUTH_FUNCTION_PACKAGE}`，除非本輪已明確要新開 function package）→ 回到 **1.2**
     - **是** → `GOTO` **1.2**

   - **1.2** **需求本體入 spec**：將「使用者需求經本輪整理後的敘事文本」**完整**寫入 `${PLAN_SPEC}`，作為本輪範圍與驗收語意的可讀錨點；**永遠不**得以單句摘要取代全文。

   - **1.3** **boundary 掃描**：依 **1.2** 敘事與已知澄清，在 `${TRUTH_BOUNDARY_ROOT}` 下尋找相關 boundary truth（掃描範圍與 artifact 型別提示見 `assets/templates/discovery-sourcing.template.md` 內 **`Impact matrix`** 表頭說明）。**本步僅 READ / SEARCH，不授權任何 artifact 寫入。**

   - **1.4** 分支：掃描根下是否找得到可對照的契約／資料資產？
     - **否** → 後續 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`（步驟 3）**必須**明列「未找到」與預計補洞方式（可合理對應獨立功能／green-field）；**永遠不**以無法驗證的 repo 外私有筆記路徑充當 boundary truth 來源；**也不得**因此順手新建 contracts／data／shared／dsl／feature／activity 檔來「補洞」
     - **是** → 掃描結果於步驟 3 落入 discovery 報告表格欄位；**不在本步**塞長篇全文

2. CREATE one DIR: 在已鎖定 `$package_naming_language` 的前提下 DERIVE `$plan_package_slug`，建立 `${CURRENT_PLAN_PACKAGE}`（此步先不在 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下新建 `${TRUTH_FUNCTION_PACKAGE}`，除非本輪明確要新開 function package）。**若已在步驟 1.1 為取得路徑而執行過本步，本步改為 ASSERT 目錄已存在並跳過重複建立。** 然後到 argument.yml 中 更新 ${CURRENT_PLAN_PACKAGE} 參數。
  

3. WRITE FILE: 依 `assets/templates/discovery-sourcing.template.md` 寫入 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`（章節順序與 placeholder 以該檔為準）；填寫密度與敘事可對照 `assets/templates/discovery-sourcing.example.md`。同步更新 `${PLAN_SPEC}`：**保留**步驟 **1.2** 已寫入之需求全文；**追加** pointer 指向 `discovery-sourcing.md`（及必要錨點），並可補與 example 同一故事線的**執行摘要**句；**不重複**貼 `discovery-sourcing.md` 全文至 spec。**本步只允許 WRITE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 與 UPDATE `${PLAN_SPEC}`；不得動 boundary truth。**

4. THINK: 在已鎖定 `$package_naming_language` 的前提下拆解本次需求涉及幾個 **function package**（`1..*`）：**bottom-up 顆粒度規則**見 `01-sourcing-and-packaging/rules/function-package-granularity.md`。每個 `$function_package_slug` 必須在 `discovery-sourcing.md` 的 **`## Function package charters`** 有「職責一句、納入、排除、本輪變更型態」；拆法與反例語感見 `assets/templates/discovery-sourcing.example.md`，欄位義務見 `assets/templates/discovery-sourcing.template.md`。**本步只產出判斷結論，不授權寫任何新檔。**

5. CREATE DIRS ONLY: 在已鎖定 `$package_naming_language` 的前提下逐模組對照 boundary；若實作落在此 boundary，於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下建立或沿用 `${TRUTH_FUNCTION_PACKAGE}`，並**僅建立目錄骨架** `${ACTIVITIES_DIR}`、`${FEATURE_SPECS_DIR}` 讓路徑可解析。**不得**在本步建立或寫入任何 `dsl.yml`、`.feature`、`.activity`、contracts、data 或其他內容檔。**目錄樹示意**見 `assets/templates/discovery-sourcing.example.md` 內「Spec structure（示意樹）」

6. UPDATE FILE: 將上一步拆解與 charters 結論回寫 `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 與 `${PLAN_SPEC}`；`${PLAN_SPEC}` 須維持步驟 **1.2** 的需求全文與本步更新後的 pointer／執行摘要；句型仍對齊 `assets/templates/discovery-sourcing.example.md`。**本步只允許 UPDATE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 與 `${PLAN_SPEC}`；其他 artifact 一律禁止變更。**
