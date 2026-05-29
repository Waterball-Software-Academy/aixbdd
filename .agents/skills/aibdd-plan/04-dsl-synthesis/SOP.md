# SOP

緣由：實作計畫就緒後，用 `dsl_cli` 把 `${CONTRACTS_DIR}` / `${DATA_DIR}` 下的 spec 自動展開為 DSL skeleton（HARNESS），再由 AI 業務化填字（SEMANTIC），最後跑 universal eval（HARNESS）。本 phase 不再以 per-rule 迭代產生 entry — `dsl_cli` 由 part-driven 自動 fan-out，落到 `${CONTRACTS_DIR}/<resource>.dsl.yml` / `${DATA_DIR}/<file>.dsl.yml`。

0. **RESOLVE arguments** —— 透過 sibling resolver 綁定變數，把 stdout 之 `KEY=value` 原樣 EMIT 給用戶；resolver 非 0 退出 → 停止 SOP 並把 stderr 透傳。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   BOUNDARY_YML=${BOUNDARY_YML}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
   DSL_KEY_LOCALE=${DSL_KEY_LOCALE}
   EOF
   ```

1. DERIVE `${DSL_KEY_LOCALE}` — 依 `steps/dsl-key-locale.md` 執行。

2. READ boundary preset name — 依 `steps/boundary-preset.md` 取出 `<boundary>`（即 `${BOUNDARY_YML}` 內活動 boundary 之 `type`）。

3. **(HARNESS) RUN** `dsl_cli generate-dsl-instructions`：

   ```bash
   uv run .claude/skills/aibdd-core/scripts/cli/dsl_cli.py generate-dsl-instructions \
     --boundary <boundary> \
     --specs ${CONTRACTS_DIR}/*.api.yml ${DATA_DIR}/*.dbml \
     --dsl ${CONTRACTS_DIR}/*.dsl.yml ${DATA_DIR}/*.dsl.yml
   ```

   - dsl_cli 會依副檔名 dispatch 對應 spec_parser，取得所有 parts，與既有 `*.dsl.yml` 內 entry 之 `target_part_path` 做 prefix-match diff，把未 resolved 之 part 餵給 active boundary 之 part_to_dsl plugin (`assets/boundaries/<boundary>/scripts/part_to_dsl.py`) 取得 template skeleton，依 part 來源 spec 路由到對應 `*.dsl.yml`（`<spec>.api.yml` → `<spec>.dsl.yml`、`<file>.dbml` → `<file>.dsl.yml`），append。
   - 命令 idempotent — 已 resolved 之 part 不再產出 skeleton。
   - 命令印出 `GenerationReport`（新增 entries 數量、各寫到哪個檔）。

4. **(SEMANTIC) LOOP** per skeleton entry 其 `format` 仍為 `"<FILL IN>"`（順序：依 entry 在檔案中之出現順序、跨檔依檔名字典序）：

   4.1 READ 該 entry 之 `target_part_path` 所指 spec 節點原文（OpenAPI operation / DBML table 等），辨識業務 actor / operation / object。

   4.2 **Candidate block 處理**：從 skeleton 的「候選參數註解區塊」逐條決定該 candidate 進 `param_bindings`（必要、會出現在 format 中）或 `datatable_bindings`（可選 / 走 DataTable）；改 binding key 為業務術語（依 `${DSL_KEY_LOCALE}`），binding 的 `target` 路徑**原樣帶過**，禁止修改。

   **預填 `datatable_bindings` 改名**：plugin 在 HARNESS 階段可能已直接預填部分 `datatable_bindings`。這些 key 預設以 raw spec 欄位名稱填入。SEMANTIC 須逐一審視已預填的 key，依 `${DSL_KEY_LOCALE}` 規則改名為業務術語（若名稱已符合慣例可保留）；`target` 路徑同樣**原樣帶過**，禁止修改。

   4.3 寫入 `format` 業務句（actor-operation-object 句型，遵 `aibdd-core::references/sentence-parts-framework/default.md`）；引用 binding key 用 `{key}` 占位。

   4.4 刪除 skeleton 中所有 plugin 寫入之候選參數註解區塊與 `<FILL IN>` 占位；若 `datatable_bindings` 仍為空，明確寫成 `{}`（不可留空 block 或殘留註解）。

   4.5 SEMANTIC 對該 entry 之**禁止項**：不得改動 `handler`、`target_part_path`、`name`、binding 之 `target`、`source_spec_path`。這些 plugin 持有的 spec ↔ DSL 對應關係不容 SEMANTIC 重新詮釋。

5. **(HARNESS) RUN** `dsl_cli eval`：

   ```bash
   uv run .claude/skills/aibdd-core/scripts/cli/dsl_cli.py eval \
     --dsl ${CONTRACTS_DIR}/*.dsl.yml ${DATA_DIR}/*.dsl.yml \
     --shared-dsl ${BOUNDARY_SHARED_DSL}
   ```

   套用 7 條 universal rules：

   - `format-params-cap` — format 句型內 `{key}` 數量 ≤ 3
   - `datatable-cap` — datatable_bindings 中 required:true 且無 default_value 之欄位數 ≤ 6
   - `schema-completeness` — 必要欄不為空 / `<FILL IN>`
   - `name-uniqueness` — entry `name` 跨所有 `--dsl` 與 `--shared-dsl` 唯一
   - `format-key-binding-bijection` — format 內 `{key}` ⇔ `param_bindings` 之 key 雙向覆蓋
   - `target-uri-scheme-validity` — 每個 binding 的 `target` 須命中 5 種 scheme 之一（Spec anchor / `response:` / `literal:` / `stub_payload:` / DBML anchor）
   - `residual-candidate-comment-block` — 不得殘留 skeleton 生成的 `# 候選參數...` 註解區塊

   FAIL → 列每條 violation 的 `entry_name` / `rule_id` / `message` / `hint` → 回步驟 4 修；常見修法包含補 `default_value` 把 required datatable 降為 optional 以紓壓 `datatable-cap`、或拆分 entry 以紓壓 `format-params-cap`。

   PASS → SOP 結束。

---

**遷移備註**：本 SOP 之前版本（commit 99d7149 之前）採 per-rule 迭代搭配 `${BOUNDARY_PACKAGE_DSL}`（function-package 內 dsl.yml）與 `scripts/dsl-cli/run.py search/verify`。該流已不再使用 — dsl.yml 已遷出 function package 落到 contracts/data 同目錄；entry schema 已從 4 層巢狀改成扁平。schema 細節以 `experiemented-skills/aibdd-plan/04-dsl-synthesis/rules/01-dsl-entry-schema.md` 內之 deprecation pointer 為準。
