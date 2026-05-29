# SOP

緣由：從 session 記錄的 `replay_from` planner 開始，依固定上下游順序逐一重跑 planner；每跑完一個就把 session 進度指標往前推一格。任一 planner 沒跑到 completed 就停在那裡，下游不續跑。

1. TRIGGER 路徑解析 script 取回 active session 路徑（同 01 的呼叫，參數相同）。READ active session JSON，取出 `replay_from`。

2. BRANCH `replay_from` 決定從哪一步起跑：
   1. `aibdd-discovery` → 從步驟 3 開始（discovery → plan → spec-by-example 全跑）。
   2. `aibdd-plan` → 跳到步驟 5（plan → spec-by-example）。
   3. `aibdd-spec-by-example-analyze` → 跳到步驟 7（只跑 spec-by-example）。
   4. 其他值 → STOP 並回報用戶：session replay 指標非法。

3. DELEGATE `/aibdd-discovery`，payload 依 `.claude/skills/aibdd-reconcile/references/planner-handoff-contract.md` 的 Discovery Payload 組裝。
   1. 若回報 status 不是 completed，STOP 並回報用戶：reconcile 停在 /aibdd-discovery，下游未執行。

4. TRIGGER session 進度推進 script，把指標推到 `aibdd-plan`：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/manage_reconcile_session.py advance \
     "<active_session_path>" "aibdd-plan"
   ```

5. DELEGATE `/aibdd-plan`，payload 依 `.claude/skills/aibdd-reconcile/references/planner-handoff-contract.md` 的 Plan Payload 組裝。
   1. 若回報 status 不是 completed，STOP 並回報用戶：reconcile 停在 /aibdd-plan，/aibdd-spec-by-example-analyze 未執行。

6. TRIGGER session 進度推進 script，把指標推到 `aibdd-spec-by-example-analyze`：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/manage_reconcile_session.py advance \
     "<active_session_path>" "aibdd-spec-by-example-analyze"
   ```

7. DELEGATE `/aibdd-spec-by-example-analyze`，payload 依 `.claude/skills/aibdd-reconcile/references/planner-handoff-contract.md` 的 Spec-by-Example Payload 組裝。
   1. 若回報 status 不是 completed，STOP 並回報用戶：reconcile 停在 /aibdd-spec-by-example-analyze。
