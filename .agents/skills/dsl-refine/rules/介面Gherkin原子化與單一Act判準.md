# Rule 1 - Acceptance Journey 必須拆成介面層原子規則

- Level: `MUST`
- `features/acceptance/**` 可以用多步驟 Journey 表達完整業務驗收；`features/{介面名稱}/**` 不得原樣複製該流程顆粒度。
- 應逐一抽出 Journey 中的業務結果、失敗不變條件與介面可觀察結果，分派給真正負責的介面，再各自形成可獨立執行的 Rule。
- 同一組 Given / When 重複出現在不同 Rule 是可接受的測試隔離成本，不得為了去重而把多個規則重新串成流程。

## Good Example

- 這個例子把一次三連猜 Journey 拆成三個可獨立失敗的介面規則。

```gherkin
Rule: 有效三連猜必須一次回傳三次計分結果
Rule: 未猜中的三連猜只會把回合交給對手一次
Rule: 對局未結束前不得揭露對手密文
```

## Bad Example

- 這個例子把出手、非當前回合拒絕、對手單次猜測與再次出手全部串在同一個 Example。

```gherkin
Rule: 三連猜完整流程
  Example: Alice 三連猜後 Bob 單次猜測
    When "Alice" 送出三連猜
    Then 現在輪到 "Bob"
    When "Bob" 送出單次猜測
    Then 現在輪到 "Alice"
```

# Rule 2 - 每個 Rule 只能驗證一個可獨立成立的面向

- Level: `MUST`
- 若某個預期結果可以在另一個結果仍成立時單獨失敗，兩者就是不同驗證面向，必須拆成不同 Rule。
- Rule 標題若同時包含成功與失敗、接受與拒絕、呈現結果與狀態不變、歷史寫入與回合切換，通常表示仍可再拆。
- 多個 Then / And 只有在共同證明同一業務事實時才可留在同一 Rule；不得因為共用一次操作，就把所有後續結果塞進同一案例。
- 可用下列問題檢查：只改壞其中一個結果時，這個 Rule 是否仍可能通過？若答案是「是」，就應拆分。

## Good Example

- 對局結束與勝者共同證明「任一 4A 讓出手玩家獲勝」這一個面向。

```gherkin
Rule: 三連猜中任一 4A 都會讓出手玩家獲勝
  Example: Alice 的第一個猜測得到 4A
    When "Alice" 送出包含 4A 的三連猜
    Then 對局已結束
    And "Alice" 獲勝
```

## Bad Example

- 一次公布、歷史分組、換手、密文保護與非當前回合拒絕都能獨立失敗，不是一個面向。

```gherkin
Rule: 三連猜會公布結果且寫入歷史並換手，也會保護密文與拒絕其他玩家
```

# Rule 3 - 每個 Example 必須恰好只有一個 Act

- Level: `MUST`
- 每個 Example 必須恰好出現一個 `When`，代表本案例唯一受測的業務動作。
- 後端案例的一個 Act 通常對應一次命令或一次查詢；不得在同一 Example 連續呼叫第二個受測命令。
- 前端案例的一個 Act 通常對應一次會觸發受測結果的使用者操作；輸入資料並按一次送出可收斂成一句業務 When，但送出後不得再刷新、重送或切換模式繼續另一段流程。
- 若 Rule 驗證初始畫面呈現，開啟畫面可以是唯一 Act；若 Rule 驗證送出操作，畫面已開啟應改由 Given 準備。

## Good Example

- 只有一次三連猜送出，其他步驟是 Arrange 與 Assert。

```gherkin
Example: Alice 依序送出三種組合
  Given "Alice" 與 "Bob" 的對戰已開局，目前輪到 "Alice"
  When "Alice" 選擇使用三連猜，並一次送出以下三次猜測：
    | 順序 | 猜測 |
    | 1    | 1234 |
    | 2    | 5678 |
    | 3    | 9012 |
  Then 這次三連猜一次回傳三次結果
```

## Bad Example

- 同一 Example 先送三連猜，再讓對手送單次猜測，包含兩個 Act。

```gherkin
When "Alice" 送出三連猜
Then 現在輪到 "Bob"
When "Bob" 送出單次猜測 "1234"
Then 現在輪到 "Alice"
```

# Rule 4 - 不得用動作型 And 隱藏第二個 Act

- Level: `MUST`
- `And` 會繼承前一個 Gherkin 關鍵字的語意；接在 When 後且會改變系統狀態的 And，仍是第二個 Act，不因沒有寫出第二個 `When` 就合格。
- 出現「再次送出」「重新查看」「刷新」「切換後送出」「另一位玩家操作」「重試」「改走另一種操作」等行為時，預設視為新的 Act。
- 接在 Then 後的 And 只能是斷言；若它會送出命令、操作畫面或推進狀態，必須拆成另一個 Example。
- DataTable 只是同一動作的輸入或輸出，不會自行形成第二個 Act。

## Good Example

- Then 後的 And 共同證明同一個獲勝結果，沒有再次操作。

```gherkin
When "Alice" 送出包含 4A 的三連猜
Then 對局已結束
And "Alice" 獲勝
```

## Bad Example

- 「重新查看」是新的業務動作，被錯誤藏在 And。

```gherkin
When "Alice" 送出三連猜
Then 訂單摘要已更新
And "Alice" 重新查看摘要
Then 摘要仍然一致
```

# Rule 5 - Journey 前序操作必須轉成已完成的 Given 狀態

- Level: `MUST`
- 若欲驗證 Journey 後段動作，先前操作的結果應改寫成 Given 的已完成業務狀態，不得在同一 Example 實際重演前序 Act。
- Given 必須描述 PM 可理解的狀態，例如「剛有一批三連猜被整批拒絕，目前仍輪到 Alice」，不得暴露 fixture、endpoint、selector 或 helper。
- 前序結果若本身也是受測面向，應另有自己的 Rule；轉成 Given 不代表可以漏掉其獨立覆蓋。
- Given 不得偷渡本案例真正要驗證的目標 Act；目標操作仍必須留在唯一 When。

## Good Example

- 先前的拒絕已成為 Arrange，本案例只驗證一次重試。

```gherkin
Example: Alice 修正後重新送出
  Given "Alice" 剛有一批三連猜被整批拒絕，目前仍輪到 "Alice"
  When "Alice" 送出三次合法猜測
  Then 這次三連猜被接受
```

## Bad Example

- 本案例先製造拒絕，再重試，實際包含兩個受測動作。

```gherkin
When "Alice" 送出不合法的三連猜
Then 這次三連猜被拒絕
When "Alice" 修正後重新送出
Then 這次三連猜被接受
```

# Rule 6 - 原子化不得遺失或擴張 Acceptance 契約

- Level: `MUST`
- 拆分前應盤點 acceptance 的每個業務結果、失敗不變條件與跨視角結果；拆分後必須至少由一個相關介面 Rule 承接。
- 不要求每個介面重複全部結果；前端只承接可操作與可觀察責任，後端承接命令、權威狀態與契約責任，其他介面依分析產物分派。
- 不得為了讓原子案例看起來完整而自行增加 acceptance 未要求的限制、錯誤結果或技術行為。
- 拆分後每個 Example 都必須能獨立 Arrange，不得依賴前一個 Example 執行完成。

## Good Example

- 同一 acceptance 結果依責任分派，且整體仍完整覆蓋。

```gherkin
# frontend
Rule: 非自己回合時兩種出手操作都必須停用

# backend
Rule: 非當前回合玩家不得送出三連猜
Rule: 非當前回合玩家的三連猜不得新增歷史
Rule: 非當前回合玩家的三連猜不得改變回合
```

## Bad Example

- 只留下畫面停用，漏掉 acceptance 明定的歷史與回合不變。

```gherkin
Rule: 非自己回合時按鈕必須停用
```

# Rule 7 - 結構收斂必須逐項通過原子化檢查

- Level: `MUST`
- 交付前逐一檢查：
  - 每個 Rule 標題是否只陳述一個可獨立成立的結果。
  - 每個 Example 是否恰好一個 `When`。
  - When 或 Then 後是否存在會推進狀態的動作型 And。
  - Journey 前序操作是否已改為可獨立建立的 Given 狀態。
  - 多個 Then / And 是否只共同證明同一驗證面向。
  - 拆分後是否仍覆蓋 acceptance 的所有結果與失敗不變條件。
  - 每個新增 Given / When / Then 是否都有同介面的 DSL 定義。
- 任一項失敗都必須先修正 feature files 與 `dsl.md`，不得宣告可交給測試實作。

## Good Example

- 檢查結果能逐項指出通過證據。

```md
- Rule：每個標題只有一個結果
- Example / When：21 / 21
- 動作型 And：0
- Acceptance 結果：全部由至少一個介面承接
- DSL 缺口：0
```

## Bad Example

- 只確認 Gherkin 能解析，沒有檢查測試顆粒度與契約覆蓋。

```md
- feature 檔案沒有語法錯誤，因此可交付
```

# Rule 8 - 參考範例不得覆寫本 RuleFile 的原子化要求

- Level: `MUST`
- `gherkin-and-dsl` 的範例可用來理解業務語言、切檔、DataTable 與 DSL 完成樣貌，但不得用其中的流程型 Example 覆寫本 RuleFile。
- 若參考範例含有第二個 When、動作型 And 或可再拆的 Rule，應只沿用不衝突的部分，並依本 RuleFile 重構後再使用。
- 參考範例不是 acceptance 權威，也不是放寬介面測試顆粒度的例外來源。

## Good Example

- 只沿用參考範例的表格與句型風格，案例仍維持單一 Act。

```gherkin
Example: 折後商品金額 950 時顯示運費 60
  Given 訂單已成功套用折扣碼，折後商品金額為 950
  When "Alice" 查看結帳頁摘要
  Then 結帳頁顯示運費 60
```

## Bad Example

- 因參考範例曾出現重新查看，就在同一 Example 保留第二個 When。

```gherkin
When "Alice" 套用折扣碼
Then 結帳頁顯示運費 60
When "Alice" 重新查看結帳頁摘要
Then 結帳頁仍顯示運費 60
```
