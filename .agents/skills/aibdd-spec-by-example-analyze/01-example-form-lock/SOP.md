# SOP

緣由：先把 Feature File 中每條 rules 的 Gherkin 骨架先決定好，並且鎖死在 `.feature` 內，後續 handler retrieval／DSL arrangement 步驟只需要延續此決策即可。

0. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   BOUNDARY_YML=${BOUNDARY_YML}
   EOF
   ```

1. READ boundary type profile
   1. PARSE `${BOUNDARY_YML}` 之 `type` 欄位為 `$boundary_type`（同 `/aibdd-plan` bind-and-load 步驟 3）。若此欄位不存在 → STOP 並報錯。

2. USE `${SCOPED_FEATURE_PATHS}` as bound impacted feature file scope
   1. `${SCOPED_FEATURE_PATHS}` 由頂層 SOP 步驟 1 綁定。
   2. 若 `${SCOPED_FEATURE_PATHS}` 為空 → STOP 並報錯。

3. TRIGGER form-lock apply script：
    1. 執行此 script:
        ```bash
        python3 .claude/skills/aibdd-spec-by-example-analyze/01-example-form-lock/scripts/cli/apply_form_lock.py \
            ${SCOPED_FEATURE_PATHS} \
            --boundary-yml "${BOUNDARY_YML}"
        ```
        1. INPUTS
            1. `${SCOPED_FEATURE_PATHS}`：步驟 2 列出的 `.feature` 路徑清單。
            2. `--boundary-yml`：active boundary 來源。
        2. OUTCOME
            1. 指定 `.feature` 原地改寫；未 lock 的 `Rule` 會插入 Example skeleton。
            2. stdout 回傳 JSON report，內含 `changed_count`、`feature_count`、`changed_features`、`questions`、`report.summary`。
    2. 若 $questions 非空：針對 $questions DELEGATE `/clarify-loop` 提問來修正錯誤，若錯誤判斷都修正完畢之後，則重複執行 3.1。