# Feature Files 是「參考用」，不是「嚴格 1:1」

## 為什麼這條 reference 存在

之前討論時曾經把這條鬆綁過——**MSW 的 fixture 不需要逐 Example 1:1 對映**。本 skill 寫出來的 tasks.md 描述也必須**反映這個鬆綁**，避免下游 worker 誤以為要把 `01-開房或加入房.feature` 裡所有 Example 都翻成單獨的 fixture。

## 鬆綁的具體含義

| 維度 | 嚴格做法（**不採用**） | 參考做法（**本 skill 採用**） |
|---|---|---|
| Fixture 數量 | feature Examples 有 N 行就要有 N 個 named fixture | 由 worker 判斷合理數量；幾個有代表性的 happy-path / edge-case / failure 範例即可 |
| Fixture 名稱 | 對應 feature 內的 Example 文字 | 由 worker 自己取語意化命名 |
| Edge case 覆蓋 | 列出來的 Outline 表格列**全數**翻譯 | 列出來的 Outline 表格**做為靈感**，挑代表性的塞進 fixture |
| 失敗類別 | 每個失敗類別（例：`數字重複`、`長度不足`、`非數字`）都要 fixture | 至少**保留一條失敗 fixture 證明 handler 會回 4xx**；其他失敗類別交給 client-side 驗證攔下 |

## 用詞檢查（SOP Phase 3 step 10 會自動檢查）

寫 fixture-related task 時，**必須**使用以下任一語氣：

- ✅ "**參考** `<feature 檔名>` 設計合理 fixture"
- ✅ "以 `<feature 檔名>` 的 Examples **作為靈感**，挑代表性場景落 fixture"
- ✅ "fixture **不需逐 Example 1:1**；happy + 1 邊界 + 1 失敗即可"

**禁止**用以下語氣（會被 SOP `$ref_phrase_check` 擋下）：

- ❌ "逐 Example 對映 fixture"
- ❌ "每個 Example 都要對應一個 named fixture"
- ❌ "完整翻譯 feature 的 Outline 表格"

## 為什麼還是要把 feature files 列為 SSOT 之一

雖然不是 1:1 對映，但 feature files **依然是必讀**：

1. **Schema 線索**：feature 內的 Given/When/Then 經常包含 entity 欄位範例（例：`房局 R-1 房碼 "0123" 玩家 P-A 席次 "1"`），有助於 fixture 內的資料形狀**像真的**
2. **業務不變式**：feature 隱含了業務規則（例：「房內已 9 人時第 10 人可加入」 → fixture 至少要有「9 人房 ready 加入新人」的場景）
3. **失敗碼選擇**：feature 提示哪些情境該回成功、哪些該回失敗，但**不規定 HTTP status code**——那由 contract 決定

**簡言之：feature 提供「應該存在哪些情境」的問題清單，contract 提供「情境的回應形狀」的答案；fixture 用 contract 的形狀去裝 feature 提到的情境**。
