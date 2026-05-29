# SOP

上一步已在 `Given` / `Then` 的每個 `# @dsl` block 補齊 `# candidates:`，並已在 feature level 決定 `When` DSL format。

本步針對每個 feature 內 `Given` 和 `Then` 區塊做出基礎編排。


1. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
      CONTRACTS_DIR=${CONTRACTS_DIR}
      DATA_DIR=${DATA_DIR}
      BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
      EOF
      ```

2. USE `${SCOPED_FEATURE_PATHS}` as bound impacted feature file scope。
      1. `${SCOPED_FEATURE_PATHS}` 由頂層 SOP 步驟 1 綁定。
      2. 若 `${SCOPED_FEATURE_PATHS}` 為空 → STOP 並報錯。

3. [LOOP] FOR EACH `${SCOPED_FEATURE_PATHS}` 內每個 `.feature`：
    1. READ 該 `.feature` 全文。
    2. TRIGGER 一個 faithful reasoning worker（可用 sub-agent；粒度固定為一個 feature 一個 worker），只處理當前 `.feature`，此 worker 將嚴格執行：`steps/dsl-arrangement.md`
    3. worker 成功完成時的唯一授權 side effect：原地改寫當前 `.feature` 內的 placeholder `# @dsl` block。
    4. worker 若回傳 `$questions`，視為該 `.feature` 尚未完成；外層 phase 不得採納該 worker 的完成宣告。

4. WAIT 所有 feature workers 完成。
    1. COLLECT 全部 worker 回傳的 `$questions`。
    2. 若 `$questions` 為空：本 phase 完成。
    3. 若 `$questions` 非空：按 feature 維度 merge / dedupe 成批次 clarify payload，DELEGATE `/clarify-loop`。
    4. WAIT clarify 結果，然後只重跑受影響的 feature worker。
    5. 回到步驟 4.1，直到 `$questions` 為空才可離開本 phase。