---
name: aibdd-isa-init
description: >
  為 SpecFormula／SF eval 與 dsl_to_isa 管線預備 ISA 執行契約與 entity 查表骨架：綁定 arguments、
  將 boundary state specifier 切換為 DDL dialect、寫入預設 `${CONTRACTS_DIR}/isa.yml` 與空
  `${DATA_DIR}/entity_to_table_mapping.yml`。
  TRIGGER when 使用者下 /aibdd-isa-init、SF eval 前缺 isa 前置、或 boundary 需改為 DDL state。
  SKIP when 尚未 `/aibdd-kickoff`（缺 `${AIBDD_ARGUMENTS_PATH}` 或 `${BOUNDARY_YML}`）、
  或僅要跑 `/aibdd-dsl-to-isa-interpretation` 且兩份前置檔已存在。
metadata:
  user-invocable: true
  source: project-level
---

# aibdd-isa-init

緣由：`dsl_to_isa` 在翻譯前必須能讀到 `${CONTRACTS_DIR}/isa.yml`（instruction regex SSOT）與（state handler 時）`${DATA_DIR}/entity_to_table_mapping.yml`； eval 的持久層若走 SQL DDL 而非 DBML，還須在 `${BOUNDARY_YML}` 以 `profile_overrides.state_specifier` 指向 `/aibdd-form-ddl-spec` 並鎖定 dialect。本 skill 只做這三項前置，不產 contracts／DDL 內容本身。

# SOP

0. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   BOUNDARY_YML=${BOUNDARY_YML}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   EOF
   ```

1. ASSERT 前置已就緒
   - `${AIBDD_ARGUMENTS_PATH}` 存在。
   - `${BOUNDARY_YML}` 存在且可 PARSE 出 `type`（例：`web-service`）。
   - 若 `${CONTRACTS_DIR}` 或 `${DATA_DIR}` 不存在 → CREATE 目錄（僅建立目錄，不寫規格內容）。
   - 任一失敗 → 提示先跑 `/aibdd-kickoff`，STOP。

2. DELEGATE `/clarify-loop`——單題確認 SF 持久層要用的 SQL dialect（決定 `state_specifier.format` 與後續 `${DATA_DIR}` 下 DDL 副檔名）。

   Payload（`questions` 一題；`options` 三選一）：

   | option id | label | 寫入 `profile_overrides.state_specifier.format` |
   |-----------|-------|-----------------------------------------------|
   | `mysql` | MySQL | `mysql` |
   | `pg` | PostgreSQL | `pg` |
   | `mssql` | Microsoft SQL Server | `mssql` |

   - `kind`: `BDY`
   - `context`: 將 `${BOUNDARY_YML}` 的 `state_specifier` 從預設 DBML 改為 DDL，供 SF eval 與 `dsl_to_isa` 使用。
   - `recommendation`: 依專案既有 stack 推斷；無法推斷則 `pg`。
   - clarify-loop 非成功完成 → STOP，不得手動在 chat 補問。

3. UPDATE `${BOUNDARY_YML}`——在保留既有欄位前提下，寫入或整塊替換 `profile_overrides.state_specifier`（對齊 `/aibdd-plan` `01-bind-and-load`：overrides 為 top-level key 整塊替換，不做 deep merge）：

   ```yaml
   profile_overrides:
     state_specifier:
       skill: /aibdd-form-ddl-spec
       format: <步驟 2 所選 mysql|pg|mssql>
   ```

   - 若檔案已有 `profile_overrides`，僅允許覆寫其內 `state_specifier` 子樹；不得新增 `profile_overrides` 以外之未知 top-level key。
   - WRITE 後 PARSE 確認 `type` 仍與步驟 1 一致。

4. WRITE `${CONTRACTS_DIR}/isa.yml`（idempotent）
   - 若檔案已存在 → 跳過本步，EMIT「已存在，未覆寫」。
   - 否則 READ `.claude/skills/aibdd-core/assets/boundaries/<$boundary_type>/isa-templates/isa.yml`（`$boundary_type` 為步驟 1 自 `${BOUNDARY_YML}` PARSE 之 `type`）→ COPY 寫入 `${CONTRACTS_DIR}/isa.yml`；模板不存在 → STOP 並回報 boundary type 與預期路徑。內容涵蓋 `api_call`／`entity_setup`／`entity_validate`／`response_validate`／`time_control`，對齊該 boundary preset 之 `HANDLER_TABLE`。

5. EMIT 完成摘要——列出：`state_specifier.format`、是否新建 `${CONTRACTS_DIR}/isa.yml`、是否新建 `${DATA_DIR}/entity_to_table_mapping.yml`；並提示下一步可接 `/aibdd-plan` `02-contracts-design`（產 DDL／OpenAPI）或 `/aibdd-dsl-to-isa-interpretation`（在 schema 就緒後跑 table mapping 與翻譯）。
