---
name: aibdd-green-execute
description: Turn a legal Red handoff for target feature files green by verifying drift, editing product code only, detecting failure oscillation, and emitting a Green handoff. TRIGGER when Green execute is requested after aibdd-red-execute. SKIP when no legal Red handoff exists or the request is test, DSL, runtime, or architecture repair.
metadata:
  user-invocable: true
---

# aibdd-green-execute

接住上游一個合法的 red handoff，把那組 target feature 檔從紅燈做到綠燈——而且只准動產品程式碼。最後把這次轉綠的結果整理成 green handoff，交給下游的 refactor。

## 這支 skill 在做什麼

1. 接住 red handoff，確認它合法、而且講的就是這次要處理的那組 feature。
2. 確認從紅到現在 runtime 環境沒有飄移。
3. 一次只修一個失敗、只改產品程式碼、只寫剛好讓它通過的最小量，反覆跑到全綠；過程中盯著有沒有「兩種失敗來回擺盪」的死循環。
4. 把這次轉綠的結果整理成 green handoff，交給呼叫者。

## 執行原則

1. 依序執行、不要跳步；每做一步，在訊息中講出你正在做哪一步，方便對話被壓縮後還能接回來。
2. 只准改產品程式碼。feature、歸檔、step-def、DSL、核心 ref、runtime ref、fixture 慣例、BDD 憲章這些檔案一律不准動——要動它們表示問題不在這支 skill，該停下來路由出去。
3. 每個失敗只寫剛好讓它通過的最小產品碼：能讓 runner 報的「第一個失敗」轉綠的最小改動就停手，不替測試還沒要求的行為、欄位、分支或抽象預先鋪路（那是下一個失敗、或 refactor 的事）。
4. 除非遇到底下明確寫出的 STOP 條件，否則一路做到產出 green handoff 為止；中途不要停下來問「要不要繼續」。真的遇到 STOP 條件時，就停下來、把停止原因（`stop_reason`）與該去找誰回報清楚。

## SOP

1. RESOLVE arguments：把後續會用到的 `${VAR}` 一次綁定，resolver 的 stdout 原樣 EMIT 給用戶；非 0 退出就停下來並透傳 stderr（缺 `.aibdd/arguments.yml` 是 exit 1，缺鍵是 exit 2 並列出缺哪些鍵）。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACCEPTANCE_RUNNER_RUNTIME_REF=${ACCEPTANCE_RUNNER_RUNTIME_REF}
   STEP_DEFINITIONS_RUNTIME_REF=${STEP_DEFINITIONS_RUNTIME_REF}
   FIXTURES_RUNTIME_REF=${FIXTURES_RUNTIME_REF}
   FEATURE_ARCHIVE_RUNTIME_REF=${FEATURE_ARCHIVE_RUNTIME_REF}
   EOF
   ```

2. 上游指定的 target feature files 就是本次 scope，以 `$SCOPE_FEATURE_FILES` 變數稱之；請在對話中簡單復述一次 `$SCOPE_FEATURE_FILES`，復述完不停，直接進下一步。

3. 接住 red handoff：READ 呼叫者交來的 `red_handoff`，依 `references/handoff-schemas.md` 解析；確認 `status` 是 `completed`、`stop_reason` 是 `none`；確認 `red_handoff.target_feature_files` 和 `$SCOPE_FEATURE_FILES` 完全一致，不一致就停下來，把可路由的 target 不符原因記成 `stop_reason`。

4. READ `${ACCEPTANCE_RUNNER_RUNTIME_REF}`、`${STEP_DEFINITIONS_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}`、`${FEATURE_ARCHIVE_RUNTIME_REF}`，理解如何在本專案跑測試、step／fixture／歸檔分別在哪。

5. EXECUTE `steps/verify-no-drift.md`：確認從紅到現在 runtime 沒有飄移。

6. [LOOP] EXECUTE `steps/turn-green-edit-product-code.md`：反覆改產品程式碼直到全綠。

7. READ `references/handoff-schemas.md` and REPORT：確認動過的只有產品程式碼，render green handoff 交回呼叫者，或遵照上游所指定的 report 方式。
