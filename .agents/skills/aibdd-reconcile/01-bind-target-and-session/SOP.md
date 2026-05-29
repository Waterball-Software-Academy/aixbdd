# SOP

緣由：把頂層綁定的三個輸入轉成具體、已驗證的路徑，並判斷本次是「開一個新 session」還是「併入一個進行中的 session」，供後續每個 phase 沿用。本 phase 不動任何檔案，只做驗證與判斷。

1. ASSERT trigger 描述非空。
   1. 若頂層步驟 0 綁定的 trigger 描述為空字串，STOP 並回報用戶：「trigger 描述不可為空；請提供本次 reconcile 的缺陷或需求描述。」

2. TRIGGER 路徑解析 script，把目標 package、archive 目錄、active session 檔、record 檔等具體路徑一次算出來：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/resolve_reconcile_context.py \
     "<arguments.yml 路徑>" "<目標 plan package 路徑>"
   ```

   1. INPUTS
      1. 第 1 參數：頂層綁定的 arguments.yml 路徑。
      2. 第 2 參數：頂層綁定的目標 plan package 路徑。
   2. OUTCOME
      1. stdout 回傳 JSON，含 `target_plan_package`、`archive_dir`、`active_session_path`、`record_path`、`specs_root` 等已解析路徑。
      2. 後續所有 phase 一律沿用此 JSON 的路徑欄位，不自行重算；需要時各 phase 可用相同兩個參數再呼叫一次此 script 取回（結果固定）。
   3. 若 script 非 0 退出，STOP 並把 stderr 透傳給用戶（通常代表目標 package 不在 `${SPECS_ROOT_DIR}` 下、basename 沒有數字前綴、或不是一個目錄）。

3. DERIVE 本次的 session 模式：
   1. 檢查上一步 JSON 的 `active_session_path` 檔案是否存在。
   2. 若存在 → session 模式為 `merge_existing`：該 package 已有進行中的 session，本輪併入。
   3. 若不存在 → session 模式為 `start_new`：本輪開一個新 session 並執行歸檔。
   4. 本步只產出判斷，不寫檔。把 session 模式帶往下一個 phase。
