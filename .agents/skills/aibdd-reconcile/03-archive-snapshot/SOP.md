# SOP

緣由：在 `start_new` 的回合，把 plan package 根目錄整批歸檔到 `archive/<session_id>/`，保存舊產物，讓下游從乾淨的 package 根重跑；`merge_existing` 回合則不重複歸檔。最後把目前 session 狀態投影成人類可讀的 `RECONCILE_RECORD.md`。

1. TRIGGER 路徑解析 script 取回 active session 路徑（同 01 的 `resolve_reconcile_context.py` 呼叫，參數相同、結果固定）。READ active session JSON，取出 `mode` 與 `session_id`。

2. BRANCH session 的 `mode`：
   1. 若為 `merge_existing` → 跳過歸檔（產物已在開 session 那一回合歸檔過），直接前往步驟 5。
   2. 若為 `start_new` → 續做步驟 3、4。

3. TRIGGER 歸檔預覽 script，先確認會搬哪些 entry（dry-run，不動檔）：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/preview_archive.py \
     "<arguments.yml 路徑>" "<target_plan_package>" "<session_id>"
   ```

   1. OUTCOME：stdout JSON 的 `entries_to_move` 列出將被搬進 `archive/<session_id>/` 的項目。
   2. 若 JSON 的 `ok` 不為 true 或 script 非 0 退出，STOP 並回報用戶歸檔預覽失敗。

4. TRIGGER 歸檔執行 script，把 package 根目錄下除 `archive/` 外的每個 entry 搬進 `archive/<session_id>/`。本步授權搬移既有 package 產物進 archive：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/execute_archive.py \
     "<arguments.yml 路徑>" "<target_plan_package>" "<session_id>"
   ```

   1. 若 JSON 的 `ok` 不為 true 或 script 非 0 退出，STOP 並回報用戶歸檔執行失敗。

5. TRIGGER record 渲染 script，把目前 active session JSON 投影成 `RECONCILE_RECORD.md`。本步授權寫入 `record_path` 指向的 `RECONCILE_RECORD.md`：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/render_reconcile_record.py \
     "<active_session_path>" "<record_path>"
   ```

   1. 若 script 非 0 退出，STOP 並回報用戶 `RECONCILE_RECORD.md` 寫入失敗。
