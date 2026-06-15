# `discovery-sourcing.md` Example

> 情境：上一輪已完成「會員登入」功能，因此既有 **plan package** 與 **function package** 都已存在。
> 這一輪 discovery 要補上「記錄每次會員登入時間」與相關欄位。
> 本輪 **只會新開 plan package**，**不會新開 function package**；既有 `packages/01-會員登入` 這個 function package 內多個 truth artifact 會被 impact。
>
> 註：本範例情境為 `${PROJECT_SPEC_LANGUAGE}` = `zh-hant`，故 slug 一律以繁體中文撰寫；技術 token（`last_login_at`、`OAuth` 等）保留英文原文。en-us 專案下 slug 應改寫為英文 kebab-case（如 `001-member-login-last-login-at`、`packages/01-member-login`）。

## Impact scope

- 本輪問題一句：既有會員登入功能已完成，這一輪要補上「每次登入成功都要記錄登入時間」。
- 納入範圍：登入成功後的時間戳記、必要資料欄位、既有登入規則與 feature 規格的更新。
- 明確排除：會員註冊、忘記密碼、角色權限、第三方 OAuth 登入、登入通知推播。

## Function package charters

### `packages/01-會員登入`

- **職責一句**：處理會員帳號登入成功／失敗流程，以及登入後狀態呈現所需的後端規格切片。
- **納入**：登入表單驗證、登入成功建立 session、登入失敗錯誤訊息、登入成功後導向。
- **排除**：註冊、忘記密碼、第三方登入、角色權限、通知推播。
- **本 plan 變更型態**：`impact-only`
- **本輪規格增量**：登入成功後必須記錄 `last_login_at`（時間戳記），並反映到 data truth 與必要規格檔。

## Packaging decision

- 新 plan package：`002-會員登入記錄登入時間`
- 本輪涉及的 function packages：
  - `packages/01-會員登入`（沿用）
- function package 決策：本輪 **只新開 plan package**；**不新開 function package**；僅 impact 既有 `packages/01-會員登入` 橫切面 truth artifacts。

## Resolved sourcing decisions

- 訪客登入是否必須先註冊帳號：**否**；沿用既有登入規格與訪談結論。
- 登入時間記錄時點：**登入成功當下**；失敗嘗試不寫入 `last_login_at`。
- 登入時間是否必須外顯在 API 回應：**條件式**；若 UI 不展示則 contract 可不更新。

## Spec structure（示意樹）

> 與 `aibdd-flows-specify/01-sourcing-and-packaging/SOP.md` 步驟 6 對齊用：boundary truth 與 function package 同在 `specs/` 根下，plan package 落在 `specs/plans/NNN-<slug>/`；邏輯 boundary 見 `architecture/boundary.yml`。

```text
specs/
  architecture/
    boundary.yml
  boundary-map.yml
  contracts/
    會員-api.yml
  data/
    會員.dbml
  shared/
    dsl.yml
  packages/
    01-會員登入/
      dsl.yml
      features/
        01-會員登入.feature
  plans/
    002-會員登入記錄登入時間/
      spec.md
      reports/
        discovery-sourcing.md
        impact-matrix.yml
```

## `spec.md` 摘要片段（同一故事線）

```markdown
## Discovery sourcing summary
- 本輪問題一句：每次登入成功都要記錄 `last_login_at`。
- 已掃過並收斂 impact 的 boundary 規格檔：`specs` 根下 contracts／data／packages（見 `reports/impact-matrix.yml`）。
- 本輪 function package：`packages/01-會員登入`。

Pointer：`reports/discovery-sourcing.md`
```

## Bad slug examples（嚴禁的 fallback 寫法）

當 `${PROJECT_SPEC_LANGUAGE}` 為 `zh-hant`（或任何非英文語系），下列 slug 形態皆為錯誤示範，**不得**作為「為避中文字元」的 fallback：

| ❌ Bad slug | 反例類型 | 為何錯 |
|---|---|---|
| `001-yi-a2b-mo-wang-fang` | romanization（漢語拼音 + 隨機數字） | 拼音 transliteration 不可逆，三年後沒人看得懂指什麼；數字串混入更失去語意 |
| `001-hui-yuan-deng-ru` | 漢語拼音 | 即使拼音正確，違反「slug 須以 `${PROJECT_SPEC_LANGUAGE}` 自然語撰寫」 |
| `001-member-login-last-login-at` | 整段英譯（zh-hant 專案下） | 規格語言已定為 zh-hant，slug 不該整段翻成英文；除非整個專案語系真的是 en-us |
| `001-會員-login` | 中英混拼且非技術 token | 無理由混拼；`login` 不是 API field／DSL token／domain acronym，應寫「登入」 |
| `001-會員登入_with_OAuth` | 句法混拼 | 雖含 `OAuth` 技術 token 是合法的，但 `with` 是英文連接詞，應寫「001-OAuth第三方登入」之類自然中文句構 |

✅ 對應正確寫法：`002-會員登入記錄登入時間`、`001-會員登入`、`001-OAuth第三方登入`、`001-CRM學員旅程階段SOP`（保留技術 token `OAuth` / `CRM` / `SOP`）。

## Notes

- `Function package charters`：每個 function package 的職責邊界與本輪增量。
- Plan-side artifacts（`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}`、`${IMPACT_MATRIX_YML}` 本身）**不放進** `${IMPACT_MATRIX_YML}` entries。
