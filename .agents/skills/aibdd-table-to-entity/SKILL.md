---
name: aibdd-table-to-entity
description: Build the entity-to-table mapping (`entity_to_table_mapping.yml`) from a boundary's physical schema specs (DBML / SQL DDL) — identity mapping.
metadata:
  user-invocable: true
  source: project-level
---

# 目的

從 schema 規格（DBML 或 SQL DDL）抽出 table 名，產出 `${DATA_DIR}/entity_to_table_mapping.yml`，作為 spectrum 框架使用的檔案。

entity to table mapping（`<isa-entity>` = `<table_name>`），不讀 Table Note／DDL 表級註解。

# SOP

1. RESOLVE arguments — 透過 sibling resolver 綁定變數，把 stdout 之 `KEY=value` 原樣 EMIT 給用戶；resolver 非 0 退出 → 停止 SOP 並把 stderr 透傳。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   DATA_DIR=${DATA_DIR}
   EOF
   ```

2. EXECUTE `build_mapping.py` — 直接執行 sibling script 產出 `${DATA_DIR}/entity_to_table_mapping.yml`；stdout/stderr 原樣 EMIT 給用戶，非 0 退出即 STOP。

   ```bash
   uv run .claude/skills/aibdd-table-to-entity/scripts/build_mapping.py "${DATA_DIR}"
   ```
