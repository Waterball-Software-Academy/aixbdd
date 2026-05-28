
1. [LOOP] FOR EACH 步驟 1 列出的 `.feature`，RESOLVE feature-level When DSL：
   1. READ 該 `.feature` 全文。
   2. QUERY DSL catalog 中 `handler = operation-invoke` 之 entries，掃描 `${CONTRACTS_DIR}/*.dsl.yml`、`${DATA_DIR}/*.dsl.yml` 與 `${BOUNDARY_SHARED_DSL}`。
   3. 依該 feature 的主 use case 與各 `When <dsl>` placeholder 所共享的操作語意，DECIDE 一個 `selected_when_format`。
   4. `selected_when_format` 只決定 step format；參數 placeholder 原樣保留，不做 binding，不產 `# candidates:`，也不新增 rule-level `When` metadata。
   5. 若無法唯一決定：組成 `$questions`，直接 DELEGATE `/clarify-loop` 提問來修正當前 feature 所需資訊；修正完成後重複執行本步驟。

2. [LOOP] FOR EACH 已 resolve `selected_when_format` 之 `.feature`，TRIGGER when-format apply script：
   1. 執行此 script:
      ```bash
      python3 .claude/skills/aibdd-spec-by-example-analyze/02-handler-retrieval/scripts/cli/apply_when_format.py \
          <feature_path> \
          --format "<selected_when_format>"
      ```
      1. INPUTS
         1. `<feature_path>`：當前 feature 路徑。
         2. `--format`：步驟 3 決定之 `selected_when_format`。
      2. OUTCOME
         1. 指定 `.feature` 原地改寫；每個 `When <dsl>` 由 script 替換為 `When <selected_when_format>`。
         2. script 不得改 `Given` / `Then`，也不得修改 format 內的參數 placeholder。
         3. stdout 回傳 JSON report，內含 `changed_count`、`feature_count`、`changed_features`、`updated_when_count`、`questions`、`report.summary`。
   2. 若 $questions 非空：針對 $questions DELEGATE `/clarify-loop` 提問來修正錯誤。
