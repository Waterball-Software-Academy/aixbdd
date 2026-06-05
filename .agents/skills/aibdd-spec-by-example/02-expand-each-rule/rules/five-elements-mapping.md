# 5 元素推導規則（業務語言版）

- 5 元素必為 `Aggregate`、`Command/Query`、`Event`、`Actor`、`Input` 共五項；不得新增或合併。
- 自動推導只准用 `Feature:` 標題與 `Rule:` 標題文字；禁止讀其他 `.feature` 檔或外部資料源來猜值。
- 任何元素若無法從文字推出，必須標 `null` 並走補問流程；禁止自行擬定 placeholder（如「某顧客」「某訂單」）填入。
- 推出之元素值必為業務語言；禁止直接搬技術 ID、英文 enum、API 動詞填入。詳見 `rules/business-language-judgments.md`。
- `Event` 在前置失敗 pattern（A／B）必為「無」；後置成功 pattern（C／D）必須有業務化通知名（C）或業務化回應內容（D）。
- `Input` 在 PATTERN_A 必填；在其他 pattern 不得強加，會混淆失敗原因。

## 元素來源對應

### `$aggregate`

- 來源文字: Rule 標題主詞
- 推導方式: 抽 Rule 標題主詞（業務實體名）
- 業務化處理: 補上業務序號（訂單 #001），禁止用技術 ID（order-001）

### `$command`

- 來源文字: Feature 標題動詞
- 推導方式: 抽 Feature 中的動作動詞
- 業務化處理: 改寫成顧客視角（按下結帳），禁止 API 視角（執行結帳）

### `$actor`

- 來源文字: Feature 主題隱含角色
- 推導方式: 由業務情境推導
- 業務化處理: 用人物名（Alice），禁止技術 ID（user-001）或泛稱（使用者）

### `$event`

- 來源文字: 後置 Rule 後半段
- 推導方式: 抽 Rule「應」後的結果描述
- 業務化處理: 改寫成業務化通知名（結帳完成通知），禁止 event class 名（OrderCheckedOut）

### `$input`

- 來源文字: Rule 標題參數名
- 推導方式: 抽 Rule 中「必須」前的名詞
- 業務化處理: 用顧客視角名稱（要結帳的訂單），禁止 API 欄位名（order_id）

## Good

Feature `結帳`、Rule（前綴 `前置（參數）`）`結帳必須先選擇要結帳的訂單`：

- `$aggregate` = 訂單 #001（Rule 主詞「訂單」+ 業務序號；寫檔為 `"#001"`）
- `$command` = 按下結帳（Feature 動詞，顧客視角改寫）
- `$actor` = 顧客 Alice（情境推導 + 人物名；寫檔為 `"Alice"`）
- `$event` = 無（前置失敗）
- `$input` = 要結帳的訂單（Rule「必須」前的名詞，顧客視角）

Feature `查詢訂單`、Rule（前綴 `後置（回應）`）`成功查詢訂單應回應顧客看得到的訂單摘要`：

- `$aggregate` = 訂單 #001
- `$command` = 查詢訂單
- `$actor` = 顧客 Alice
- `$event` = 訂單摘要：金額 1000 元、折抵 100 元、應付 900 元（業務化回應內容）
- `$input` = null（PATTERN_D 不強加）

## Bad

- 看到 Rule `已結帳的訂單不能再次結帳` 卻把 `$aggregate` 填為「結帳流程」：應為「訂單」（Rule 主詞）。
- 自動推不出 `$actor` 時，填「使用者」當 placeholder：禁止；必須標 `null` 走補問。
- `$actor` 填 `user-001`：技術 ID 非業務語言；必須改為人物名（Alice）或補問用戶。
- `$aggregate` 填 `order-001`：技術 ID 非業務語言；必須改為業務序號（訂單 #001）。
- `$command` 填 `執行結帳` 或 `POST /checkout`：API 視角非業務語言；必須改為顧客視角（按下結帳）。
- `$event` 在 PATTERN_C 填 `OrderCheckedOut`：event class 名非業務語言；必須改為業務化通知（結帳完成通知）。
- PATTERN_C 的 `$event` 填「無」：後置成功必須有事件名；填無代表分類錯誤，回 phase 1 重分。
- PATTERN_A 不填 `$input`：缺 Input 等同 Pattern A 無法表達失敗原因，禁止省略。
