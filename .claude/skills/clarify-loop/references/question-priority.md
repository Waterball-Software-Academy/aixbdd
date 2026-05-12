# Question Priority

Planner 在 payload 提供每題 `priority_score`；clarify-loop 依此排序本批次的呈現順序與批次切分。

---

## Planner 計分建議

| 影響範圍 | 分數 |
|---------|------|
| 改變 top-level boundary / 檔案組織 | 15 |
| 改變 Rule 組成（跨多個 feature）| 12 |
| 改變 STEP 數量 / actor 界線 | 10 |
| 改變單一 Rule 的實作細節 | 8 |
| 新增 optional Rule / 通知通道（GAP 類）| 5 |

兩個維度可疊加 → 高分題先出。

---

## clarify-loop 排序規則

1. **高分先出**：影響大者先定錨（先做結構性決策，再填細節）
2. **同分排序**：依 `location` 字典序（同檔案聚合）
3. **依賴約束**：若 `Q_i.dependencies = [Q_j]` → `Q_j` 必須於同批或更早批次出現
4. **批次切分**：超過 `${MAX_QUESTIONS_PER_ROUND}` → 以分數為切點，前 N 題入本批，剩餘延後

---

## 依賴處理

payload 提供 `dependencies: [Qid, ...]` 時：

- **同批**：排序時確保依賴方先於被依賴者呈現
- **跨批**：依賴題目未解 → 被依賴題目延後至下一批；必要時延後多批
- **循環依賴**：偵測到 cycle → Step 1 回呼叫方 `{status: "invalid_dependencies", cycle: [...]}`

---

## Sweep 後重排

Consistency Sweep 若自動移除過時便條紙，clarify-loop 須：

1. 從剩餘 payload 移除對應題目
2. 若被移除題目是其他題的 dependency → 重新檢查依賴鏈
3. 下一 Round 以更新後的清單重排

---

## 範例

k=003 初始 10 題優先序（依上述規則）：

| # | 類型 | 分數 | 位置摘要 |
|---|------|------|---------|
| Q1 | BDY | 15 | 訪客觸發登入歸屬 auth/ vs checkout/ |
| Q2 | BDY | 12 | 訂單建立時機（送出 vs callback）|
| Q3 | BDY | 10 | callback 重試主體 |
| Q4 | BDY | 10 | callback 逾時處理 |
| Q5 | BDY | 10 | 收件地址環境前置 vs 主題前置 |
| Q6 | BDY | 10 | 選付款管道獨立 STEP vs 表單欄位 |
| Q7 | BDY | 8 | 訪客登入後接續行為 |
| Q8 | BDY | 6 | 金額計算爭議具體結果值 |
| Q9 | GAP | 5 | 庫存過期是否通知 |
| Q10 | GAP | 5 | 付款結果通知通道 |

本批次全部 10 題 ≤ `MAX_QUESTIONS_PER_ROUND = 10` → 一次 AskUserQuestion 呼叫處理（若受 AskUserQuestion 題數上限限制則拆為 Sub-round）。
