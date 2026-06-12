# WRITEBACK：本輪新增／改寫之 `.activity` → `${IMPACT_MATRIX_YML}`

1. FOR EACH SOP 步驟 6 **本輪新建**之 `.activity`（缺檔而由 `/aibdd-form-activity` 新落檔者）：TRIGGER `upsert`。
   - `path`：指向該 `.activity`、且**相對 `${TRUTH_BOUNDARY_ROOT}`** 之路徑，即 `packages/<NN-slug>/activities/<activity_relpath>`（`${ACTIVITIES_DIR}` 去除 `${TRUTH_BOUNDARY_ROOT}` 前綴後之形態）。**禁止 glob**；不含 repo 外路徑。
   - `change_type`：`add`（本輪新增之 UAT flow 活動圖）。
   - `impact_summary`：現在式一句話，描述該 flow 的業務旅程（對齊其 `summary_one_line`）。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
     --matrix ${IMPACT_MATRIX_YML} upsert \
     --path <path> --change-type add --impact-summary "<summary>"
   ```
2. FOR EACH SOP 步驟 6 以 `mode="overwrite"` **改寫**之既有 `.activity`：TRIGGER `upsert`（`change_type` 取 `update`；同 path 覆寫既有 entry，不會新增第二列）。檔在 plan 前已存在者為 `update`；本 plan 先前批次新增者維持 `add`（語意基準＝相對 plan 前 baseline）。
3. 本輪僅 READ／未改寫之既有 `.activity` **不**在此步——其已由 Phase 01（`01-sourcing-and-packaging` 依掃描、或 `01-amending-and-repackaging` 依全批次淨需求重推）寫入對應 entry。步驟 6 DELETE 之 `$OBSOLETE_ACTIVITIES` 亦**不**在此步：其 `remove` entry（plan 前既存者）由 Phase 01 寫入並保留為刪除紀錄；plan 內新增後取消者之 entry 已由 Phase 01 reconcile 收斂。
4. TRIGGER `validate`；`ok` 為 false 時依 `questions` 修正後重跑 `upsert`／`validate`，**不得**改寫 YAML 本體繞過 validator。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
     --matrix ${IMPACT_MATRIX_YML} validate
   ```
5. 完成後，matrix 中本輪所有新 `.activity` 之 `add` entry 之 `path` 與磁碟上實際落檔之 `.activity` **逐字一致**。此為本輪 activity `add` entry 的**唯一**產生點。
