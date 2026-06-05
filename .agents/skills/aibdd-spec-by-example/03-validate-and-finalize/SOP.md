# SOP — 03 validate and finalize

對 phase 2 補完的每筆 Example 做 pattern key 檢核、formatter 檢核、cucumber 字面檢核，最後產出總結讓用戶決定下一步。

0. RESOLVE arguments——沿用 Phase 1 已 EMIT 之 binding；若缺失則重跑 resolver（manifest 同 `01-scan-and-classify/SOP.md` 步驟 0）。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

1. FOR EACH `$expanded_rule` in `$expanded_rules`：READ 該 Rule 之 Example block（已 UPDATE 進 `.feature` 檔），執行 step 2..4。

2. ASSERT pattern key 檢核：依 `rules/pattern-key-checklist.md` 對該 pattern 之必填元素逐項核對 Example 文字。缺項者加入 `$validation_failures`，記錄 `{rule, missing_keys}`。本步只讀檔做斷言，不寫檔。

3. ASSERT formatter 檢核：依 `rules/formatter-rules.md` 檢查該 Example 之類型前綴、關鍵字順序、空行、標點、Example 標題（不含 Cucumber 引號／And 縮排；該項只在步驟 4）。不合格者加入 `$validation_failures`，記錄 `{rule, formatter_issues}`。本步只讀檔做斷言，不寫檔。

4. ASSERT cucumber 可跑字面檢核：僅依 `rules/cucumber-literal-format.md` 檢查引號、`And` 縮排、Data Table cell、禁止 step 內「」。不合格者加入 `$validation_failures`，記錄 `{rule, cucumber_literal_issues}`。本步只讀檔做斷言，不寫檔；禁止在其他步驟或 phase 2 重複執行本檢核。

5. IF `$validation_failures.length > 0`：DELEGATE 回 phase 2 step 7 對失敗者重寫 Example；禁止在本 phase 直接 UPDATE 修補（保持單一寫入入口）。重寫完成後重跑 step 1..4，直到 `$validation_failures` 為空。

6. DERIVE `$summary`：彙整本次執行結果，含 `{total_rules, expanded_count, skipped_count, blocked_count}`，與 `$blocked_rules` 之每筆原因摘要（多為「用戶補問未完成」或「分類失敗」）。本步只產出 in-memory 結構，不寫檔。

7. IF `$blocked_count > 0`：向用戶呈報 `$blocked_rules` 清單，問是否要繼續處理或暫停；若用戶選擇暫停，本 skill 終止；若選擇繼續，DELEGATE 回 phase 1 重跑 blocked 筆。

8. IF `$blocked_count == 0` 且 `$expanded_count > 0`：向用戶呈報 `$summary`，並依 SKILL.md SOP step 4 引導下一步（提示可執行 `/aibdd-api-plan` 或 `/aibdd-data-plan` 來產出 API Plan 或 Data Plan）。本步僅允許輸出文字訊息給用戶，禁止 UPDATE 任何 `.feature` 檔或建立新檔。

9. IF `$expanded_count == 0`（全部 skip）：向用戶呈報「本 package 無 Rule 需補完」並終止。本步僅允許輸出文字訊息，禁止寫檔。
