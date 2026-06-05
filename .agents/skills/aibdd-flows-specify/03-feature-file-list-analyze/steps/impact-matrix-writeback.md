# WRITEBACK：本輪新增之 `.feature` → `${IMPACT_MATRIX_YML}`

1. FOR EACH SOP 步驟 1 **本輪新建**之 `.feature`（缺檔而新建者；既有未改寫之 `.feature` **不**在此步——其已由 `01-sourcing-and-packaging` 依掃描寫入對應 entry）：TRIGGER `upsert`。
   - `path`：指向**與其 `binds_feature` 同一檔案**、且**相對 `${TRUTH_BOUNDARY_ROOT}`** 之路徑，即 `packages/<NN-slug>/features/<NN>-<action-slug>.feature`（`${FEATURE_SPECS_DIR}` 去除 `${TRUTH_BOUNDARY_ROOT}` 前綴後之形態）。**禁止 glob**；不含 repo 外路徑。
   - `change_type`：`add`（本輪新增之 rule-less feature 骨架）。
   - `impact_summary`：現在式一句話，描述該 feature 的業務意圖／本輪新增之規格責任（對齊其對應 Action）。
   ```bash
   python3 .claude/skills/aibdd-flows-specify/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
     --matrix ${IMPACT_MATRIX_YML} upsert \
     --path <path> --change-type add --impact-summary "<summary>"
   ```
2. TRIGGER `validate`；`ok` 為 false 時依 `questions` 修正後重跑 `upsert`／`validate`，**不得**改寫 YAML 本體繞過 validator。
   ```bash
   python3 .claude/skills/aibdd-flows-specify/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
     --matrix ${IMPACT_MATRIX_YML} validate
   ```
3. 完成後，matrix 中本輪所有新 `.feature` 之 `add` entry 之 `path` 與磁碟上實際落檔之 `.feature` **逐字一致**。
