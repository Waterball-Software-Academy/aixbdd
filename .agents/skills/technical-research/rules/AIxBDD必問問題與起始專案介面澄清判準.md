# Rule 1 - AIxBDD 有三題必問，沒問完不得寫 research / techstack

- Level: `MUST`
- 這是 AIxBDD workflow。`/technical-research` 在寫入 `research.md` 或更新 `specs/truth/techstack.md` 之前，必須先確認這三題都已拍板：
  1. **BDD techstack**：各端用哪套跑 Gherkin。一定要 clarify。
  2. **測試策略**：怎麼驗。一定要問。沒講就預設都是 E2E。
  3. **系統有哪些端**：起始專案，且系統介面疑似有後端或其他端時，也要問。
- 三題都走 `/clarify`。不可只在 `Rationale` 裡自行補完，也不可沿用相簿範例或 agent 推論充當答案。
- 任一必問題尚未拍板，必須停止，不進入產出 `research.md` / `techstack.md` 的 phase。

## Good Example

- 這個例子是好的，因為三題都先 clarify，再寫 research。

````md
起始專案。`spec.md` 有工位終端、狀態板、系統設定，工單狀態要共用。

本輪 `/clarify`：
1. BDD techstack：前端 Playwright，後端 behave
2. 測試策略：前端 E2E，後端 behave 打 API 與權威狀態
3. 系統有哪些端：前端 webapp + 後端 API

之後才寫 `research.md`。
````

## Bad Example

- 這個例子是壞的，因為三題都沒問，直接從 spec 假設寫出無後端、不要 E2E。

````md
`spec.md` 假設寫了純前端、無後端。

直接寫：
- 不建後端
- 測試用 vitest，不引入 E2E
- 不問 BDD techstack
````

# Rule 2 - 只有使用者這輪原話、本輪 clarify、或既有 techstack 已寫明，才算已回答

- Level: `MUST`
- 下列才算該題已拍板，可以跳過重問：
  - 使用者這輪原話已經指定，例如「後端則是 behave」「前端要上 webapp」「後端是 python fastapi」「要直接上 e2e test」
  - 本輪 `/clarify` 已經得到該題答案
  - 既有 `specs/truth/techstack.md` 已寫明該端、該端 BDD techstack、以及測試策略，且本輪沒有改判
- 下列不算已回答，仍必須 clarify：
  - `spec.md` 假設或範圍寫了「純前端」「無後端」「無資料庫」「不要 E2E」
  - `research.example.md`、`techstack.example.md` 或任何教學範例的堆疊
  - agent 從產品故事、畫面清單或「本版最小複雜度」自己推論出的端與測試策略
  - 空的、只有標題的、或尚未寫入採用技術的 `techstack.md`

## Good Example

- 這個例子是好的，因為它把使用者原話當答案，不把 spec 假設當答案。

````md
使用者這輪說：後端是 python fastapi，後端則是 behave，要直接上 e2e test。

判定：
- BDD techstack 後端 = behave，已拍板
- 測試策略 = E2E，已拍板
- spec 假設「無後端」不採用，仍要問系統有哪些端，或沿用使用者已講的前端 webapp + FastAPI
````

## Bad Example

- 這個例子是壞的，因為它把 spec 假設與範例預設當成已拍板。

````md
`spec.md` 寫無後端，`research.example.md` 寫先不要 E2E。

判定：
- 系統沒有後端，不用問
- 測試策略沿用 vitest
````

# Rule 3 - BDD techstack 必須按端問清楚 runner

- Level: `MUST`
- BDD techstack 問的是：每個存在的端，用哪套跑該端 Gherkin。
- 前端 webapp 的 BDD techstack 與後端 API 的 BDD techstack 要分開問或分開選，不可寫成「全專案用同一套測試框架」就帶過。
- 若某端還沒被確認存在，先問「系統有哪些端」，再問該端的 BDD techstack。
- 寫入 `research.md` 時，BDD techstack 必須是獨立決策，或在測試決策裡按端列明 runner。寫入 `techstack.md` 時，`測試與驗證` 必須看得到各端 BDD techstack。

## Good Example

- 這個例子是好的，因為各端 runner 分開寫。

````md
BDD techstack：
- 前端 webapp：Playwright
- 後端 API：behave
````

## Bad Example

- 這個例子是壞的，因為只寫一個測試框架，看不出各端 Gherkin 怎麼跑。

````md
測試與驗證：
- vitest
- 手動 demo
````

# Rule 4 - 測試策略一定要問；沒講就預設都是 E2E

- Level: `MUST`
- 測試策略是必問題，即使 agent 覺得單元測比較便宜，也必須先問。
- 使用者沒講測試策略時，預設都是 E2E：有前端就上前端 E2E，有後端就上後端 E2E。後端 E2E 用該端的 BDD techstack 打 API 與權威狀態，不是只打領域函式。
- 不可把「先 vitest / pytest、E2E 以後再補」「Quickstart 手動驗證」「完整瀏覽器 E2E 成本偏高所以不引入」寫成預設。
- 只有使用者明確改判「這端先不要 E2E」時，才可在 `research.md` 與 `techstack.md` 排除該端 E2E。

## Good Example

- 這個例子是好的，因為沒講時落成 E2E，有講才改。

````md
使用者沒提測試策略。

落成：
- 前端 webapp：E2E
- 後端 API：E2E（behave）
````

## Bad Example

- 這個例子是壞的，因為自行把預設收成單元測。

````md
核心風險在狀態與數量，所以本版不引入瀏覽器 E2E，只用 vitest。
````

# Rule 5 - 起始專案且系統介面疑似有後端或其他端時，必須問有哪些端

- Level: `MUST`
- **起始專案**指這次是第一個 plan，或 `specs/truth/techstack.md` 還不存在、是空的、或還沒寫入任何採用技術。
- 起始專案時，只要系統介面**疑似**有後端或其他端，就必須問「這次有哪些端」。不可直接寫成只有前端或只有後端。
- 下列任一成立，即為疑似有後端或其他端：
  - `spec.md` 出現多個畫面，且畫面要共用同一份業務狀態
  - 出現工單、訂單、庫存、審核、待辦、狀態板這類需要跨終端或重整後仍在的狀態
  - 出現開始／完成、先到先得、可用量、紀錄追溯、欄位設定這類命令
  - 出現 API、資料庫、後端、伺服器、第二個終端、第二個角色專用畫面
  - 成功標準要求資料不被重整清掉，或兩個操作者看到同一份真相
- 問的是端的存在，不是框架細節。框架（例如 FastAPI、Vite）可在同一輪或下一題補，但不能用「先當純前端原型」跳過端的存在。
- 不是起始專案、且既有 `techstack.md` 已寫明有哪些端、本輪也沒有改判時，不必重問這一題。

## Good Example

- 這個例子是好的，因為起始專案看到多畫面與共用工單狀態，就問有哪些端。

````md
起始專案。spec 有工位終端、狀態板、系統設定，同一張工單要推進。

必問：
- 這次有哪些端？前端 webapp / 後端 API / 其他
````

## Bad Example

- 這個例子是壞的，因為起始專案明明疑似有後端，卻用 spec 假設直接排除。

````md
起始專案。spec 假設 5 寫無後端。

判定：沿用純前端，不問有哪些端。
````
