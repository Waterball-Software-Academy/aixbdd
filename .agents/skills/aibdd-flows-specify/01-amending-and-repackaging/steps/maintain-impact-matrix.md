# MAINTAIN `${IMPACT_MATRIX_YML}` via wrapper（amend 模式）

1. 為什麼用 wrapper
   1. `${IMPACT_MATRIX_YML}` 是本輪「哪些 boundary 規格檔會被 impact、怎麼 impact」的機讀 SSOT；下游 `/aibdd-plan`、`/aibdd-spec-by-example-analyze` 用 `query` 讀 `entries`，不再 parse markdown。
   2. 逐檔 explicit path、封閉 `change_type` enum、禁止 glob、禁止重複 path 等 invariant 由 wrapper CLI 隨附之 schema（`impact-matrix.schema.yml`）與 validator 強制；手改 YAML 容易漏欄位或寫非法 enum，會讓下游 scope 綁定 silently 錯誤。
   3. 因此維護 impact entries 的唯一合法路徑是 `manage_impact_matrix.py` 的 `init`、`upsert`、`delete`、`validate`、`query`；本 substep 在 amend 階段用 `init`（僅補缺）、`upsert`（含 `change_type=remove`）、`delete`（reconcile 淘汰不在 `$desired_entries` 的 entry）、`validate`。

2. wrapper 使用規範（宣告式維護策略：每次都以全批次淨需求**重推**「本 plan 預期的完整 entry 集合」作為唯一目標狀態，再把 matrix **收斂**到該集合；不對既有 entries 做逐筆增量修補，也不追蹤歷次變更的差分）
   1. amend 固定流程：SNAPSHOT `$ENTRIES_BEFORE`（以 `list` 讀出收斂**前**的全量 entries，原樣 EMIT 給用戶）→ DERIVE `$desired_entries`（見步驟 3）→ `init`（僅當上層步驟 1.1 記錄 `$matrix_missing = true`）→ 對 `$desired_entries` 每一筆各跑一次 `upsert`（同 path 覆寫，change_type／impact_summary 以本次推論為準）→ 對「現存 matrix 中、不在 `$desired_entries`」的 entry 各跑一次 `delete` → `validate` → SNAPSHOT `$ENTRIES_AFTER`（收斂**後**的全量 entries，原樣 EMIT）。
   2. 一檔一 entry：每次 `upsert` 只寫一個 `path`；同一 path 再 `upsert` 會覆寫既有 entry（amend 改判 `change_type` 即藉此覆寫），不會新增第二列。
   3. 讀 stdout JSON：`ok`、`questions`、`entries` 是是否繼續的唯一依據；`validate` 的 `ok` 為 false 時，依 `questions` 修正後重跑 `upsert`／`validate`，不得改寫 YAML 本體繞過 validator。
   4. `path` 一律相對 `${TRUTH_BOUNDARY_ROOT}`，不含 repo 外路徑；禁止 glob（`*.feature` 等）。
   5. `impact_summary` 用現在式一句話說明本輪變更對該檔的規格增量或對照目的，供 human review 與後續 reconcile；不寫 implementation 步驟。
   6. 快照留存：`$ENTRIES_AFTER` 即現行 `${IMPACT_MATRIX_YML}`，遺失時可隨時 `list`／`query` 還原；`$ENTRIES_BEFORE` 僅以 EMIT 留在對話中、不另落檔，供同一 run 內的 Phase 02／03 取用。

3. DERIVE `$desired_entries`：本 plan 預期的完整 entry 集合
   1. 推論基準：以 `${PLAN_SPEC}` **所有批次**（001..NNN）合併後的**淨需求**，對照 plan 開始前的 boundary truth baseline，重推本 plan 對每一檔的影響——不是只看本次變更批次的差異。每檔一筆 `{path, change_type, impact_summary}`。
   2. 淨需求下已不影響的檔（先前批次曾納入、本次變更後不再動它）自然**不在** `$desired_entries`，reconcile 時其 entry 被 `delete`；plan 內新增又取消的檔同理（淨影響歸零，不留 entry）。
   3. 淘汰 **plan 前既存**的 truth 檔者，以 `change_type=remove` 留在 `$desired_entries`——刪除也是本 plan 的影響，必須留機讀紀錄；檔案刪除不在本步，由 Phase 02／03 依其明文 DELETE 授權執行。
   4. **不 forward-declare 本輪新增的 `.feature`／`.activity`（`add`）**：新 feature／activity 的 explicit 路徑必須由 Phase 02／03 萃取階段決定並 writeback 回 matrix，`$desired_entries` 不得在 Action 萃取前先猜檔名／路徑。此禁令**僅及尚未落檔的新檔**；**現存 matrix 的每一筆 entry（含先前輪由 Phase 02／03 writeback 寫入的 activity／feature entry）都必須被逐筆考量一遍**：仍屬淨需求者納入 `$desired_entries` 經 CLI `upsert` 覆寫（必要時改判 `change_type`、更新 `impact_summary`），不屬者由 CLI `delete` 收斂；**不得**以「該 entry 非本步寫入」為由跳過考量。
   5. 不納入 `$desired_entries` 的範圍：plan-side artifacts（`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}`、`${IMPACT_MATRIX_YML}` 本身）、`${TRUTH_BOUNDARY_ROOT}` 外的路徑、以及尚未存在且本輪不打算新建內容的 placeholder 路徑。

4. `change_type` 怎麼選（語意基準＝**本 plan 對該檔的影響、相對於 plan 開始前的 boundary truth baseline**，不是當下 filesystem 狀態）
   1. `read_only_compare`：檔在 plan 前已存在；本輪只 READ／對照既有規格界定邊界，不改寫該檔內容。`impact_summary` 寫「對照什麼、用來界定哪個邊界」。
   2. `update`：檔在 plan 前已存在；本輪變更確定要更新該檔（feature rule、dbml 欄位、dsl 語彙等）。`impact_summary` 寫「確定要補／改什麼規格增量」。
   3. `add`：該 path 的規格內容由**本 plan** 新增（不論初始批次或本次變更批次；檔可能尚不存在）；path 必須是將來要落地的 explicit 路徑，禁止用 glob 代替。`impact_summary` 寫「新增什麼規格責任」。
   4. `conditional_update`：是否改動取決於尚未鎖定的變更決策（常見：`contracts` 是否因 UI／API 外顯而必改）。`impact_summary` 必須寫清條件與兩側後果；若決策已在 `discovery-sourcing.md` 的 `Resolved sourcing decisions` 拍板，應改判為 `update` 或 `read_only_compare`，不要留模糊 conditional。
   5. `remove`：檔在 plan 前已存在；本輪變更明文淘汰該既存規格檔。`impact_summary` 寫「淘汰什麼、依據哪段需求原文」。
   6. 常見誤判防呆（皆為步驟 3.1 淨需求推論的自然結果，列出以供核對）：本 plan 自己新增的檔，重推後仍是 `add`，**不得**因「檔已存在於 filesystem」翻成 `update`；plan 內新增又取消的檔不在 `$desired_entries`（entry 被 reconcile 刪除），**不得**改判 `remove`——`remove` 僅用於 plan 前既存檔。

5. TRIGGER wrapper 子步驟
   1. `list`（SNAPSHOT `$ENTRIES_BEFORE`，收斂前執行一次）：
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} list
      ```
   2. `init`：僅當 `$matrix_missing = true`（上層步驟 1.1 補建情境）執行一次；matrix 已存在則略過。
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} init
      ```
   3. `upsert`：對 `$desired_entries` 每一筆各執行一次；`change_type` 依步驟 4 選定。
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} upsert \
        --path <path> --change-type <change_type> --impact-summary "<summary>"
      ```
   4. `delete`：對「現存 matrix 中、不在 `$desired_entries`」的每一 entry 各執行一次。
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} delete --path <path>
      ```
   5. `validate`：全部 `upsert`／`delete` 完成後執行一次；`ok` 為 false 則回到 `upsert` 修正。
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} validate
      ```
   6. `list`（SNAPSHOT `$ENTRIES_AFTER`，`validate` 通過後執行一次）：
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} list
      ```
