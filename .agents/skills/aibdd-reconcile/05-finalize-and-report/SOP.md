# SOP

緣由：所有該重跑的 planner 都跑完後，把 session 收尾、寫出最終紀錄，並用白話跟用戶報告這次對齊的結果與後續待辦。

1. TRIGGER 路徑解析 script 取回 active session 路徑與 record 路徑（同 01 的呼叫，參數相同）。

2. TRIGGER session 收尾 script，把 session 標記為 completed 並落地最終 session JSON。本步授權寫入 `archive/<session_id>/RECONCILE_SESSION.json` 並移除 active session 檔：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/manage_reconcile_session.py finish \
     "<active_session_path>" "completed"
   ```

   1. OUTCOME：stdout JSON 的 `stdout_final_session_path` 是最終 session JSON 落地位置；active session 檔已移除。
   2. 若 script 非 0 退出，STOP 並回報用戶：session 收尾失敗，請檢查 active session 檔。

3. TRIGGER record 渲染 script，從最終 session JSON 寫出最終 `RECONCILE_RECORD.md`。本步授權寫入 `record_path` 指向的 `RECONCILE_RECORD.md`：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/render_reconcile_record.py \
     "<stdout_final_session_path>" "<record_path>"
   ```

   1. 若 script 非 0 退出，STOP 並回報用戶：最終 `RECONCILE_RECORD.md` 寫入失敗。

4. EMIT 給用戶一段白話總結，至少涵蓋：本次目標 plan package、最上游 planner、歸檔位置、cascade chain、以及這次 reconcile 的 trigger 描述。

5. EMIT 提醒用戶：「/aibdd-tasks、/aibdd-implement 已過期；請重新 derive tasks 並重跑 implement。」
