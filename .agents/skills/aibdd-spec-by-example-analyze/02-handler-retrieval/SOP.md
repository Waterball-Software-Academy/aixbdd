# SOP

緣由：先把 `Given` / `Then` 的 `# @dsl` block 可選 DSL id 就地補齊，再獨立決定每個 feature 的 `When` DSL format，讓後續 DSL arrangement 只需在 `.feature` 內挑選與編排，不必再回頭掃整個 DSL catalog。

0. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
   EOF
   ```

1. USE `${SCOPED_FEATURE_PATHS}` as bound impacted feature file scope。
   1. `${SCOPED_FEATURE_PATHS}` 由頂層 SOP 步驟 1 綁定。
   2. 若 `${SCOPED_FEATURE_PATHS}` 為空 → STOP 並報錯。

2. 針對上述 `${SCOPED_FEATURE_PATHS}` -- EXECUTE this procedure `steps/list-handler-candidatesfor-given-and-then.md`

3. 針對上述 `${SCOPED_FEATURE_PATHS}` -- EXECUTE this procedure to apply dsl to when steps: `steps/apply-dsl-to-when-steps.md`
