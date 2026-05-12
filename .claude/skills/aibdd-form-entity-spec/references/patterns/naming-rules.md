# Strategy Guard（逆向回饋）

生成/更新 erm.dbml 時，若發現以下情況，**REPORT** 給協調器並觸發 Strategy Guard：

1. **Aggregate 結構衝突**：正規化發現某 Aggregate 應拆分，而現有 .feature 的 Background datatable 違反設計 → 回到 Feature 層修正
2. **缺少必要 Aggregate**：關聯需要 Aggregate B 存在，但無 .feature 定義了它 → 回到 Strategic 補充
