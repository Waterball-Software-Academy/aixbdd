# Atomic Rule — Definition

跨 skill 共用的 invariant：何謂「原子規則 (atomic rule)」。本檔為 Subagent semantic validator 與各 Planner 引用的唯一權威。

---

## §定義

**Atomic rule** 是**單一斷言**、**單一事實**、**不可再拆**的規章單元。滿足以下全部條件：

1. **單一主體（Who）**：句子主詞明確，不含「某些人 / 相關者」模糊指涉
2. **單一受體（to Whom / on What）**：動作對象明確，不含並列多目標（除非並列目標是不可分離的事實，如「系統同時寫入 A 與 B」）
3. **單一動作（Does What）**：一個動詞，不含「且」「並」「同時」等連詞串接的多動作
4. **單一條件（Under What）**：前件單一（必要時以 AND 合取，但不得隱藏多路分岔）
5. **單一後果（With What Consequence）**：後件單一（成功 / 失敗其一；不得在同句同時聲明兩種後果）

> **語義判定**優先於語法判定。「且」不必然代表複合；「，」也可能暗藏分岔。以**第一性原則**拆到不可再拆為止。

---

## §判定準則

### 五問自檢

對任一 rule 句，逐問下列五問；任一答不出或答案含糊即為**非原子**：

| 問 | 檢查目標 |
|---|---|
| 1. 誰（Who）| 主體是否單一且明確 |
| 2. 對誰 / 對什麼（Whom / What）| 受體是否單一 |
| 3. 做什麼（Does）| 動作是否單一 |
| 4. 何時 / 在何條件下（When / Under）| 前件是否單一 |
| 5. 結果是什麼（Consequence）| 後件是否單一 |

### 第一性原則（顆粒度下界）

拆到無法再拆的最小斷言；再拆一次會破壞語意完整性（例如拆掉主語 / 拆掉動詞）時，即為原子。

> **警告**：顆粒度不是越細越好。拆過頭會讓 rule 喪失可驗收性（單獨無法寫出 example 覆蓋）。下界是「可獨立產出 ≥1 個 BDD Example」。

### must / should / shall 不得藏 comment

表達規章強度的 modal 動詞（must / should / shall / may / must not）**不得**被寫成註解 / 旁註 / 括弧；必須位於主句動詞位置或使其成為可驗收的正文。

- ❌ `系統記錄登入事件（必要時加上 IP）`
- ✅ `系統 MUST 記錄登入事件。`
- ✅ `當啟用稽核時，系統 MUST 記錄 IP。`

---

## §反例

### 典型複合 rule

| 複合 rule | 違反準則 | 拆分結果 |
|---|---|---|
| 「使用者登入成功**後**，系統記錄時間**並**發送通知」 | 單一動作（記錄 + 發送） | R1: 登入成功後記錄時間；R2: 登入成功後發送通知 |
| 「**管理員或老師**可停課」 | 單一主體（並列主語） | R1: 管理員可停課；R2: 老師可停課 |
| 「下單**且**庫存足夠時扣庫存**否則**拒單」 | 單一條件 + 單一後果 | R1: 下單 AND 庫存足夠 → 扣庫存；R2: 下單 AND 庫存不足 → 拒單 |
| 「系統檢核格式，**若**失敗回 400」 | 兩句隱藏：檢核動作 + 錯誤回應 | R1: 系統 MUST 檢核格式；R2: 格式錯誤 → 回 400 |
| 「通知可走 email**或** SMS（依設定）」 | 路徑分岔藏在括弧 | R1: 設定=email → 寄 email；R2: 設定=sms → 發 SMS |

### 注意的邊界情形

- **不可分離並列動作**（如「系統同時寫入 A 與 B 以保證 atomicity」）：當並列動作的**同時性本身是待驗收事實**，可保留單一 rule，但 rule 文字必須明確點出 atomic 語意。
- **隱性前件**（「系統記錄登入」沒講「當使用者登入成功」）：須補完前件再拆；原句不達原子。

---

## §規則常數（Invariant Value） vs. Example Data

Rule 中出現的「值」分兩類，處置不同：

| 類別 | 定義 | 判定 | 處置 |
|------|------|------|------|
| **規則常數（Invariant Value）** | 值本身即規則語意 | 「把此值改掉，這條 Rule 是否還成立？」答 **No** | **必須** 保留於 Rule |
| **Example Data** | 值僅為某次觀察 / 測試之具象化 | 同上問題答 **Yes** | **不得** 寫入 Rule；移至 Scenario / Examples |

### 規則常數（保留於 Rule）

- ✅「夜店 應 禁止未滿 **18 歲** 之人入場」— 改成 16 即非此 Rule
- ✅「信用卡 / LinePay 付款 應 預留庫存（**TTL = 15 分鐘**）」— TTL 數值即政策
- ✅「scheduled-tick 觸發（cron `*/1 * * * *`）時」— cron 即 trigger signature
- ✅「郵遞區號 必須 為 **3 碼** 或 **5 碼**」— 位數即資料格式契約
- ✅「付款方式 ∈ {信用卡, LinePay, 銀行轉帳}」— 枚舉即規則域

### Example Data（移至 Examples）

- ❌「使用者輸入優惠券 `"SUMMER20"` 時 → 折抵 200 元」— 特定碼 / 特定金額為測資
- ❌「訂單 id 為 `A001` 時 → 狀態轉 paid」— 特定 id 為測資

### 五問自檢的第 6 問

| 問 | 檢查 |
|---|---|
| 6. 值是否為常數（Invariant）| Rule 中之具體數字 / 列舉 / 正則，改之後 Rule 是否仍成立？ |

- 答「**不成立**」→ 規則常數，保留於 Rule
- 答「**仍成立**」→ Example Data，移至 Examples

---

## §驗證

Subagent semantic validator 於 Step 5b（Quality Gate）直接引用本檔判定：

### Checklist（最小集）

- [ ] 每條 rule 通過五問自檢
- [ ] 無「且 / 並 / 同時 / 以及」串接多動作（例外須於 rule 文末註明 atomicity 理由）
- [ ] 無「或 / 以及 / 與」串接多主體 / 多路徑分岔
- [ ] modal 動詞（must / should / shall）位於主句動詞位置
- [ ] 每條 rule 可獨立產出 ≥ 1 個 BDD Example

### Violation 標記

判定為非原子時，validator 產生便條紙 KIND=`CON`（衝突），payload 欄位：

```yaml
kind: CON
rule_path: "features/<feature>.feature:<line>"
violation: "composite-action | composite-subject | composite-branch | hidden-modality"
proposed_split: ["R1: ...", "R2: ..."]
```

由 Planner Step 4（clarify-loop）主持 user confirm 後落地拆分。
