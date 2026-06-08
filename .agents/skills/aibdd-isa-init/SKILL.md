---
name: aibdd-isa-init
description: > 
   初始化 ISA 相關規格：確認 SQL dialect、建立 `isa.yml`。
metadata:
  user-invocable: true
  source: project-level
---

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
   1. `${AIBDD_ARGUMENTS_PATH}` 存在。
   2. `${BOUNDARY_YML}` 存在且可 PARSE 出 `type`（例：`web-service`）。
   3. 若 `${CONTRACTS_DIR}` 或 `${DATA_DIR}` 不存在 → CREATE 目錄（僅建立目錄，不寫規格內容）。
   4. 任一失敗 → 提示先跑 `/aibdd-kickoff`，STOP。

2. DELEGATE `/clarify-loop`——單題確認專案持久層要用的 SQL dialect（決定 `state_specifier.format` 與後續 `${DATA_DIR}` 下 DDL 副檔名）。

   Payload（`questions` 一題；`options` 三選一）：

   | option id | label | 寫入 `profile_overrides.state_specifier.format` |
   |-----------|-------|-----------------------------------------------|
   | `mysql` | MySQL | `mysql` |
   | `pg` | PostgreSQL | `pg` |
   | `mssql` | Microsoft SQL Server | `mssql` |

   1. `kind`: `BDY`
   2. `context`: 將 `${BOUNDARY_YML}` 的 `state_specifier` 設為 DDL，供 SF eval 與 `dsl_to_isa` 使用。
   3. `recommendation`: 依專案既有 stack 推斷；無法推斷則 `pg`。
   4. clarify-loop 非成功完成 → STOP，不得手動在 chat 補問。

3. UPDATE `${BOUNDARY_YML}`——在保留既有欄位前提下，寫入或整塊替換 `profile_overrides.state_specifier`：

   ```yaml
   profile_overrides:
     state_specifier:
       skill: /aibdd-form-ddl-spec
       format: <步驟 2 所選 mysql|pg|mssql>
   ```

   1. 若檔案已有 `profile_overrides`，僅允許覆寫其內 `state_specifier` 子樹；不得新增 `profile_overrides` 以外之未知 top-level key。
   2. WRITE 後 PARSE 確認 `type` 仍與步驟 1 一致。

4. WRITE `${CONTRACTS_DIR}/isa.yml`（idempotent）
   1. 若檔案已存在 → 跳過本步，EMIT「已存在，未覆寫」。
   2. 否則 READ `.claude/skills/aibdd-core/assets/boundaries/<$boundary_type>/isa-templates/isa.yml`（`$boundary_type` 為步驟 1 自 `${BOUNDARY_YML}` PARSE 之 `type`）→ COPY 寫入 `${CONTRACTS_DIR}/isa.yml`；模板不存在 → STOP 並回報 boundary type 與預期路徑。

