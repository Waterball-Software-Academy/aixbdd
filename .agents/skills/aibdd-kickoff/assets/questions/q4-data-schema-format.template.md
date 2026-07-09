### q4-data-schema-format
- prompt: 後端持久狀態的 data schema 要用哪種格式落地？
- kind: CON
- options: dbml | ddl:postgresql | ddl:mysql | ddl:mssql
- recommendation: dbml
- answer.raw: {{Q4_ANSWER}}
- resolved_decision: { key: data_schema_format, value: {{DATA_SCHEMA_FORMAT}} }
- status: {{Q4_STATUS}}

<!-- @guideline -->
**僅 `type: web-service` 的 boundary 詢問**（stack = `python_e2e` / `java_e2e`）。其他 type（如 `nextjs_playwright` 的 `web-app`）的 state_specifier 非 persistent，**不問本題**，`data_schema_format = n/a`。

決定 `state_specifier` 怎麼落 `${DATA_DIR}`：
- `dbml` — 採 web-service base preset 的 `state_specifier`（`/aibdd-form-entity-spec`，format `dbml`，`domain.dbml`）。**不寫** `boundary.yml` 的 `profile_overrides`，沿用 base。
- `ddl:<dialect>` — 改用 `/aibdd-form-ddl-spec`；`state_specifier.format` = dialect（`postgresql` / `mysql` / `mssql`）。Phase 4 把整塊 `profile_overrides.state_specifier` 寫進 `boundary.yml`。format ↔ default_filename：

| Q4 選項 | data_schema_format（寫入 kickoff-plan） | boundary `format` | default_filename |
|---|---|---|---|
| `ddl:postgresql` | `postgresql` | `postgresql` | `domain.pg.sql` |
| `ddl:mysql` | `mysql` | `mysql` | `domain.mysql.sql` |
| `ddl:mssql` | `mssql` | `mssql` | `domain.mssql.sql` |

resolved 後 `data_schema_format` ∈ `dbml` / `postgresql` / `mysql` / `mssql` / `n/a`（非 web-service 為 `n/a`）。

答非四個 option 之一、或 web-service 卻未答 → 標 unresolved 重問，不要自行猜值。
reply token：`Q4: dbml | ddl:postgresql | ddl:mysql | ddl:mssql`
