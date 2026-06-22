# Example 疑慮分析切角

1. 目的
   1. 本檔針對當前各 rule 的草稿 Example，逐項查驗其 4 rule pattern 與 5 元素是否正確。
   2. 查驗只用兩條基準：`$template_path`（該 pattern 宣告的必填與嚴禁元素清單與骨架）與 `aibdd-spec-by-example/rules/five-elements-mapping.md`、`aibdd-spec-by-example/rules/business-language-judgments.md`。
   3. 本檔將切角分成兩類：
      1. `$NEED_TO_CLARIFY`：Example 需要的某個值無法只從 `Feature:` 及 `Rule:` 標題文字推出，需求真相不足，交給批次 clarify 補問。
      2. `$NEED_TO_FIX`：Example 已可直接判定違反 pattern 或業務語言判準，不必訪談，就地重新草擬即可。

## $NEED_TO_CLARIFY

1. 5 元素推不出
   1. 要看什麼：`$five_elements` 中該 pattern 必填的元素（四種前綴皆需 `$actor`/`$aggregate`/`$command`；後置（狀態）另需變更後狀態與 `$event`；前置（參數）另需 `$input`）是否有任一項無法從標題文字推出而被標 `null`。
   2. 需求訪談重點：用 `$template_path` 的「引導一句話」補問該缺項的業務值；依 `aibdd-spec-by-example/rules/five-elements-mapping.md`，推不出者必標 `null` 走補問，禁止自填「某顧客」「某訂單」這類 placeholder。
   3. 例：Feature／Rule 標題都沒出現觸發者，`$actor` 無法推出，補問「這個動作的觸發者是誰」。

2. 參數型別判不準（字串 vs 數值）
   1. 要看什麼：`$five_elements` 是否有參數值本身為數字、或為「可被解析為數字」的字串（如 `1000`、`3`、`001`、`0911111111`）；不論是否含前導零、不論業務角色（金額／數量／等級皆然）。只要能讀成數字就算命中。
   2. 需求訪談重點：一律補問 PM「這個欄位團隊統一當字串還是數值？」，優先提供建議選項（預設建議字串）；補問結果於整份 spec 一致沿用。
   3. 例：`會員等級 3`、`金額 1000`、`手機號 0911111111` 都能讀成數字，型別一律須補問。

3. 業務狀態值不明
   1. 要看什麼：pattern 骨架中由用戶補問填入的狀態欄位（前置（狀態）的「不合條件狀態」與「維持原狀態」、後置（狀態）的「滿足前提狀態」與「變更後新狀態」）是否能從 Rule 標題取得具體業務狀態詞。
   2. 需求訪談重點：補問該前置／後置狀態在業務上的具體名稱（中文業務詞，如「處理中」「已結帳」），避免硬填模糊狀態。
   3. 例：`後置（狀態） - 發放紀錄應建立`，但「建立後」的具體業務狀態文字 Rule 沒給，補問。

4. 系統提示／回應內容不明
   1. 要看什麼：前置（參數／狀態）的「系統提示」訊息字串、後置（回應）的「業務面回應內容」是否能從標題推出顧客實際看到的文字／欄位。
   2. 需求訪談重點：補問顧客在失敗時看到的提示訊息，或查詢成功時看到哪些欄位與值；這些依模板本就標示「用戶補問或自由文」。
   3. 例：`前置（參數） - 指定顧客必須已提供`，但「沒指定顧客」時顧客看到的提示文字 Rule 沒明說，補問。

## $NEED_TO_FIX

1. pattern 與 Example 內容不符
   1. 要看什麼：Example 的斷言形態是否與 `Rule:` 類型前綴一致：前綴是「後置（回應）」卻出現「變成…」或「系統發出…」（應為後置（狀態））；前綴是「前置（參數／狀態）」卻寫成成功變更（應為後置（狀態））。
   2. 如何修正：依宣告的類型前綴重推 `$five_elements` 並重新草擬，使 Example 形態符合該前綴模板。若依該前綴語意上根本推不出合理 Example（規則本質不屬此類），屬分類錯誤，就地更新 `$rule.pattern_label` 為正確 pattern 後重新草擬。
   3. 例：前綴 `後置（回應）` 的 Example 出現 `And 系統發出 "查詢完成通知"`，查詢不發事件，混入了後置（狀態）模板。

2. 該 pattern 必填元素缺漏
   1. 要看什麼：對照 `$template_path` 宣告的必填元素清單，逐項確認草稿每個必填元素都到位（例：前置（參數）需 `$input` 缺漏描述／系統提示／`$aggregate` 沒被改動；前置（狀態）需 `$aggregate` 維持原狀斷言；後置（狀態）需變更後狀態與 `$event` 斷言；後置（回應）需業務面回應內容）。
   2. 如何修正：依骨架補齊缺漏的 Given/When/Then 行後重新草擬。
   3. 例：後置（狀態）的 Example 只有 `Then 訂單 "2406KX8Q7M2P9T" 變成 "已結帳"`，缺 `And 系統發出 "..."` 事件斷言。

3. 嚴禁／越界元素誤入
   1. 要看什麼：後置（回應）出現狀態變更行、事件斷言或 HTTP／JSON；前置（參數／狀態）的 `$event` 不是「無」而填了通知；後置（狀態）的 `$event` 填「無」。
   2. 如何修正：越界行（多出的狀態變更／事件／技術描述）刪除後重新草擬；但後置（狀態）的 `$event` 填「無」依 `aibdd-spec-by-example/rules/five-elements-mapping.md` 屬分類錯誤，就地更新 `$rule.pattern_label` 後重新草擬。
   3. 例：後置（回應）的 Example 出現 `Then 回應 HTTP 200，body 包含 amount=900`。

4. 元素帶技術氣味（違反業務語言 5 維度）
   1. 要看什麼：依 `aibdd-spec-by-example/rules/business-language-judgments.md` 5 維度識別用技術 ID（order-001）、狀態用英文 enum（process／CHECKED_OUT）、動詞用 API 視角（執行／呼叫／POST）、結果寫「操作失敗」、`$event` 用 event class 名（OrderCheckedOut）。
   2. 如何修正：依 `aibdd-spec-by-example/rules/five-elements-mapping.md` 重推為業務語言值後重新草擬。
   3. 例：`Given 訂單 "order-001" 狀態為 "process"`，應為 `訂單 "2406KX8Q7M2P9T" 狀態為 "處理中"`。

5. 數字型別寫錯
   1. 要看什麼：身分值（業務序號 2406KX8Q7M2P9T、前導零 001、代碼、批號、電話）被裸寫成數字、或明確的金額／數量／次數被加上引號。
   2. 如何修正：依型別自問重新草擬：身分值字面加 `"..."`、大小值裸寫不加引號。
   3. 例：`折抵面額 "100" 元`（金額被加引號）應為 `折抵面額 100 元`；`發放批號 20240601`（身分）應為 `"20240601"`。

6. 資料量過載
   1. 要看什麼：Given 是否把 `$aggregate` 全欄位（含系統算出的 invariant 衍生值，如折抵金額、應付金額）都 seed 進來，而非只放與該 Rule 相關的最少欄位。
   2. 如何修正：刪去衍生值與無關欄位後重新草擬，只保留驗證本 Rule 所需的欄位。
   3. 例：Given 表格塞入「折抵金額 100」，折抵是系統算的，不該由 Given 手動 seed。

## 使用提醒

1. 同一 Example 可同時命中多個切角；不要因已歸進某一類就停止從其他角度查驗。
2. 邊界判斷：先問「是 Example 需要的值推不出（真相不足）」還是「Example 已明顯寫錯」；前者歸 `$NEED_TO_CLARIFY`，後者歸 `$NEED_TO_FIX`。
3. 若某項既推不出又被自填了 placeholder，先歸 `$NEED_TO_FIX`（刪 placeholder、標 `null`），其 `null` 缺口再由 `$NEED_TO_CLARIFY` 第 1 項補問。
