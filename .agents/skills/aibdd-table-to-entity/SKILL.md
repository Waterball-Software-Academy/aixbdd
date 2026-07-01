---
name: aibdd-table-to-entity
description: Build the entity-to-table mapping (`entity_to_table_mapping.yml`) from a boundary's physical schema specs (DBML / SQL DDL) — identity mapping.
metadata:
  user-invocable: true
  source: project-level
---

# 目的

從 schema 規格（DBML 或 SQL DDL）抽出 table 名，依資料夾各自產出 `entity_to_table_mapping.yml`，作為 spectrum 框架使用的檔案。

`${DATA_DIR}` 底下每個「直接」含 schema 檔的資料夾（含 `${DATA_DIR}` 外層本身、以及 primary／secondary 等子資料夾）各自產出一份只涵蓋該層直屬 schema 檔的 `entity_to_table_mapping.yml`；外層只在自己直屬有 schema 檔時才產出，子資料夾扛全部 schema 時外層不產出。唯一例外：整個 `${DATA_DIR}` 完全沒有 schema 檔時，外層仍產出一份空 list（保留「尚無 data」契約）。同一資料夾跨檔同名 table 會被拒絕，不同資料夾則可並存。

entity to table mapping（`<isa-entity>` = `<table_name>`），不讀 Table Note／DDL 表級註解。

# SOP

1. RESOLVE arguments — 透過 sibling resolver 綁定變數，把 stdout 之 `KEY=value` 原樣 EMIT 給用戶；resolver 非 0 退出 → 停止 SOP 並把 stderr 透傳。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   DATA_DIR=${DATA_DIR}
   EOF
   ```

2. EXECUTE `build_mapping.py` — 直接執行 sibling script，依資料夾在 `${DATA_DIR}` 樹下各自產出 `entity_to_table_mapping.yml`；stdout/stderr 原樣 EMIT 給用戶，非 0 退出即 STOP。

   ```bash
   uv run .claude/skills/aibdd-table-to-entity/scripts/build_mapping.py "${DATA_DIR}"
   ```
