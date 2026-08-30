# Gherkin And DSL Standards

這份標準是給 `gherkin-and-dsl` skill 用的詳細判準。原則只有一個：

> Gherkin 要讓 PM 看得懂，DSL 要讓 AI / 測試作者幾乎不需要腦補就能落地成測試程式碼。

## 1. Gherkin 語言邊界與句型收斂

- Gherkin 句型只講業務語意，不講 API、HTTP、selector、sessionStorage、輪詢、fixture 名稱。
- 前端、後端等介面分開寫；每個介面下的 feature files 依功能模組分組，DSL 由同模組 `dsl.md` 與介面根共用 `dsl.md` 分層承接。
- 每個 test case 最終都必須有對應的 Gherkin 實體。
- 語意 100% 相同的句型，必須共用同一句型。
- 句子若過胖、同時夾帶多個動作或多個斷言，應拆成更核心、可重用的步驟。
- DataTable 只用在兩種情況：
  - 多列資料
  - 單句其實隱含超過 3 個欄位的摘要資訊
- 預設值註解只放「會影響閱讀理解的業務預設值」，不放技術預設值。

## 2. Feature / Rule / Example 結構

- 先依系統功能面向切 feature files，檔名用繁體中文，並清楚表達受測動作或面向。
- `Rule` 必須原子化：如果 Example 的標題聽起來像另一條規則，就應拆成新的 Rule。
- `Example` 應該描述資料情境，不要只是重複 Rule 名稱。
- `Background` 只有在同一份 feature 裡，多個 Example 真的共用同一段 setup，且抽出後不會讓 Example 變難讀時才使用。
- `Scenario Outline` 只用在「同一條規則、流程完全相同、只是整組資料替換」的情況；如果其實是不同規則，不要硬套 Scenario Outline。

### 2.1 功能模組與 DSL 歸屬

- feature file 必須放在 `{介面}/{模組}/*.feature`，介面根目錄不得直接放 `.feature`。
- 模組優先沿用既有 truth 的功能邊界；只有既有模組都不適合時才新增。不可把某個專案當下的模組清單硬編碼成通用規則。
- 模組專屬句型放在 `{介面}/{模組}/dsl.md`。
- 只有跨模組使用，而且句型、Gherkin 參數、DataTable、預設值與實作契約完全一致的 row，才放在 `{介面}/dsl.md`。
- 文字相同或出現兩次不代表可以上提；同文異義必須拆成能辨識語意的不同句型。
- 同一句型只能有一個權威位置。升格或下放時要刪除舊 row，不保留根與模組 duplicate。
- 讀取某個 feature 時，合併介面根與同模組 DSL 查找，每個 Gherkin step 必須恰好命中一個 row。

## 3. 句中參數與 DataTable 格式

- 句中字串參數用雙引號：`"Alice"`、`"1234"`、`"等待中"`。
- 句中整數參數不加引號：`1`、`2`。
- DataTable 中的值一律不加引號。
- 參數 key 名稱用繁體中文，並盡量和規格一致，如：`玩家`、`配對碼`、`密文`、`猜測`。

## 4. DSL 必備欄位

介面根與模組 `dsl.md` 中的每個 DSL row 至少要有：

- `DSL 句型`
- `Gherkin 參數`
- `Data Table 參數`
- `預設參數`
- 實作語意欄

### 4.1 Gherkin 參數欄

- 條列每個參數
- 每個參數至少包含：名稱、型別、最小必要語意
- 不寫從句型本身就已經看得出來的補充

### 4.2 Data Table 參數欄

- 每個句型都要明講支不支援 DataTable
- 若不支援，只寫 `不支援`
- 若支援，列出：
  - 必填 / 可選
  - 型別
  - 最小必要語意

### 4.3 預設參數欄

- 只保留「如果不講清楚，AI 很容易猜錯」的預設值
- 不要把內部實作決策全部塞進來
- 例：`不合法的配對碼 = "12"` 是好的預設值；`等待快照次數 = 1` 不應出現在 Gherkin，但可留在前端 DSL

## 5. 後端 DSL 的實作語意

後端 DSL 的目的，不是只告訴 AI 打哪個 endpoint，而是規定這個句子最少要在哪些真相來源上成立。

### 5.1 Given / When 的顆粒度

Given / When 至少寫：

- `怎麼做`
- `權威狀態落地`
- `回寫`
- `不必查`

原則：

- 動作做完後，權威狀態要先在 store / DB 落地
- 不能只回寫 `last_response`
- 若是失敗請求，要明講權威狀態不能被改動

### 5.2 Then 的顆粒度

Then 用「驗證契約」來寫，不用固定模板硬填，但至少從這些通道挑相關的：

- `呈現結果`：這次 API 回應
- `權威狀態`：store / DB 真相
- `再讀確認`：再查一次仍成立
- `跨視角`：另一位玩家看到的是否一致
- `不該發生`：不該被改掉、不該被建立、不該被洩漏

原則：

- Then 不能只停在 response
- 對於「開了新房」「加入了既有房間」「猜中密文」「這次操作被拒絕」這種業務事實，至少要同時驗 response 與權威狀態
- 拒絕類 Then 特別要驗「狀態沒被失敗請求改壞」

## 6. 前端 DSL 的實作語意

前端假設要落地成 Playwright BDD。

### 6.1 不該在 DSL 主表出現的東西

- raw selector
- raw sessionStorage key
- 細碎 DOM 實作細節
- helper 內部實作

這些應該留在 page object、fixture helper 或真正的 step definition 內部。

### 6.2 Given / When / Then 的顆粒度

前端實作語意應優先圍繞：

- `使用 fixture`
- `Arrange 來源`
- `頁面操作`
- `等待條件`
- `回寫資料`

### 6.3 嚴格度要求

- 前端 Then 不能只看畫面文字
- 畫面上顯示的房主 / 密文保護 / 回合提示，必須能對應到後端權威狀態
- `猜測操作不可用` 不能只驗 disabled，還要確認使用者無法真的送出那次動作
- `畫面不含某密文` 不能只檢查完整字串，有必要時要防止把數字拆成多格或多段洩漏

## 7. 覆蓋與可落地性檢查

最終要檢查：

- 每個 test case 的 Arrange / Act / 預期輸出 / 必須維持不變，都被 Gherkin + DSL 吸收
- 沒有只剩原文註解、但步驟沒覆蓋到的驗證點
- 任一 Gherkin step 合併查找介面根與同模組 `dsl.md` 後，若不是恰好命中一個 row，就算缺口；零個是遺漏，多個是權威位置重複或句型歧義
- Gherkin 句子仍然是 PM 可讀的業務語言
- DSL 已經足夠讓 AI 推理出測試程式碼，不需大量腦補
- 機械稽核只負責指出拓樸、重複與匹配問題；共用契約是否語意一致仍由 agent 判斷

## 8. 典型重構順序

1. 先從 testplan 搬出可 review 的 Gherkin 草稿
2. 先補 `When`，再補 `Given / Then`
3. 再收斂共用句型
4. 先在唯一權威 DSL 位置補齊句型，再回填 feature
5. 再做 `Rule` / `Background` / `DataTable` / `Scenario Outline` 結構優化
6. 最後檢查覆蓋與嚴格度

## 9. 何時不要再繼續抽象化

若再抽象化會導致以下任一情況，就應停止：

- Rule 變得太大，不再原子
- Example 標題失去資料情境感
- DataTable 欄位過多，反而降低可讀性
- Scenario Outline 把其實不同規則的案例硬混在一起
- Gherkin 為了實作方便而暴露技術細節
