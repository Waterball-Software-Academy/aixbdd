# 參數設定

- **產出錨點** → 同 SKILL.md **PRINCIPLE: CWD 為產出錨點**；下列 `${…}` 均錨定於 **`CWD`**。
- **implementation 根** → `${CURRENT_PLAN_PACKAGE}/implementation/`
- **sequence 目錄** → `${CURRENT_PLAN_PACKAGE}/implementation/sequences/`
- **internal-structure 檔** → `${CURRENT_PLAN_PACKAGE}/implementation/internal-structure.class.mmd`

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. **THINK：external boundary surface 模型**
   - **READ** `rules/external-surface-granularity.md`。
   - 對 `$BOUNDARY_DELTA.provider_edges` 之每條 edge **FAITHFUL REASONING**：每個 **provider boundary** 必有 contract reference 或顯式 non-contract 原因；每條 mockable consumer→provider edge 必有 test double policy；**禁止**把同 boundary 內部協作者列為 mock target；3rd-party providers 必有 external stub candidate（payload 與 response binding source）；行為依賴 provider failure 者必有 failure-mode anchor。
   - 輸出 `$EXTERNAL_SURFACE_MODEL`（含 `edges[]`、`stubs[]`、`failure_modes[]`）。本步**不寫檔**。

2. **THINK：實作路徑與內部結構**
   - **READ** `rules/sequence-path-granularity.md`。
   - 從 `$PLAN_INPUTS.activity_truth`／`$PLAN_INPUTS.feature_truth`／`$BOUNDARY_DELTA`／`$EXTERNAL_SURFACE_MODEL` **FAITHFUL REASONING** 萃取**主要實作路徑**：happy／alt／err **各為獨立路徑**；每條路徑必有可追溯之 activity flow／atomic rule／contract operation／dispatch decision 依據。
   - 輸出 `$IMPLEMENTATION_MODEL = { paths: [...], collaborators: [...] }`，每條 path 含 `scenario_slug`／`category`（`happy`|`alt`|`err`）／`actor`／`boundary_entry_operation`／`internal_collaborators[]`／`provider_calls[]`／`state_changes[]`／`response_verifier_candidates[]`／`source_refs`。

3. **CREATE：implementation 目錄骨架**
   - CREATE `${CURRENT_PLAN_PACKAGE}/implementation/`、`${CURRENT_PLAN_PACKAGE}/implementation/sequences/`。
   - 本步**只建目錄**，**不**預建空 `.mmd` 檔。

4. **WRITE FILES：sequence diagrams**
   - FOR EACH path in `$IMPLEMENTATION_MODEL.paths`：依 `<scenario_slug>.<category>.sequence.mmd` 寫入 `${CURRENT_PLAN_PACKAGE}/implementation/sequences/`，內容為 Mermaid sequence 圖。
   - 每張 sequence **必含**：actor、boundary entry operation、internal collaborators、provider contract calls、state changes、response verifier candidates。
   - **不得**把多條主要路徑塞同一 `.mmd`（違反 `rules/sequence-path-granularity.md`）；**不得**用 legacy 命名 `*.backend.sequence.mmd`。

5. **WRITE FILE：internal-structure.class.mmd**
   - 把 `$IMPLEMENTATION_MODEL.paths` 之**結構聯集**（所有 collaborators／operations／state surfaces）寫入 `${CURRENT_PLAN_PACKAGE}/implementation/internal-structure.class.mmd`，作為下游 `/aibdd-tasks` GREEN 階段定位類別／模組／operation 之依據。
   - **不得**含 product code patch、step definition 內容、test queue 狀態。

6. **ASSERT：路徑可追溯性**
   - 對每個 implementation target（actor／operation／collaborator／provider call／state change），ASSERT 至少能追溯到一條 activity path／atomic rule／provider contract／boundary-map dispatch override；
   - 任一 target 找不到追溯來源 → 在 `$IMPLEMENTATION_MODEL.blocked_reasons[]` 紀錄（含 target、原因），供 phase 05 之 `research.md` 之 `## Blocked Reasons` 顯式落地；**禁止**靜默忽略。
