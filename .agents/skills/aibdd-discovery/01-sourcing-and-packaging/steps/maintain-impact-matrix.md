# MAINTAIN `${IMPACT_MATRIX_YML}` via wrapper

1. 為什麼用 wrapper
   1. `${IMPACT_MATRIX_YML}` 是本輪「哪些 boundary 規格檔會被 impact、怎麼 impact」的機讀 SSOT；下游 `/aibdd-plan`、`/aibdd-spec-by-example-analyze` 用 `query` 讀 `entries`，不再 parse markdown。
   2. 逐檔 explicit path、封閉 `change_type` enum、禁止 glob、禁止重複 path 等 invariant 由 `scripts/assets/impact-matrix.schema.yml` 與 validator 強制；手改 YAML 容易漏欄位或寫非法 enum，會讓下游 scope 綁定 silently 錯誤。
   3. 因此 discovery 階段維護 impact entries 的唯一合法路徑是 `manage_impact_matrix.py` 的 `init`、`upsert`、`delete`、`validate`、`query`；本 substep 在 discovery 寫入階段只用 `init`、`upsert`、`validate`。

2. wrapper 使用規範
   1. 固定流程：`init`（本輪 matrix 尚不存在時）→ 對 scope 內每一 impacted 檔各跑一次 `upsert` → 最後一次 `validate`。
   2. 一檔一 entry：每次 `upsert` 只寫一個 `path`；同一 path 再 `upsert` 會覆寫，不會新增第二列。
   3. 讀 stdout JSON：`ok`、`questions`、`entries` 是是否繼續的唯一依據；`validate` 的 `ok` 為 false 時，依 `questions` 修正後重跑 `upsert`／`validate`，不得改寫 YAML 本體繞過 validator。
   4. `path` 一律相對 `${TRUTH_BOUNDARY_ROOT}`，不含 repo 外路徑；禁止 glob（`*.feature` 等）。
   5. `impact_summary` 用現在式一句話說明本輪對該檔的規格增量或對照目的，供 human review 與後續 reconcile；不寫 implementation 步驟。

3. 本步 scope：哪些檔要寫 entry
   1. 依上層 SOP 步驟 1.3 掃描結果，凡本輪 discovery 會 impact、對照、或條件式可能改動的 boundary truth 規格檔，各寫一筆 entry。典型包含 `${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`、`${TRUTH_BOUNDARY_PACKAGES_DIR}/**` 下之 `.feature`、`dsl.yml` 等已存在或本輪將被規格化指向的檔案。
   2. 每一個本輪會動到的 `${FEATURE_SPECS_DIR}` 下 `.feature` 必須有 entry。
   3. 不寫入 entry 的範圍：plan-side artifacts（`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}`、`${IMPACT_MATRIX_YML}` 本身）、`${TRUTH_BOUNDARY_ROOT}` 外的路徑、以及上層 SOP 步驟 1.4 尚未存在且本輪不打算新建內容的 placeholder 路徑。

4. `change_type` 怎麼選
   1. `read_only_compare`：檔已存在；本輪只 READ／對照既有規格界定邊界，不在本 plan package 內改寫該檔內容。`impact_summary` 寫「對照什麼、用來界定哪個邊界」。
   2. `update`：檔已存在；本輪規格上確定要更新該檔（feature rule、dbml 欄位、dsl 語彙等）。`impact_summary` 寫「確定要補／改什麼規格增量」。
   3. `add`：本輪會新增該 path 的規格內容（新 `.feature`、新契約段落等）；檔可能尚不存在，但 path 必須是將來要落地的 explicit 路徑，禁止用 glob 代替。`impact_summary` 寫「新增什麼規格責任」。
   4. `conditional_update`：是否改動取決於尚未鎖定的 sourcing 決策（常見：`contracts` 是否因 UI／API 外顯而必改）。`impact_summary` 必須寫清條件與兩側後果；若決策已在 `discovery-sourcing.md` 的 `Resolved sourcing decisions` 拍板，應改判為 `update` 或 `read_only_compare`，不要留模糊 conditional。

5. TRIGGER wrapper 子步驟
   1. `init`：`${IMPACT_MATRIX_YML}` 尚不存在時執行一次；已存在則略過。
      ```bash
      python3 .claude/skills/aibdd-discovery/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} init
      ```
   2. `upsert`：對步驟 3 scope 內每一 impacted 檔各執行一次；`change_type` 依步驟 4 選定。
      ```bash
      python3 .claude/skills/aibdd-discovery/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} upsert \
        --path <path> --change-type <change_type> --impact-summary "<summary>"
      ```
   3. `validate`：全部 `upsert` 完成後執行一次；`ok` 為 false 則回到 `upsert` 修正。
      ```bash
      python3 .claude/skills/aibdd-discovery/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} validate
      ```

6. downstream consumer／producer contract
   1. `/aibdd-plan`：`query --change-type update --change-type add --change-type conditional_update`，再受 `$PLAN_SCOPE`（current plan package + function package charters）過濾；`02-contracts-design` 可對本 phase 派生出的 `contracts/`、`data/` target paths 經 wrapper `upsert` 回寫 matrix。
   2. `/aibdd-spec-by-example-analyze`：`query --suffix .feature --change-type update --change-type add`，物化為 `${SCOPED_FEATURE_PATHS}`；不納入 `read_only_compare` 或 `conditional_update` 的 feature。
