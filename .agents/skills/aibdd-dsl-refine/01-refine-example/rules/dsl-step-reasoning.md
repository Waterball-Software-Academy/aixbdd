# dsl step 推理分析（合理性優先，閘門式）

前提：`.feature`（SBE 產出）**不是 SSOT**，而是「待驗證的候選」。每個尚未定義（未標 `# done`）的業務 step
都先驗證它本身的測試意圖與合理性，**確認正確後才推理 isa_step**。
【硬規則】絕不在不正確的 step 上推理 isa——前置閘門沒過就先變更 step，不得硬展開 isa。

順序固定：測試意圖 → 合理性判定 → 變更判定 →（閘門）→ isa 推理。

## 1. 測試意圖分析

對該 example 讀出：
- 角色與意圖：前置（Given 建什麼狀態）／動作（When 觸發什麼操作）／斷言（Then 驗什麼結果）。
- 類型：happy / negative / idempotency。
- 與所屬 `Rule:` 的關係：在驗該 atomic rule 的哪一面？預期結果與 negative 條件為何。

## 2. 合理性判定（五類，任一不過即「不合理」）

### A. Step 合理性（每一句）
- **能對到後端**：該句能對到 ≥1 個後端 isa 操作（內建型別或合理 custom）；對不到任何後端操作（純 UI／太空泛）→ 不合規。
- **有意義**：對驗證本 example 的測試意圖有貢獻；非贅述、非與 Rule 無關鋪陳、非重複前一步。
- **單一職責**：一句不混多個無關 isa 操作（該拆）；一個操作不被拆成多句不自足（該併）。
  （註：When 可含「預期的連續動作」，不視為違規。）
- **資料自足**：句子帶的資料足以判斷 payload；空泛如「其餘欄位皆已填寫」不自足。

### B. 前置完整性（整個 example）
- **資料前置**：When/Then 引用的實體／識別碼，有前置 Given 建立（entity_setup 或前置 api_call 捕獲）。
- **身分前置**：需要 UID 的 api_call，actor 有前置 Given 準備並捕獲 id。
- **時間前置**：Then 有時間斷言或結果時間相依 → 需要前置 TimeControl（「現在時間為 …」）。

### C. VAR 變數鏈
- 每個 `$alias` 引用，前面都要有對應的 `>alias` 捕獲（或前置實體建立）；懸空引用 → 不合規。

### D. 與 Rule 一致
- 真的在驗所屬 `Rule:`，且覆蓋到該 Rule 的條件；跑題、或漏掉 Rule 的條件 → 不合規。

### E. Then 斷言
- **驗到真正結果**：情境需要時不只驗 API 回應，要驗資料落地（entity_validate）或不存在（entity_non_existence）。
- **失敗語意要對（依測試情境判斷）**：若情境就是要驗某個特定失敗（如權限不足 401、衝突 409…），用明確／獨立的 DSL step 語意表達；若只是通用驗證失敗（400 類），通用「沒成功 + 訊息」即可。不可把有意義的失敗一律塞成「沒成功」。
- **禁空斷言**：Then 不可只說「操作成功」卻沒驗具體狀態。

## 3. 變更判定

- 全部合理 → 通過閘門，進第 4 步。
- 任一不合理 → 此 step **需變更**；變更類型擇一或並用，並以**完整 Example** 經 `/clarify-loop` 確認後才改 `.feature`：
  - **重寫**：讓句子自足、意圖清楚。
  - **拆**：一句混多無關操作 → 拆成數句。
  - **併**：一個操作被拆散 → 併成自足句（見 [feature-restructure.md](feature-restructure.md)）。
  - **補前置 Given**：補資料／身分／時間前置。
  - **對齊 Rule**：修正跑題或漏條件。
- 確認前不得逕改，更不得在未改的錯 step 上推 isa。

## 4. 閘門 → isa 推理

step 確認正確後，才依下列規則推出有序 isa_steps：
- 型別：[builtin-instruction-decision-tree.md](builtin-instruction-decision-tree.md)
- 符號：[symbol-system-usage.md](symbol-system-usage.md)
- 非內建：[custom-isa-placement.md](custom-isa-placement.md)

## Good

```text
step：Given "Alice" 準備一筆資料齊全的訂單   ← 空泛、不自足（A 不過）
→ 不在此句硬塞 entity_setup；以完整 example 經 clarify-loop 問使用者
→ 確認後併成自足句「When "Alice" 送出收件地址留空、其餘必填欄位皆已填的訂單」
→ step 正確 → 才推 isa（api_call body 缺收件地址 + response_validate 失敗）
```

## Bad

```text
- 不審查，直接把空泛句硬當 entity_setup 塞假資料就往下推 isa。
- 在跟所屬 Rule 對不上的 step 上推一堆 isa_steps（建在錯前提）。
- 把「權限不足」這種有意義的失敗一律塞成通用「沒成功」，丟失測試情境。
- 引用 $order.id 但前面沒有任何 step 捕獲它（VAR 鏈斷裂）就往下推。
```
