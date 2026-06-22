# Cucumber 可跑字面格式

- 本檔定義寫入 `.feature` 的 Example 字面格式，目標是 Cucumber／Behave 等 runner 能解析並對上 step definition 參數。
- 業務語言語意依 `aibdd-spec-by-example/rules/business-language-judgments.md`；本檔只管字面怎麼寫。
- 檢核時機：在草稿收斂步驟讀本檔對草稿 Example ASSERT；草擬產出形狀以各 pattern template `## Good` 為準。
- 本資料夾檢核邊界（各管一塊、不重疊、不互補檢）：本檔只管 cucumber 可跑字面，包含 ASCII 引號、Data Table、`Given/When/Then/And` 縮排、佔位符引號、step 句型收斂；版面／類型前綴／空行由 `aibdd-spec-by-example/rules/formatter-rules.md` 管；各 pattern 必填元素由 `aibdd-spec-by-example/reasoning/derive-findings.md` 與各 pattern template 管。

## 必守不變式

1. 可綁定參數（人物名、業務序號、訊息全文、券名等）必須以 ASCII 雙引號 `"..."` 包住；數字（金額、數量、次數等）一律裸寫、不加引號。
2. 禁止用全形書名號「」包住 step 參數（`系統提示「...」` 不可；改 `系統提示 "..."`）。
3. `Given`、`When`、`Then`、`And` 四者關鍵字左側縮排必須相同（同一 Example 內）；禁止只在 `Then` 底下把 `And` 再多縮一層。
4. `Rule` 與 `Example` 之間至少一空行；`Example` 與第一個 `Given` 之間不插空行；`Given`／`When`／`Then`／`And` 之間不插空行。
5. Data Table（若使用）每個 cell 內的可綁定值不得加 ASCII 雙引號，包含人物名、業務序號、金額數字、訊息全文、優惠券名、英文技術 ID。
6. 單一 `Given`／`When`／`Then`／`And` 句型若需要承載超過 4 個可綁定參數，必須改為「step 句尾冒號 + Data Table」；禁止把 5 個以上參數全部塞在同一行 step。
7. 佔位符（角括號形式，如 `<業務狀態>`、`<$event 業務化通知>`、`<業務面新狀態>`、`<業務面回應內容>`、`<$aggregate>`）只要落在可綁定參數位置，就必須與具體值一樣以 ASCII 雙引號包住：寫 `"<業務狀態>"`、`"<$event 業務化通知>"`；禁止裸寫 `<業務狀態>`。模板骨架與替換後的最終 Example 皆適用，確保替換成具體值後引號仍在。
8. step 句型收斂：每個 `Given`／`When`／`Then`／`And` 只用單一、直述、可綁定的業務句型；禁止在 step 句尾用括號補一段否定或狀態註記（如 `... 仍是處理中（沒被折抵）`）。需表達「某結果未發生」時，改用既有不變斷言句型（`<aggregate> 維持 "<原狀態>"` 或 `<aggregate> 沒被改動`），不得新造括號否定句增加句型數量。

## 參數加引號範圍

- 必加引號: 非 Data Table step 行內的人物名、訂單／券等業務序號、系統提示全文、優惠券名、業務狀態值、英文技術 ID（若保留）。
- 不加引號: 非 Data Table step 行內的數字（金額、數量、次數等），一律裸寫。
- 禁止加引號: Data Table cell 內的人物名、業務序號、金額數字、系統提示全文、優惠券名、英文技術 ID；cell 內容視為已結構化資料，不再用引號標記參數邊界。
- 佔位符同等對待: 角括號佔位符若位於可綁定參數位置，視同具體值一律加引號（`"<業務狀態>"`、`"<$event 業務化通知>"`、`"<$aggregate>"`）；唯一例外是 Data Table cell 內，比照具體值不加引號。
- 可不加重複引號: 固定中文連接詞（顧客、有一筆、元）；非 Data Table step 行中不確定時一律加引號。

## Data Table 使用時機

- 可綁定參數計數: 以 step definition 可能擷取的值計算，包含人物名、業務序號、金額數字、系統提示全文、優惠券名、英文技術 ID、狀態值；固定中文連接詞不計入。
- 4 個以內: 可維持單行 step，但仍須保持業務語言與 ASCII 引號。
- 超過 4 個: step 行只保留動作或查詢語意，資料欄位放入緊接其後的 Data Table。
- Data Table 承載的可綁定參數不設上限；SBE 只要求欄位具備業務語言與可讀性，不以欄位數量裁切範例。
- Data Table 欄位名稱必須是業務語言，禁止 JSON key、DTO field、HTTP body 欄位名。
- Data Table cell 不使用 ASCII 雙引號；例如 `2406KX8Q7M2P9T`、`1000 元`、`Alice`。

## Data Table 示範

```gherkin
Then  "Alice" 看到訂單摘要：
  | 訂單           | 狀態   | 商品總額 | 折抵金額 | 應付金額 |
  | 2406KX8Q7M2P9T | 處理中 | 1000 元  | 100 元   | 900 元   |
```

## 可跑示範

```gherkin
Rule: 前置（參數） - 結帳必須先選擇要結帳的訂單

  Example: "Alice" 按下結帳但沒選訂單，結帳沒成功
    Given 顧客 "Alice" 有一筆處理中的訂單 "2406KX8Q7M2P9T"，金額 1000 元
    When  "Alice" 按下結帳，但沒選擇要結帳哪一筆訂單
    Then  結帳沒有成功
    And 系統提示 "請選擇要結帳的訂單"
    And 訂單 "2406KX8Q7M2P9T" 仍是 "處理中"
```

## 不可跑（檢核必標 failure）

```gherkin
  Example: Alice 按下結帳但沒選訂單，結帳沒成功
    Given 顧客 Alice 有一筆處理中的訂單 2406KX8Q7M2P9T，金額 1000 元
    Then  結帳沒有成功
      And 系統提示「請選擇要結帳的訂單」
    And 訂單 2406KX8Q7M2P9T 仍是處理中（沒被折抵）
    And <$aggregate> 變成 已結帳
```

- 缺 ASCII 引號；`And` 多縮排；訊息用「」。
- 句尾以 `（沒被折抵）` 補否定註記（違反不變式 8）；應改為 `And 訂單 "2406KX8Q7M2P9T" 維持 "處理中"`。
- 佔位符 `<$aggregate>` 裸寫未加引號、且新狀態 `已結帳` 未加引號（違反不變式 7）；應為 `And "<$aggregate>" 變成 "已結帳"`。

## 檢核程序

1. 掃描非 Data Table 的 step 行是否出現未加引號的 `2406KX8Q7M2P9T`、`Alice`（緊鄰業務動詞或標點者視為缺引號）。
2. 是否出現 `「` 或 `」` 於 step 行（註解 `#` 行除外）。
3. `Then` 之後的 `And` 是否比 `Given` 多縮排 2 個以上空格（同一 Example 內比對關鍵字左緣）。
4. 計算每一行 `Given`／`When`／`Then`／`And` 內的可綁定參數數量；若同一行超過 4 個，標記為 high-arity step 違規，必須改成 step 句尾冒號並把資料移入下一段 Data Table。
5. 檢查 Data Table cell 是否包含 ASCII 雙引號；若出現 `"..."`，標記為 datatable quoted cell 違規。
6. 掃描非 Data Table 的 step 行是否出現未加引號的角括號佔位符（緊鄰業務動詞或標點的 `<...>`，如 `<業務狀態>`、`<$event 業務化通知>`、`<$aggregate>`）；缺引號者標記為 unquoted placeholder 違規。
7. 掃描 step 行尾是否以全形括號補否定／狀態註記（如 `（沒被折抵）`、`（未改動）`）；出現者標記為 parenthetical negation 違規，要求改用 `維持 "<原狀態>"` 或 `沒被改動` 等既有不變斷言句型。
8. 違規逐條併入 `$NEED_TO_FIX`；禁止只記「格式錯誤」。
