---
name: aibdd-refactor-execute
description: Refactor product code under a Green target feature-file set by loading the dev constitution and runtime refs, applying one minimal move at a time, rerunning acceptance tests, reverting red moves, and emitting a Refactor handoff. TRIGGER when Refactor execute is requested after aibdd-green-execute. SKIP when the target set is not green or the request adds behavior.
metadata:
  user-invocable: true
---

# aibdd-refactor-execute

在「這組 target feature 已經全綠」這個安全網底下整理產品程式碼：一次只做一個最小的結構性整理，每做一個就重跑一次測試，紅了就立刻退回去。全程不准新增行為。最後把整理結果整理成 refactor handoff，交回呼叫者。

## 這支 skill 在做什麼

1. 接住 green handoff，確認它合法、而且講的就是這次要整理的那組 feature。
2. 載入開發憲章與 runtime 來源，確認從綠到現在沒有飄移。
3. 重跑一次測試，確認 target 真的是綠的（這是整理的安全網）。
4. 依開發憲章與 refactor-move-policy 挑候選、一次只做一個結構性整理、跑一次測試：過了就保留，紅了就退回；連續退太多次就縮小範圍。
5. 把整理結果整理成 refactor handoff，交回呼叫者。

## 執行原則

1. 依序執行、不要跳步；每做一步，在訊息中講出你正在做哪一步。
2. 只整理、不加行為：一次只做一個結構性動作，不准改 API 契約、DB schema、IPC 契約、runtime feature、step-def matcher、fixture 契約、runtime ref、或可測試性錨點的簽章。
3. 綠燈是唯一安全網：每個動作做完都要重跑測試，紅了就立刻退回那個動作。
4. 需要使用者審核的動作（interaction gate）一定要先問過再做；除此之外，除非遇到底下明確寫出的 STOP 條件，否則一路做到產出 refactor handoff 為止，中途不要停下來問「要不要繼續」。

## SOP

1. RESOLVE arguments：把後續會用到的 `${VAR}` 一次綁定，resolver 的 stdout 原樣 EMIT 給用戶；非 0 退出就停下來並透傳 stderr（缺 `.aibdd/arguments.yml` 是 exit 1，缺鍵是 exit 2 並列出缺哪些鍵）。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   DEV_CONSTITUTION_PATH=${DEV_CONSTITUTION_PATH}
   ACCEPTANCE_RUNNER_RUNTIME_REF=${ACCEPTANCE_RUNNER_RUNTIME_REF}
   STEP_DEFINITIONS_RUNTIME_REF=${STEP_DEFINITIONS_RUNTIME_REF}
   FIXTURES_RUNTIME_REF=${FIXTURES_RUNTIME_REF}
   FEATURE_ARCHIVE_RUNTIME_REF=${FEATURE_ARCHIVE_RUNTIME_REF}
   EOF
   ```

2. 上游指定的 target feature files 就是本次 scope，以 `$SCOPE_FEATURE_FILES` 變數稱之；請在對話中簡單復述一次 `$SCOPE_FEATURE_FILES`，復述完不停，直接進下一步。

3. 接住 green handoff：READ 呼叫者交來的 `green_handoff`，依 `references/handoff-schemas.md` 解析；確認 `status` 是 `completed`、`stop_reason` 是 `none`；確認 `green_handoff.target_feature_files` 和 `$SCOPE_FEATURE_FILES` 完全一致，不一致就停下來，把可路由的 target 不符原因記成 `stop_reason`。

4. READ 開發憲章 `${DEV_CONSTITUTION_PATH}` 與 `${ACCEPTANCE_RUNNER_RUNTIME_REF}`、`${STEP_DEFINITIONS_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}`、`${FEATURE_ARCHIVE_RUNTIME_REF}`：開發憲章決定本專案的結構／分層規約（哪些整理方向才合規、哪些程式碼受保護），runtime refs 決定如何跑測試、step／fixture／歸檔在哪。

5. EXECUTE `steps/verify-no-drift.md`：確認從綠到現在 runtime 沒有飄移。

6. 確認綠燈安全網：對這組 target feature 跑一次 baseline acceptance runner；結果非 `passed` 就停下來，回報 `stop_reason: not_green_baseline`；並確認 runner 指令確實涵蓋每一個 target。

7. [LOOP] EXECUTE `steps/apply-refactor-moves.md`：依開發憲章與 refactor-move-policy，一次只做一個結構性整理直到候選跑完。

8. READ `references/handoff-schemas.md` and REPORT：只從「已採用」的動作算出最終真正改到的檔案清單，render refactor handoff 交回呼叫者，或遵照上游所指定的 report 方式。
