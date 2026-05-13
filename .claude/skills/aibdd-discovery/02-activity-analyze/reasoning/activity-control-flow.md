# 活動圖控制流推理流程

1. **`$INITIAL_ACTION` 與 `INITIAL`**：`$INITIAL_ACTION`＝此 flow 在敘事上**第一個**業務 Action（或由使用者／外部觸發後、進入系統邊界後之第一個可指認 Action）。將圖上 **`INITIAL`（起點）**以單一轉移連到 **`$INITIAL_ACTION`**。

2. **有向骨架**：僅依 `$P` 可引用之**時間／因果／敘事先後**，把屬於此 flow 的 Action 用有向邊串起；先**不接**條件文字，但須自 `INITIAL → …` 可到達每個已聲稱屬於此 flow 的 Action（暫時允許「尚缺決策」之匯流暫存點，標在內部註記即可）。

3. **decision／branch／merge**：凡 `$P` 出現**可判定條件**（若／否則／分支／審核結果／狀態值等）→ 補 **decision**（或語法等效之守衛節點）與帶語意標籤之**分支邊**；多條支線重匯同一後續 Action → 以 **merge**（或等效、但必須單一讀者看得懂之匯合）收斂。**禁止**無標籤之多重出邊或「分支語意與證據句脫鉤」。

4. **fork／parallel／join**：僅當 `$P` **明示**可並行、互不阻塞、且完成條件為「**全部**完成才續行」時，使用 **fork** 拆支線、在匯攏處使用 **join**；每一並行支線仍須滿足 `rules/activity-step-granularity.md`（**不得**把單一業務意圖之內部技術鏈拆成 parallel）。

5. **final／rework**：凡業務上可結案／可驗收失敗或成功終點 → 接到 **final**（或 Activity **`FINAL`**，依你所採記號法擇一且全檔一致）。若有 **退回、補件、再送** → 畫出**回到**先前 Action 或 decision 的邊，並確保從 `INITIAL` 經由該迴圈仍可達某 **final**（圖上不可無終）。

6. **分析證據與可達性 -> 紀錄 $GAPS**：對每一 Action、decision、fork／join、merge 與每一條轉移，**至少**能指回一句 `$P`（或已約定之 discovery 佐證）；做不到則刪結構或寫入 `$GAPS`。掃描**死路**（到不了 **final**）、**不可達節點**、僅有入無出／無入有出之異常 → 修正或記 **$GAPS**。

˙. **寫回**：通過上一項檢查後，將圖形與註解**更新**至該 flow 對應之 `.activity`（步驟 **4** 已建檔）。**跨 flow** 的 Action 若因 `rules/activity-diagram-granularity.md` 必須分檔，**不得**硬併入本檔。
