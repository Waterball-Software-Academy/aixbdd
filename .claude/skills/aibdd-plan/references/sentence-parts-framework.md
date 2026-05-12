# sentence-parts-framework（已廢止 — Tombstone）

**本檔已廢止，不再為 SSOT。**

`/aibdd-plan` DSL 合成時，`sentence_part`／`handler`／Gherkin `keyword` 對應的**唯一機械來源（SSOT）**為 boundary preset asset：

`.claude/skills/aibdd-core/assets/boundaries/web-backend/handler-routing.yml`

（`routes`：`sentence_part` + `keyword` + `handler` + `semantic`；`handlers`：`required_source_kinds`、`l4_requirements`。）

對應的 preset 級契約：`aibdd-core/references/preset-contract/web-backend.md`。

**禁止使用**：

- `SENTENCE_PARTS_FRAMEWORK_REF`（已自 `arguments.yml` 範本移除）
- 任何與上述 YAML 並行的「generic sentence parts framework」規則檔。

若文件或舊對話仍引用本檔內文的 Operations／States／Mock 敘事，視為過時指引；請以 `handler-routing.yml` 為準。
