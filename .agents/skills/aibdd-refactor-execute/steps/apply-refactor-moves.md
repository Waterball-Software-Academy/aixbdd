# SOP

1. 算出這次受保護的產品程式碼範圍：依 `${DEV_CONSTITUTION_PATH}` 的結構／分層規約、`green_handoff.product_files_modified` 與 target feature files 推得；開發憲章同時界定「哪些整理方向才合規」。
2. 依 `../references/refactor-move-policy.md` 的優先序，把可改善處分類成候選整理動作；過濾掉會改行為、新增功能、改契約、或觸及 SKILL.md 執行原則所列受保護表面的候選，以及重複次數少於三次的 DRY 抽取。
3. 準備三份空清單：已採用的動作、已退回的動作、縮小範圍的紀錄。
4. [LOOP] 逐一處理每個候選動作：
   1. 對照 `../references/refactor-move-policy.md` 的 interaction gate，看這個動作需不需要使用者審核；需要就先問使用者，不同意就標記略過、換下一個。
   2. 只針對「剛好一個結構性動作」改產品程式碼。
   3. 對這組 target feature 跑一次 acceptance runner，得到最新報告。
   4. 報告 `passed`：記進「已採用」。報告 `failed`：把剛剛的改動退回，記進「已退回」。
   5. 連續退回達 3 次：把範圍從整組 target 縮小到單一 feature 檔或最小的產品程式碼區塊，記進「縮小範圍」紀錄，並用新範圍重新過濾剩餘候選。
5. 候選都跑完後，對這組 target feature 再跑一次 acceptance runner；確認最終報告 `passed`，否則停下來，回報 `stop_reason: refactor_safety_failure`。
