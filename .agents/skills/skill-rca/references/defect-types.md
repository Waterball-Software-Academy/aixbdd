# Skill 缺陷類型參考

## 分類表

| 類型稱呼 | 定義 | 典型修復 |
|------|------|---------|
| 決策樹盲區 | 決策樹/SOP 有未考慮的分支或前提 | 補分支、加前置檢查 |
| 模板誤導 | 模板結構暗示了錯誤做法 | 改模板結構、加註解 |
| 參考膚淺 | 規則存在但不夠具體，邊界情況未覆蓋 | 補具體案例、加邊界說明 |
| 自驗缺失 | 產出後沒有驗證步驟攔截錯誤 | 加 checklist 或驗證規則 |
| 繼承遺漏 | 跨層級傳遞時丟失資訊 | 補繼承清單、加 cross-check |
| 規章落差 | skill 結構尚未符合 Program-like SKILL.md 規章，或已符合但 SOP / references / reasoning 漂移 | 委派 `/programlike-skill-creator` 產生遷移或修復提案 |
| 孤兒資產 | skill artifact 存在但無 runtime consumer、human-aid 標記、deprecated 標記或 manifest 保留理由 | 刪除、移到 legacy/deprecated，或補上真實 consumer edge |
| 雙重真值來源 | 同一概念在多個 artifact 以 SSOT / contract / required format 身分重複宣告，且可能互相漂移 | 指定唯一 SSOT；其他檔改成 thin entry、link 或 deprecated |
| 過胖模板未 lazy-load | 單一 template 承載多個 phase / RP / consumer 區塊，導致 caller 只能整檔 READ 或以段落字串引用 | 拆成 lazy-load 子檔，保留薄入口與明確載入順序 |
| 分桶錯誤 | 流程、gate 或 branching 藏在 `references/` / `assets/`，或固定輸出格式藏在 `reasoning/` / reference 概念檔 | 依職責移回 `SKILL.md`、`reasoning/`、`references/` 或 `assets/templates/` |
| 資產生命週期漂移 | artifact 的 owner、consumer、讀取粒度或淘汰狀態與現行 pipeline 不一致 | 建立 artifact graph，消除孤兒、雙 SSOT、過胖模板或錯層資產 |

可複合（如「決策樹盲區 + 模板誤導」、「自驗缺失 + 規章落差」、「孤兒資產 + 資產生命週期漂移」）。

RCA 報告與 root cause 摘要一律使用「類型稱呼」，不得使用縮寫標籤。根因描述只指向 skill artifact 的設計缺陷，不將責任歸咎於提出請求的人。

---

## 向後驗證規則

提案修改後，mental replay 一次：

> 如果 skill 已有這個修改，原缺陷還會不會產生？

- 若答案是「**會**」→ 提案不夠，需再加強
- 若答案是「**不會**」→ 提案通過，可執行
