1. FOR EACH 步驟 8 之 contract `slice.target_path`：TRIGGER `upsert`，`path` 為 `contracts/<target_path>`（相對 `${TRUTH_BOUNDARY_ROOT}`）；`change_type` 依下列規則選一個：
    1. 檔已存在且 plan 確定改寫 → `update`
    2. 新 target_path → `add`
    3. 仍待 sourcing 決策才能落地 → `conditional_update`
    `impact_summary` 用現在式一句話描述本 skill 對該契約檔的規格增量。
    ```bash
    python3 .claude/skills/aibdd-flows-specify/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
    --matrix ${IMPACT_MATRIX_YML} upsert \
    --path <path> --change-type <change_type> --impact-summary "<summary>"
    ```
2. TRIGGER `validate`；`ok` 為 false 時依 `questions` 修正後重跑 `upsert`／`validate`。
    ```bash
    python3 .claude/skills/aibdd-flows-specify/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
    --matrix ${IMPACT_MATRIX_YML} validate
    ```
