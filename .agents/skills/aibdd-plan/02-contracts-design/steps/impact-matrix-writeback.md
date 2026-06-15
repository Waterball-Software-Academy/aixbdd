1. FOR EACH 步驟 2 之 contract `slice.target_path`：TRIGGER `upsert`，`path` 為 `contracts/<target_path>`（相對 `${TRUTH_BOUNDARY_ROOT}`）；`change_type` 依下列規則選一個：
    1. 檔已存在且 plan 確定改寫 → `update`
    2. 新 target_path → `add`
    3. 仍待 sourcing 決策才能落地 → `conditional_update`
    `impact_summary` 用現在式一句話描述本 phase 對該契約檔的規格增量。
2. FOR EACH 步驟 4 之 state `target_path`：TRIGGER `upsert`，`path` 為 `data/<target_path>`（相對 `${TRUTH_BOUNDARY_ROOT}`）；`change_type` 規則同上。
    ```bash
    python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
    --matrix ${IMPACT_MATRIX_YML} upsert \
    --path <path> --change-type <change_type> --impact-summary "<summary>"
    ```
3. TRIGGER `validate`；`ok` 為 false 時依 `questions` 修正後重跑 `upsert`／`validate`。
    ```bash
    python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
    --matrix ${IMPACT_MATRIX_YML} validate
    ```