# Rule 1 - 必須以全 spec taxonomy 掃描高影響缺口

- Level: `MUST`
- 掃描 `spec.md` 時，必須先建立 coverage 觀點，而不是只追著現成的 `NEEDS CLARIFICATION` 標記跑。
- 至少依下列 taxonomy 逐類盤點，並在心中標記 `Clear`、`Partial` 或 `Missing`：
  - Functional Scope & Behavior
    - 核心使用者目標與成功條件是否清楚
    - out-of-scope 或非目標是否有明示
    - 角色、使用者類型或權限邊界是否分得清楚
  - Domain & Data Model
    - 關鍵實體、欄位、關係是否足夠支持需求
    - 唯一性、識別方式、狀態轉換或生命週期是否清楚
    - 重要資料量假設或容量邊界是否缺失
  - Interaction & UX Flow
    - 關鍵流程、前後步驟與狀態切換是否可重演
    - error / empty / loading / retry / interrupted states 是否有定義
    - 可及性、語系或互動限制是否有明示
  - Non-Functional Quality Attributes
    - Performance：延遲、吞吐、回應門檻是否足夠可驗證
    - Scalability：規模、併發、成長上限是否有假設
    - Reliability & Availability：故障、恢復、不中斷要求是否存在
    - Observability：logging、metrics、tracing 或 debug signals 是否需要
    - Security & Privacy：角色限制、資料保護、濫用防護是否缺失
    - Compliance：法規、審計或治理限制是否有明示
  - Integration & External Dependencies
    - 外部服務、第三方 API、通知通道或同步依賴是否存在
    - 匯入匯出格式、協議或版本假設是否缺失
    - 外部依賴失敗時的退化行為是否未定
  - Edge Cases & Failure Handling
    - 負向情境、非法輸入、競態衝突是否已涵蓋
    - rate limit、throttling、timeout、斷線、重送等情況是否缺失
    - 多人同時操作、狀態不同步或重複提交的處理是否未定
  - Constraints & Tradeoffs
    - 已知技術、部署、儲存或環境限制是否已進 spec
    - 明確取捨、拒絕方案或刻意延後範圍是否有說清楚
  - Terminology & Consistency
    - 同一概念是否用多種名稱描述
    - User Story、FR/NFR、關鍵實體與成功標準之間是否互相矛盾
  - Completion Signals
    - 驗收情境是否足夠驗證主要流程
    - 成功標準是否可量測、可驗證且與需求一致
    - checklist ready 判定是否可能被尚未拍板的缺口推翻
  - Misc / Placeholders
    - `TODO`、`TBD`、`NEEDS CLARIFICATION`、模糊形容詞或未量化用語是否影響後續規劃
- 若某類是 `Partial` 或 `Missing`，應進一步判斷它是否足以形成候選提問，而不是直接把所有缺項都升級。

## Good Example

- 這個例子是好的，因為它保留分類與子項，不必回讀外部來源也能重演掃描。

```md
掃描結果：
- Interaction & UX Flow：`Partial`
  - 已有主要成功路徑
  - 缺少斷線與 retry 情境
- Non-Functional Quality Attributes：`Partial`
  - 已說明需要即時同步
  - 缺少可接受延遲門檻
- Terminology & Consistency：`Clear`
```

## Bad Example

- 這個例子是壞的，因為它把高指導面積 taxonomy 壓成一句空泛口號。

```md
掃描方式：
- 系統性檢查 spec 是否還有缺口
```

# Rule 2 - 只有會改變規格正確性或 readiness 的缺口才升級為候選提問

- Level: `MUST`
- 某個 `Partial` 或 `Missing` 類別，只有在其答案會實質改變下列事項時，才應建立 candidate question：
  - 使用者故事切分、邊界或優先順序
  - FR / NFR 歸戶、需求正確性或規格一致性
  - 正式驗收情境、成功標準或 ready 判定
  - 關鍵實體、資料約束、狀態轉換或外部依賴
  - 會讓 `/plan`、後續研究或設計明顯走向不同方向的關鍵決策
- 若缺口只影響命名偏好、微文案、局部互動措辭、可在規劃或實作時安全採用預設的低風險細節，應保留在 spec 的假設、`NEEDS CLARIFICATION` 或 deferred 風險中，不升級為本輪提問。
- 若缺口已在 spec 明示為刻意延後、不納入第一版或由其他 skill 承接，也不應重複升級提問。

## Good Example

- 這個例子是好的，因為提問會直接改變驗收與 NFR 邊界。

```md
缺口：
- 「狀態同步要在可接受的時間內完成」但沒有延遲門檻

判斷：
- 會影響 NFR 驗證與 readiness
- 建立 candidate question
```

## Bad Example

- 這個例子是壞的，因為它把低風險 wording 偏好升級成正式提問。

```md
缺口：
- 錯誤訊息要寫「重新嘗試」還是「再試一次」

判斷：
- 建立 candidate question
```

# Rule 3 - 候選提問必須依 Impact × Uncertainty 排序，並控制提問預算

- Level: `MUST`
- 建立 candidate question 後，必須以 `Impact × Uncertainty` 的綜合判斷排序，而不是依 spec 出現順序或看到哪個缺口先問哪個。
- `Impact` 應優先看它對規格正確性、跨章節一致性、正式驗收、資料模型、NFR 承諾與後續 `/plan` 的影響面。
- `Uncertainty` 應看目前 spec 是否存在多種合理解讀、是否互相矛盾、是否缺少唯一可推導答案。
- 單輪委派 `/clarify` 時，最多只帶 1 至 3 題；整個 clarify session 累計不得超過 5 題。
- 若高影響缺口超過 3 題，應先保留排序最高的 1 至 3 題，其餘列為 deferred 高風險缺口，在完成回報中明示，不可一次傾倒所有問題。

## Good Example

- 這個例子是好的，因為它先挑真正會扭轉後續規劃的缺口。

```md
候選提問排序：
1. 首位出牌規則：會改變對戰流程與驗收
2. 對戰中斷線處置：會改變狀態轉換與勝負邊界
3. 即時同步延遲門檻：會改變 NFR 驗證
4. 房間列表顯示樣式：defer
```

## Bad Example

- 這個例子是壞的，因為它沒有排序邏輯，也沒有控制題數。

```md
看到缺口就全部問：
1. 先手規則
2. 斷線處置
3. 延遲門檻
4. 錯誤文案
5. 房間命名
6. 提示顏色
```

# Rule 4 - 不為提問而提問，已足夠清楚時直接進回寫或回報

- Level: `SHOULD`
- 若 spec 雖有局部未定細節，但已不足以改變高影響判斷，則不應再委派 `/clarify`，而應直接保留為假設、`NEEDS CLARIFICATION` 或 deferred 風險。
- 若本輪掃描後所有高影響類別皆已 `Clear`，應直接跳過 `/clarify`，進入回驗與完成回報。
- 若缺口雖存在，但答案更適合由後續研究、技術方案或 planner skill 決定，也應在完成回報中明示 defer 理由，而不是提早把規劃問題偽裝成需求澄清。

## Good Example

- 這個例子是好的，因為它辨識出低風險未定細節不值得打斷流程。

```md
觀察：
- 主要流程、驗收與 NFR 已足夠清楚
- 僅剩房間列表呈現細節未定

決策：
- 不進 `/clarify`
- 在完成回報中列為低風險 deferred
```

## Bad Example

- 這個例子是壞的，因為它把所有未定細節都當成必問問題。

```md
觀察：
- 只剩低風險 UI 細節未定

決策：
- 仍要求進 `/clarify` 再問 3 題
```
