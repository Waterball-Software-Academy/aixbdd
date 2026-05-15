# DSL 禁止自生（precision keystone）

DSL synthesis 過程中，下列**五類**內容只要在 atomic rule／activity／contract／data 中找不到對應出處，**就視為自生、不得收下**。命中任一類即 STOP；**禁止**寫弱 placeholder DSL 讓下游 `/aibdd-spec-by-example-analyze` 自行用 CiC(GAP) bypass。

### 1. 動詞與介面詞

atomic rule 用業務動詞時，L1 不得自長 HTTP method／API verb／status code／路徑樣式作 placeholder。

- ✗ rule 寫「建立會員資料」，L1 寫 **「`POST /members` 回傳 `{狀態碼}`」**
- ✓ rule 寫「建立會員資料」，L1 寫 **「使用者建立會員資料 `{會員 ID}`」**；method／path 由 contract 透過 `L4.source_refs.contracts` anchor，**不入** L1

### 2. 數值與技術欄位

rule 未提之數字／欄位——SLA、retry、timeout、版本號、過期時間、上下限、通道（email／SMS）——DSL 不得自填 placeholder 或 default value。

- ✗ rule 寫「失敗會通知使用者」，DSL 綁 `{重試次數: 3}`／`default: 通道=email`
- ✗ rule 寫「金額不可為負」，DSL 補 `{金額上限: 100000}`
- ✓ rule 寫「失敗會通知使用者」，DSL 只綁 `{通知對象}` 之 assertion，retry／通道留待 rule 明示後再加

### 3. 隱性前提

rule 未寫之前置條件（先登入、先 KYC、先綁定信用卡）不得被 DSL 自加 `Given` 步驟。

- ✗ rule 寫「會員可下單」，DSL 加 `Given 該會員已通過 KYC`
- ✓ rule 寫「會員可下單」，DSL 只 `Given 會員 {會員 ID} 存在`，KYC／信用綁定**不**自加

### 4. 與原文衝突的語氣（hedging）

rule 用「必須／不得／一律／僅」時，DSL 之 expected value 不得弱化為「通常」「視情況」「可能」。

- ✗ rule 寫「**必須**通過二階段驗證」，DSL assertion 寫 `通常會通過二階段驗證`
- ✓ rule 寫「**必須**通過二階段驗證」，DSL assertion `Then 系統應已通過二階段驗證`

### 5. 同 boundary 內部協作者作 mock target

rule 未提之 internal mock／spy 不得列入 DSL `external-stub` entry；只有跨 boundary 之 provider edge 才能 stub。

- ✗ rule 寫「金流失敗則回滾」，DSL external-stub 對同 boundary 之 `PaymentRepository` 開 stub
- ✓ rule 寫「金流失敗則回滾」，DSL external-stub 指 3rd-party 金流 provider；`PaymentRepository` 為內部協作者，**不**stub

---

凡命中任一類即視為「自生 DSL」，**禁止**寫進 registry；應回頭 `DELEGATE /clarify-loop`（profile=`aibdd-plan`，phase=`dsl-self-gen-gap`）由 Discovery owner 補真相後再續跑。
