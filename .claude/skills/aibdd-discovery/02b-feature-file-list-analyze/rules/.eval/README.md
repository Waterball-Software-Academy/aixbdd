# Feature file list — API granularity benchmarks

針對 `API-granularity.md` 中 **流程編排／自動推進**、**內建系統處理**、**僅可命名之分支** 等陷阱的評測集。

## 用法

1. 僅將各 case 的 **需求原文** 提供給執行者（或 LLM）。
2. 請其依 `API-granularity.md` 產出 feature file 清單。
3. 與同檔 **預期產出**、**不應出現** 兩節比對；預期齊全且無誤拆即通過（順序不拘，同義檔名需人工對照）。

## 本集涵蓋的陷阱

- **批次完成後自動編排**：需求寫「全部 X 完成後系統自動 Y」，不應另開 feature。
- **階段轉換當副作用**：進入下一階段、建立背景任務，併入最後一個使用者 Action。
- **內部技術鏈**：計算、寫庫、通知、呼叫第三方，不拆成並列 feature。
- **可命名分支**：多種處置／策略用 Scenario，不因可獨立命名而拆檔。

## Cases

| 編號 | 檔案 |
|------|------|
| 01 | `cases/01-parallel-countersign.md` |
| 02 | `cases/02-daily-settlement-batch.md` |
| 03 | `cases/03-manuscript-review-publish.md` |
| 04 | `cases/04-procurement-qa-negotiation.md` |
| 05 | `cases/05-onboarding-verification.md` |
| 06 | `cases/06-guess-number-boss-room.md` |
