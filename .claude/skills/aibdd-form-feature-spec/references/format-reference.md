# Rule 撰寫指南

## Rule 命名與原子化

### 命名句型

每條 Rule 的名稱必須遵循：

```
Rule: <類型前綴> - <主詞> 必須/應 <單一條件>
```

- **類型前綴**：`前置（狀態）`、`前置（參數）`、`後置（回應）`、`後置（狀態）`。後置（狀態）可選用子類前綴：`後置（狀態：資料）`、`後置（狀態：外發）`、`後置（狀態：資源）`、`後置（狀態：行為）`
- **主詞**：一個明確的實體屬性或系統狀態
- **動詞**：前置用「必須」（約束），後置用「應」（預期結果）
- **單一條件**：一個可驗證的具體斷言

**正確：**
```
Rule: 前置（狀態）- 商品庫存必須大於 0
Rule: 前置（參數）- 加入數量必須大於 0
Rule: 後置（狀態）- 購物車應新增一筆商品項目
```

**錯誤（違反原子化）：**
```
Rule: 前置（狀態）- 商品庫存必須大於 0 且商品狀態必須為上架中
```
→ 兩個主詞、兩個條件，應拆為兩條 Rule。

**錯誤（分類標題風格）：**
```
Rule: 前置（狀態）- 購物車驗證（存在 / 上架 / 庫存）
Rule: 後置（回應）- 計算應付金額（原價 → 促銷 → 優惠券 → 運費 → 稅）
```
→ 讀起來像文件目錄的章節標題，不是可測試的斷言。缺少主詞 + 動詞 + 單一條件。應改為：
```
Rule: 前置（狀態）- 購物車中的每項商品必須存在於系統
Rule: 前置（狀態）- 購物車中的每項商品必須處於上架狀態
Rule: 前置（狀態）- 購物車中的每項商品的可用庫存必須大於等於購買數量
Rule: 後置（回應）- 應付金額應等於商品原價小計減去促銷折扣減去優惠券折扣加上運費加上稅金
```

**錯誤（Q4 不可測試 — 過程約束）：**
```
Rule: 後置（回應）- 應付金額的計算順序應為商品原價加總 → 促銷折扣 → 優惠券折扣 → 運費 → 稅金
Rule: 後置（回應）- 同商品的促銷折扣應互斥
Rule: 後置（回應）- 折扣類優惠券應不可疊加
```
→「計算順序」「互斥」「疊加規則」皆為抽象過程約束，無法寫成 `Then <主詞> 應為 <具體值>`。必須改寫為具體的結果值斷言：
```
Rule: 後置（回應）- 應付金額應等於商品原價小計減去促銷折扣減去優惠券折扣加上運費加上稅金
Rule: 後置（回應）- 商品套用的促銷折扣應為該商品所有可用促銷方案中最優惠的單一方案的折扣金額
Rule: 後置（回應）- 同一訂單同時使用兩張折扣類優惠券時應回傳錯誤訊息 "優惠券不可疊加"
```

---

### 類型前綴決策樹

依序回答五個問題，終端即為 Rule 的類型前綴。

**Q1：這條規則約束的是「動作之前必須成立」還是「動作之後必須成立」？**
- 前 → Q2
- 後 → Q3

**Q2：約束的主詞是「系統既有狀態」還是「本次請求的輸入參數」？**
- 系統既有狀態（資料庫中的資料、其他 Aggregate 的狀態）→ **前置（狀態）**
- 本次請求的輸入參數（表單欄位、API payload、URL path parameter）→ **前置（參數）**
- 分不清 → 主詞在 DB 裡查得到 → 狀態；主詞由呼叫者本次帶入 → 參數

**Q3：驗證這條規則時，只需看「本次 API 回傳值」就夠了嗎？**
- 是（回傳 body / status code / error message 就能驗完）→ **後置（回應）** → Q4
- 否（需要查 DB / event log / 外部系統才能驗）→ **後置（狀態）** → Q5

**Q4（可測試閘門）：能寫成 `Then <主詞> 應為 <具體值>` 嗎？**
- 能 → **後置（回應）** ✓
- 不能（如「互斥」「計算順序」「疊加規則」）→ ⚠ 重寫信號：將抽象過程約束轉為具體的結果值斷言（範例見上方 Q4 反例）

**Q5：系統側狀態變更的性質？**

| 判準 | 前綴 | 口訣 |
|------|------|------|
| 改資料庫紀錄（新增/修改/刪除 row） | `後置（狀態：資料）` | 改紀錄 |
| 叫第三方系統（發 email / 呼叫外部 API / 送推播） | `後置（狀態：外發）` | 叫別人家 |
| 佔用有限資源（鎖庫存 / 鎖座位 / 扣餘額） | `後置（狀態：資源）` | 佔有限東西 |
| 跑兩次才測得出差異（冪等性 / 重試策略 / 過期釋放） | `後置（狀態：行為）` | 跑兩次才測得出 |

---

### Authentication 豁免

4-rules pattern **不涵蓋**「使用者已認證」這類 actor 身分屬性。認證由 actor key binding 在 feature file 層表達（`@buyer` / `@admin` / `@logged-in-user`），不列為 Rule、不寫為 Given step。

```
❌ Rule: 前置（狀態）- 使用者必須已登入
❌ Rule: 前置（狀態）- 使用者必須持有有效 session
```

例外：流程本身為認證主題（登入 / 註冊 / 密碼重設 / MFA）時，認證即是流程 action，Rule 可正當列出認證相關條件（`前置（參數）- email 必須為合法格式`、`後置（回應）- 回應應包含 JWT token`）。

完整慣例見 `aibdd-core::authentication-binding.md`。

---

### 原子化判定

- 陳述句中出現「且」「和」「並且」→ 拆分為多條 Rule
- 陳述句中出現「或」→ 保留在同一條 Rule
- 混合前置與後置 → 拆分

### 必要參數規則（必備 + 允許合併）

每個 Feature **至少**必須有一條「前置（參數）」Rule 驗證必要參數。

所有「缺少必要參數」的檢查可合併為單一 Rule，使用 Scenario Outline：

```gherkin
Rule: 前置（參數）- 必要參數必須提供

  Scenario Outline: 缺少 <缺少參數> 時操作失敗
    Given 系統中有以下用戶：
      | userId | name  |
      | 1      | Alice |
    When 用戶 "Alice" 將商品 <商品ID> 加入購物車，數量 <數量>
    Then 操作失敗，錯誤為"必要參數未提供"

    Examples:
      | 缺少參數 | 商品ID | 數量 |
      | 商品 ID  |        | 1    |
      | 數量     | 1      |      |
```

其他具有**領域特定約束**的參數規則仍各自獨立為原子 Rule。

---

## Rule line vs Rule body 的分工

每條 Rule 由兩部分組成：**Rule line**（必填，單行）+ **Rule body**（選填，縮排 +2 spaces 的多行區塊）。Rule line 限放 prefix + 短斷言；細節與 bullet 縮排到 body。

### Rule line

Rule line 限放：

```
Rule: <類型前綴> - <主詞> 必須/應 <單一條件>
```

**不放**：細節 / bullet / 條件分歧 / 範例 / 註解。控制在約 50 個全形字以內。

### Rule body

當 Rule 的單一斷言需要展開細節時——條件分歧、bullet 列舉、具體值清單、上下文補述——把細節縮排 +2 spaces 到 Rule body：

```gherkin
Rule: 後置（狀態：行為） - 設定精靈讓工程師輸入測試指令
  工程師在精靈表單內輸入：
  - test command（例 `pnpm test`）
  - test filter pattern（例 `--filter {goalFeature}`）
  並可看到組合後的指令預覽。

Rule: 前置（狀態） - 同一時間只允許一個 active 指揮站臺 tab

Rule: 後置（狀態：行為） - 已有指揮站臺時再點「🚀」直接 focus existing tab
  工程師在已存在 active 指揮站臺時再點擊「🚀」：
  - 把既存的指揮站臺 tab 帶到前景（focus existing），不開新 tab
  - 不重置 session 進度
  - 不重設 chat scope；若右側面板當前不在 Evaluation Agent 模式則同步切回
```

中間那條 Rule（單一斷言、已自洽）**不需要 body**——能省則省。

### 何時放 body

| 該放 body | 不該放 body |
|---|---|
| 條件分歧（`若 X → A；否則 → B`） | 重複陳述 Rule line |
| Bullet 列舉（多欄位 / 多值 / 多 sub-clause） | TODO / 之後再補 / 待澄清 |
| 具體值清單（icon vocabulary、status enum、phase 序列） | 與 Rule line 主詞無關的離題補充 |
| 上下文補述（為什麼這條 Rule 存在的 1–2 句） | 實作細節（HOW，留 Plan 階段） |

---

## Gherkin dialect keyword 撞牆禁忌

description 段、Rule body、bullet 行的「行首」（縮排空白後第一個字元）**不可**撞到目前 feature 所選 Gherkin dialect 的任一 step keyword（Given / When / Then / And / But 及其 alias）。keyword set 以該 feature 的 `# language:` header 或專案 `GHERKIN_KEYWORD_DIALECT` 對應到的 Gherkin dialect 為準；來源是 @cucumber/gherkin `gherkin-languages.json`，不得在 arguments 裡另列固定黑名單。

**Prefix collision 警示**：只要行首字串以該 dialect keyword 開頭，就視為碰撞；例如 zh-TW dialect 中「`當前`」會被 parser 抓成 `當` + 後文。下列只是 zh-TW 範例，其他語言必須套用該 dialect 自己的 keyword set：

| 撞到 | 改寫 |
|---|---|
| `當 X 時 → ...` | `若 X → ...` 或 `X 時 → ...` 或 `X 發生時 → ...` |
| `當前 phase 為 RED` | `Goal 當前 phase 為 RED`（前面塞主詞讓「當」不在行首） |
| `並且 X` | `也 X` 或 `同時 X` |
| `而且 X` | `另外 X` 或 `亦 X` |
| `假設 X 不存在` | `若 X 不存在` |
| `那麼 ...` | `則 ...` 或 `會 ...` |
| `但是 ...` | `不過 ...` 或 `然而 ...` |

實作要求：

- formatter / validator 必須先解析 feature dialect，再用該 dialect 的完整 Given / When / Then / And / But keyword set 檢查 description、Rule body、bullet 行首。
- `check_discovery_phase.py` 應以 `RULE_BODY_KEYWORD_COLLISION` violation 擋下這類撞牆，且錯誤訊息必須指出命中的 dialect 與 keyword。
- zh-TW 只是其中一個 dialect，禁止把 zh-TW keyword list 寫成全域 config。

---

## Step 內變數 placeholder — 必用 ASCII 雙引號 *(NORMATIVE)*

Gherkin step 內被 step-def 捕獲為變數的字串字面值，**必須**用 ASCII 雙引號
`"..."` 包圍（對應 cucumber-expressions `{string}` parameter type）。
**禁用**任何 CJK 全形括號（`「」` / `『』` / `《》`）、ASCII 單引號 `'...'`、
反引號 `` `...` ``，無論寫的是中文或英文內容。

CJK 全形括號 `「」` 雖然也能透過 `「{}」` 配合 cucumber-expressions 的 anonymous
`{}` placeholder 跑通，但會：

1. 與 `_shared` step-defs 既有 `{string}` 慣例不一致，無法重用 vocabulary
2. 視覺上與「中文 prose 的引述符」混淆 — AI 在中文內容裡容易把「natural-prose
   quotation」與「Gherkin parameter delimiter」當同一概念，落檔時各 step 自創
   不同符號，cargo-cult 擴散
3. cucumber-expressions 的 IDE highlight / autocomplete 預設只認 `"..."`

**改寫表**：

| ❌ 撞到 | ✅ 改寫 |
|---|---|
| `Then 畫面看得到 callout，內容為「IMPORTANT」` | `Then 畫面看得到 callout，內容為 "IMPORTANT"` |
| `Given 已開啟檔案「foo.md」` | `Given 已開啟檔案 "foo.md"` |
| `When 段落『Hello world』內嵌 inline callout` | `When 段落 "Hello world" 內嵌 inline callout` |
| `Then 不應看到 `<!--` 字面字` | `Then 不應看到 "<!--" 字面字` |

step-def 對應寫法（picked up by cucumber-expressions parser）：

```ts
// ✅ 正確 — `{string}` 自動 unwrap "..."
Then("畫面看得到 callout，內容為 {string}", async ({ appPage }, expected: string) => { ... });

// ❌ 錯誤 — 自造 placeholder delimiter
Then("畫面看得到 callout，內容為「{}」", async ({ appPage }, expected: string) => { ... });
```

驗證指令（落檔後跑）：

```bash
# Feature side：行內若有「不接著 IDE 命令字 / 標題段落」的 CJK 括號夾英文 / 數字 / 引號，疑似 placeholder
grep -nP '(「[^」]*[\w".]+[^」]*」|『[^』]*[\w".]+[^』]*』)' ${FEATURE_SPECS_DIR}/**/*.feature

# Step-def side：禁用 CJK 括號搭 {} placeholder
grep -rnP '「\{\}」|『\{\}』' ${PROJECT_ROOT}/tests/**/*.steps.ts
```

兩個指令都應零輸出。

---

## 資料驅動原則

每個 Step 必須指定具體、可驗證的資料，禁止模糊描述。

**正確示範：**
```gherkin
Given 系統中有以下用戶：
  | name  | email          | level | exp |
  | Alice | alice@test.com | 1     | 0   |
When 用戶 "Alice" 更新課程 1 的影片進度為 80%
Then 操作成功
And 課程 1 的進度應為：
  | lessonId | progress | status |
  | 1        | 80       | 進行中 |
```

**規則：**
- Given：使用 datatable 提供所有相關屬性的具體值
- When：明確指定用戶名稱/ID、資源 ID、參數值
- Then：使用 datatable 驗證具體的預期值，禁止模糊描述如「已改變」
- Then：失敗場景必須指定具體錯誤訊息：`Then 操作失敗，錯誤為"<具體錯誤訊息>"`
- **錯誤訊息一致性**：同一類失敗跨 Feature 使用同一條錯誤訊息
- **禁止在 datatable 中使用 JSON 字串**，複雜資料應拆分為多個 Given/And 步驟

---

## Given 設定方式

### 選擇 A：直接設定 Aggregate State

```gherkin
Given 訂單 "ORDER-123" 的狀態為：
  | orderId   | status | totalAmount |
  | ORDER-123 | 已付款  | 1500        |
```

適用：Aggregate 的不變條件（Invariant）簡單。

### 選擇 B：透過 Commands 設定

```gherkin
Given 用戶 "Alice" 建立訂單 "ORDER-123"，購買課程 1
And 用戶 "Alice" 完成訂單 "ORDER-123" 的付款，金額 1500 元
```

適用：Aggregate 有複雜的 Invariant（如「總金額 = Σ品項金額 + 運費 - 折扣」）。

| 條件 | 建議 |
|------|------|
| Invariant 簡單（如 `0 ≤ progress ≤ 100`） | 選擇 A |
| Invariant 複雜（跨屬性計算、狀態流轉） | 選擇 B |
| 建立路徑需要 5 個以上 Commands | 選擇 A |

---

## Key 識別規則

### Key 選擇原則

- **Actor（用戶等）**：優先使用 name（如 `"Alice"`），而非 ID
- **其他 Aggregate**：視情境選最具辨識度的屬性（如訂單用 `"ORDER-123"`）

### 引號規則

- **字串值用雙引號**：`"Alice"`、`"ORDER-123"`
- **數字值不用引號**：`1`、`80`

### 複合 Key

| 連接詞 | 範例 | 複合 Key |
|--------|------|----------|
| 在 | `用戶 "Alice" 在課程 1 的進度為 70%` | userId + lessonId |
| 對 | `用戶 "Alice" 對訂單 "ORDER-123" 的評價為 5 星` | userId + orderId |

**所有 Feature File 之間的句型應保持一致。**

---

## When 步驟格式

| 類型 | 格式 | 範例 |
|------|------|------|
| Command | `用戶 "<key>" <動詞＋參數>` | `When 用戶 "Alice" 更新課程 1 的影片進度為 80%` |
| Query | `用戶 "<key>" 查詢 <目標＋參數>` | `When 用戶 "Alice" 查詢課程 1 的進度` |
