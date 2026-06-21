### q4-codebase-layout
- prompt: 程式碼要放在 repo root 還是子目錄？
- kind: CON
- options: repo_root | subdir:<kebab-case-dir>
- recommendation: repo_root
- answer.raw: {{Q4_ANSWER}}
- resolved_decision: { key: boundary_codebase_subdir, value: {{BOUNDARY_CODEBASE_SUBDIR}} }
- status: {{Q4_STATUS}}

<!-- @guideline -->
決定程式碼與 `specs/` 的掛載點：
- `repo_root` — 全部掛在 repo root，`boundary_codebase_subdir = ""`。
- `subdir:<dir>` — 全部掛在 `${PROJECT_ROOT}/<dir>/`，`<dir>` 為 kebab-case 目錄名。

resolved 後 `boundary_codebase_subdir` 取 `""`（repo_root）或 `<dir>`（subdir）。選了 subdir 就**整套**掛進去——別把程式碼放子目錄卻把 `specs/` 留在 root，兩者必須同一掛載點。
reply token：`Q4: repo_root | subdir:<kebab-case-dir>`
