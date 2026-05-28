# Shared Given Law (web-service)

1. 本檔是 web-service boundary 中所有 rule type 共用的 `Given Block` construction law SSOT。
2. 本檔只承載 web-service boundary 所有 rule type 共用的 `Given Block` construction law。
3. rule-type-specific `Given Delta` 一律拆到 sibling `given-delta-*.md`；不得把 delta 直接混回本檔。

## Given Block

針對 Given Block，請遵照 Decision Tree 一步一步推理來選擇適當的 DSL 編排方式。

### Decision Tree
1. 是否存在一段短 upstream journey，能自然把系統帶到接近目標狀態？
   1. 定義：`upstream journey` 指的是一串在業務語意上發生於當前 `When` 之前的上游操作；這些操作本來就會把系統逐步帶到某個接近受測前置的狀態，而不是為了測試方便臨時拼出的不自然 setup。
   2. `短` 的意思是：通常為 `1..3` 條 `operation-invoke` steps，且每一步都仍與當前 rule 的 failure source 或直接語意關聯；若再往前 replay 只會引入無關流程，則不算短。
   3. 判準：若把這段 journey replay 完，讀者能自然理解系統目前「停在什麼階段、還差哪個前置」，就算存在可用的 upstream journey。
   4. 電商 Gherkin 例子：
      ```gherkin
      Given 顧客 {顧客} 建立購物車 {購物車}
      And 購物車 {購物車} 已加入商品 {商品}
      And 顧客 {顧客} 送出訂單 {訂單}
      When 顧客 {顧客} 支付訂單 {訂單}
      ```
   5. 上例中的 upstream journey 就是前三條 `Given`。
      1. 它們都是 `支付訂單` 之前自然會發生的上游操作。
      2. replay 完後，系統自然停在 `pending_payment` 一類的「付款前」狀態。
      3. 這時若 rule 要測「付款前訂單必須處於待付款狀態」，就可先優先考慮 `journey-replay`。
   1. 是 → 進 2。
   2. 否 → 進 3。
2. replay 後是否已足夠清楚表達被測前置？
   1. 是 → 選 `journey-replay`。
      1. 適用：前置最自然地表達為「流程尚未走到下一階段」，且 replay 本身已能隔離 failure source。
      2. 輸出：`Given` 由 `1..*` 個 upstream `operation-invoke` steps 組成。
      3. 不選：`state-builder-snapshot`，因為它會過早抹掉 journey semantics。
      4. 不選：`hybrid-replay-plus-snapshot`，因為最後那段局部 state 並不需要額外 spotlight。
   2. 否 → 選 `hybrid-replay-plus-snapshot`。
      1. 適用：replay 已把系統帶到接近正確邊界，但最後一小段局部 state 還必須被顯式補出。
      2. 輸出：先 replay，再補 `1..*` 條 focused `state-builder` steps。
      3. 不選：純 `journey-replay`，因為讀者仍需腦補最後一段局部狀態。
3. 是否有 direct `state-builder`，可在不破壞 invariant 的前提下直接建出被測前置？
   1. 是 → 選 `state-builder-snapshot`。
      1. 適用：被測前置落在單一 aggregate，且 builder 可用少量欄位直接表達。
      2. 輸出：`Given` 由 `1..2` 條 focused `state-builder` steps 組成。
      3. 不選：`journey-replay`，因為它只會額外引入與本 rule 無關的上游旅程。
   2. 否 → 進 4。
4. 是否存在可由 truth 證明的 proxy aggregate，可穩定導出被測前置？
   1. 是 → 選 `proxy-aggregate-seeding`。
      1. 適用：沒有 direct builder，但 proxy 與被測前置條件之間的因果關係可被客觀證明。
      2. 輸出：`Given` 先建 proxy aggregate，再由其穩定導出被測前置。
   2. 否 → 視為目前沒有合法 candidate，返回上層重新檢查 candidate universe 或 rule understanding。

### Forces
1. `Given` 只能使用當前 `# candidates:` 中已存在的 `candidate_specs`。
2. 除了被測條件本身之外，其餘 dbml 中 entity/aggregate 的 invariant 必須維持合法。
   1. 意義：讀者看到 `Given` 時，應能判定這次失敗或成功主要來自被測條件，而不是來自其他 entity 本身已經壞掉。
   2. 例子：
      1. 合法 DBML 狀態可以長這樣：
         ```dbml
         Table orders {
           id text [pk]
           status text
           total_price int
         }

         Table order_items {
           id text [pk]
           order_id text [ref: > orders.id]
           unit_price int
           quantity int
           line_total int
         }
         ```
      2. 錯誤示範一：若 `訂單總價` 與所有 `訂單項目` 的 `小計` 加總對不起來，這個 `Given` 不合法。
         ```gherkin
         And 系統 預先建立 訂單 {訂單}
           | 狀態 | 訂單總價 |
           | pending_payment | 1000 |
         And 系統 預先建立 訂單項目 {訂單項目一}
           | 訂單 | 單價 | 數量 | 小計 |
           | {訂單} | 300 | 2 | 600 |
         And 系統 預先建立 訂單項目 {訂單項目}
           | 訂單 | 單價 | 數量 | 小計 |
           | {訂單} | 100 | 1 | 100 |
         ```
      3. 錯誤原因：此時 `訂單項目` 的 `小計` 加總只有 `700`，但 `訂單總價` 被寫成 `1000`；若 AI 接受這種 state-builder，就代表它沒有守住 aggregate invariant。
3. `Given` 不需要把所有 sibling precondition 都補到最完整；只要保留足以隔離當前 failure source 或 success path 所需的最小合法背景即可。
   1. 意義：`Given` 要補的是「足夠讓這條 rule 可判定」的背景，不是把同 feature 其他 rule 的合法條件一次補滿。
   2. 例子：
      1. 若只想測「訂單必須處於待付款狀態」，最小 DBML 狀態只需要把顧客、訂單、訂單項目關聯建好，並讓訂單停在 `pending_payment`；不必連物流、發票、優惠券使用紀錄一起補。
         ```dbml
         Table orders {
           id text [pk]
           customer_id text
           status text
           shipment_id text
         }
         ```
      2. 對應的 Gherkin 可以只停在：
         ```gherkin
         Given 顧客 {顧客} 建立購物車 {購物車}
         And 購物車 {購物車} 已加入商品 {商品}
         And 顧客 {顧客} 送出訂單 {訂單}
         ```
      3. 此時故意不補「物流已建立」或「付款授權已存在」，因為那是其他 sibling precondition 的負擔，不是這條 rule 的最小合法背景。
4. 若被測條件本身就是 lifecycle phase / journey stage，優先用「停在上一個自然階段」來表達，而不是為了顯式寫出 phase 值就先偏向 giant snapshot。
   1. 意義：若流程本身就能自然停在某個較早階段，優先保留那段 journey semantics，不要急著用大顆粒 snapshot 直接覆寫狀態。
   2. 例子：若要測「付款前訂單必須處於待付款狀態」，可用「顧客建立購物車 -> 加入商品 -> 送出訂單」讓系統自然停在 `pending_payment`，而不是立刻用一條 giant `orders.state-builder` 硬寫一整包訂單狀態。
5. 允許一條或多條 `Given` / `And`；若單條過胖或語意不清，優先拆成多條。
   1. 意義：step 數量不是越少越好；若拆開後更容易看出 identity 建立、journey replay、局部 state 補強各自負責什麼，就應該拆。
   2. 例子：`Given` 可拆成「顧客建立購物車」、「購物車加入商品」、「顧客送出訂單」三條，而不是把它們壓成一句需要大量腦補的超長 step。
6. `Given` 的 step shape、拆分、順序與 background reuse 也屬於 force，而不是最後才補的格式細節。
   1. step shape：第一條 step 用 `Given`，後續同一段前置建構用 `And`；每條 step 只承擔一個清楚目的，例如建 identity、replay upstream action、補局部 state、凍結時間、設定 external stub。
   2. split：若單條 `state-builder` 需要跨多 aggregate 補大量欄位，或 upstream journey 與最後局部 state 分屬不同語意責任，就必須拆成多條。
   3. ordering：`time-control` 先於所有受時間影響的 step；`external-stub` 先於依賴它的 operation；upstream replay 先於局部 snapshot；parent identity 先於 dependent aggregate。
   4. background reuse：只有在同一 `Rule` 或同一 `Scenario Outline` 下所有 examples 都共用的前置建構，才可提升成 `Background`；若會遮蔽 load-bearing precondition，則不得提升。
   5. mixed strategy：`journey-replay` 與 `state-builder-snapshot` 可以混用，但必須清楚說明 replay 部分負責什麼、snapshot 部分補什麼。

### Optimization
1. Tie-break Order
   1. `minimum cognitive load`
      1. 先選最容易讓讀者一眼看懂前置狀態如何成立的 plan。
      2. 一句過胖的 snapshot 要扣分。
   2. `natural boundary expression`
      1. 若前置最自然地表達為「流程尚未到下一階段」，優先保留能停在該自然邊界的 plan。
   3. `journey faithfulness`
      1. 若 rule 的關鍵語意來自上游旅程，優先保留必要 replay。
   4. `background reuse`
      1. 若某段前置狀態在同一 `Rule` 或 `Scenario Outline` 下穩定共用，優先可 reuse 的 plan。
   5. `minimum cardinality`
      1. 在前述條件相當時，再選步驟較少者。
   6. `state path shortest`
      1. 最後才比較從空狀態到目標狀態的路徑長度。
2. Explicit Preference
   1. 三句清楚的 `Given` / `And`，通常優於一句需要大量欄位解讀的胖 builder。
   2. 若 replay 已能自然表達「尚未進入下一階段」，優先純 replay，不要為了顯式寫 phase 值而強行補 snapshot。
   3. `hybrid-replay-plus-snapshot` 只有在 replay 無法清楚 spotlight 最後一段局部狀態時才應勝出。
   4. `proxy-aggregate-seeding` 只有在 direct strategy 都較差時才應勝出。

### Legality Gate
1. 最終 `Given` 必須讓當前 `When` 可執行，且不得偷跑當前 `When` 正在受測的主操作。
2. 所有被建出的 persisted state、required identity、FK 關聯與 aggregate invariant 都必須合法；不得依賴隱含 lookup。
3. `Given` 只能使用 `candidate_specs` 中已存在的 DSL；若採 `proxy-aggregate-seeding`，proxy 與被測前置條件的關係必須可由 truth 證明。
4. `Given` 只可補到足以隔離當前 failure source 或 success path 所需的最小合法背景；若 plan 需要讀者腦補、埋沒 load-bearing precondition、或混入過多與本 rule 無關的 setup，視為不合法。
5. `Given` 不得把當前 `When` 的主操作放回前置建構，也不得用 `Then` handler 來做前置建構。
6. `Given` 不得為了追求最少句數而隱藏必要前置語意，也不得把所有困難都推給最後一條 giant snapshot。

### Output Expectation
1. `Given` 應產出一個 `selected_plan`，將 `<dsl>` 替換為對應 step 序列，並遵守 shared precondition trace schema。

