# 設定
1. 後端專案的 `**.dsl.yml` 主要放在 `${CONTRACTS_DIR}`、`${DATA_DIR}`、`${BOUNDARY_SHARED_DSL}` 之中，這三者路徑來自於 arguments resolve 之結果。

# 指令

請參考底下指令來善用 dsl_cli query 來找到該 step format 的候選 DSL。
```bash
    uv run .claude/skills/aibdd-core/scripts/cli/dsl_cli.py query \
    --step-text "<Gherkin 步驟文案>" \
    --handler <handler-a> \
    --handler <handler-b> \
    --dsl ${CONTRACTS_DIR}/*.dsl.yml \
    --dsl ${DATA_DIR}/*.dsl.yml \
    --shared-dsl ${BOUNDARY_SHARED_DSL} \
    --source-scope all
```

