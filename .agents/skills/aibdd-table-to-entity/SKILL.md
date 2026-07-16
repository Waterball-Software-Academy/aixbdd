---
name: aibdd-table-to-entity
description: Build the entity-to-table mapping (`entity_to_table_mapping.yml`) from a boundary's physical schema specs (DBML / SQL DDL), preserving existing entity names and naming new tables from the plan spec.
metadata:
  user-invocable: true
  source: project-level
---

# 目的

從 schema 規格（DBML 或 SQL DDL）抽出 table 名，依資料夾在 `${DATA_DIR}` 樹下各自產出 `entity_to_table_mapping.yml`，作為 spectrum 框架使用的檔案。

`${DATA_DIR}` 底下每個直接含 schema 檔的資料夾（含 `${DATA_DIR}` 外層本身、以及 primary／secondary 等子資料夾）各自產出一份只涵蓋該層直屬 schema 檔的 `entity_to_table_mapping.yml`；外層只在自己直屬有 schema 檔時才產出，子資料夾扛全部 schema 時外層不產出。唯一例外：整個 `${DATA_DIR}` 完全沒有 schema 檔時，外層仍產出一份空 list（保留尚無 data 契約）。同一資料夾跨檔同名 table 會被拒絕，不同資料夾則可並存。

產出是增量的：既有 `entity_to_table_mapping.yml` 裡的 entity name 是真相，重跑時原樣保留，只為既有 mapping 尚未涵蓋的新 table 補命名。同一 table 若已有多筆 entity name（例如一個 table 同時被不同 entity 別名指涉），每一筆都原樣保留，不因重跑而合併或丟失。新 table 的 entity name 依 `${PLAN_SPEC}` 的需求敘事推論；需求敘事找不到對應依據時，退回以 `<子資料夾名>_<table名>` 命名。

schema 檔只認 `.dbml`、`.mysql.sql`、`.pg.sql`、`.mssql.sql` 四種副檔名；其他副檔名的檔案不進命名 worklist，由 plan 以 ignored_files 顯式回報而非默默略過。不含支援 schema 檔的資料夾若已存在 `entity_to_table_mapping.yml`（例如由不支援的 schema 方言人工轉換而來），該檔視為 foreign mapping：嚴禁改寫，但其 entity name 仍佔用全域命名空間。

table name 跨資料夾可重複（不同資料庫可各有同名 table），但 entity name 必須全域唯一，foreign mapping 已佔用的 entity name 也算在內。跨資料夾出現重複 entity name 時須向使用者確認改名，並以 `<子資料夾名>_<table名>` 作為建議選項。

# SOP

1. 綁定 arguments: EXECUTE command 執行 sibling resolver 綁定 `$DATA_DIR` 與 `$PLAN_SPEC`，對使用者輸出其 `KEY=value` stdout；若 command 失敗 則 STOP 並對使用者輸出 stderr。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   DATA_DIR=${DATA_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   EOF
   ```

2. 取回命名 worklist: EXECUTE command `build_mapping.py plan "$DATA_DIR"` 作為 $WORKLIST，其 stdout 之 JSON 每個 folder 帶已保留 existing entry 與待命名 new_tables，另帶不改寫但佔用 entity name 的 foreign_mappings 與被忽略的 ignored_files；若 ignored_files 非空 則對使用者輸出該清單；若 command 失敗 則 STOP 並對使用者輸出 stderr。

   ```bash
   uv run .claude/skills/aibdd-table-to-entity/scripts/build_mapping.py plan "${DATA_DIR}"
   ```

3. 命名新 table: 對 $WORKLIST 每個 folder 的每個 new_table，參考 `$PLAN_SPEC` REASONING 其 entity name；需求敘事找不到對應依據則設其 entity name 為 `<folder>_<table名>`。把每個 folder 的 { table: entity } 決議整體綁為 $NAMING。

4. 消解全域 entity 撞名: 對 $NAMING 中與其他 folder 或 $WORKLIST foreign_mappings 產生相同 entity name 的 table，DELEGATE /clarify-loop 向使用者確認改名並附 `<folder>_<table名>` 作為建議選項，依結論 UPDATE $NAMING，重複至 $NAMING 內 entity name 全域唯一。

5. 自查全域唯一: ASSERT $NAMING 併入 $WORKLIST 各 folder existing entry 與 foreign_mappings 各 entity 後，所有 entity name 全域唯一，否則回到步驟 4 重新消解。

6. 落檔 mapping: EXECUTE command `build_mapping.py apply "$DATA_DIR"`，把 $NAMING 序列化為 { folder: { table: entity } } 形狀的 JSON 從 stdin 交付，依資料夾各自落檔 `entity_to_table_mapping.yml`，對使用者輸出其 stdout/stderr；若 command 因 entity name 撞名而失敗 則 依其 stderr 列出的衝突回到步驟 4 重新消解後重試直到成功。

   ```bash
   printf '%s' "$NAMING_JSON" | uv run .claude/skills/aibdd-table-to-entity/scripts/build_mapping.py apply "${DATA_DIR}"
   ```
