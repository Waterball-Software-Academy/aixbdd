TRIGGER handler-candidate apply script：
   1. 執行此 script:
      ```bash
      python3 .claude/skills/aibdd-spec-by-example-analyze/02-handler-retrieval/scripts/cli/apply_handler_candidates.py \
          ${SCOPED_FEATURE_PATHS} \
          --contracts-dir "${CONTRACTS_DIR}" \
          --data-dir "${DATA_DIR}" \
          --shared-dsl "${BOUNDARY_SHARED_DSL}"
      ```
      1. INPUTS
         1. `${SCOPED_FEATURE_PATHS}`：步驟 1 列出的 `.feature` 路徑清單。
         2. `--contracts-dir`：contract DSL 目錄（`${CONTRACTS_DIR}`）。
         3. `--data-dir`：data DSL 目錄（`${DATA_DIR}`）。
         4. `--shared-dsl`：boundary shared DSL 路徑（`${BOUNDARY_SHARED_DSL}`）。
      2. OUTCOME
         1. 指定 `.feature` 原地改寫；每個 `# @dsl` block 的 `# candidates:` 區塊由 script enrich。
         2. stdout 回傳 JSON report，內含 `changed_count`、`feature_count`、`changed_features`、`updated_block_count`、`questions`、`report.summary`。
   2. 若 $questions 非空：針對 $questions DELEGATE `/clarify-loop` 提問來修正錯誤，若錯誤判斷都修正完畢之後，則重複執行 2.1。