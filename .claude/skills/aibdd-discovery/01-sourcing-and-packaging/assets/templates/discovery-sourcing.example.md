# `discovery-sourcing.md` Example

> 情境：上一輪已完成「會員登入」功能，因此既有 **plan package** 與 **function package** 都已存在。
> 這一輪 discovery 要補上「記錄每次會員登入時間」與相關欄位。
> 本輪 **只會新開 plan package**，**不會新開 function package**；既有 `packages/member-login` 這個 function package 內多個 truth artifact 會被 impact。

## Impact scope

- 本輪問題一句：既有會員登入功能已完成，這一輪要補上「每次登入成功都要記錄登入時間」。
- 納入範圍：登入成功後的時間戳記、必要資料欄位、既有登入規則與活動流程的更新。
- 明確排除：會員註冊、忘記密碼、角色權限、第三方 OAuth 登入、登入通知推播。

## Impact matrix

| 既有規格檔（相對 `${TRUTH_BOUNDARY_ROOT}`） | 變更類型 | impact 描述 |
|---|---|---|
| `packages/member-login/features/member_login.feature` | 更新 | 先用既有 scenario 界定「登入成功」邊界；本輪補上登入成功後必須記錄 `last_login_at` 規則 |
| `packages/member-login/activities/member_login.activity` | 更新 | 先用既有活動流程定位插入點；本輪在登入成功路徑顯式寫入時間戳記記錄動作 |
| `packages/member-login/dsl.yml` | 更新 | 沿用既有登入語彙；本輪延伸到「最後登入時間」相關語彙或狀態描述 |
| `data/member.dbml` | 更新 | 先確認既有欄位是否足夠；本輪新增或調整 `last_login_at` 以承載登入時間 state truth |
| `contracts/member-api.yml` | 條件式更新 | 先對照現行契約與回傳模型；本輪若需求外顯到 API 才改動 |

## Function package charters

### `packages/member-login`

- **職責一句**：處理會員帳號登入成功／失敗流程，以及登入後狀態呈現所需的后端規格切片。
- **納入**：登入表單驗證、登入成功建立 session、登入失敗錯誤訊息、登入成功後導向。
- **排除**：註冊、忘記密碼、第三方登入、角色權限、通知推播。
- **本輪變更型態**：`impact-only`
- **本輪規格增量**：登入成功後必須記錄 `last_login_at`（時間戳記），並反映到 data truth 與必要規格檔。

## Packaging decision

- 新 plan package：`002-member-login-last-login-at`
- 本輪涉及的 function packages：
  - `packages/member-login`（沿用）
- function package 決策：本輪 **只新開 plan package**；**不新開 function package**；僅 impact 既有 `packages/member-login` 橫切面 truth artifacts。

## Resolved sourcing decisions

- 訪客登入是否必須先註冊帳號：**否**；沿用既有登入規格與訪談結論。
- 登入時間記錄時點：**登入成功當下**；失敗嘗試不寫入 `last_login_at`。
- 登入時間是否必須外顯在 API 回應：**條件式**；若 UI 不展示則 contract 可不更新。

## Spec structure（示意樹）

> 與 `01-sourcing-and-packaging.md` 步驟 6 對齊用：展示 **boundary truth 樹** 與 **新開 plan package** 的相對位置；目錄名請替換成實案。

```text
specs/
  architecture/
    boundary.yml
  web-backend/
    contracts/
      member-api.yml
    data/
      member.dbml
    packages/
      member-login/
        dsl.yml
        features/
          member_login.feature
        activities/
          member_login.activity
  002-member-login-last-login-at/
    spec.md
    reports/
      discovery-sourcing.md
```

## `spec.md` 摘要片段（同一故事線）

```markdown
## Discovery sourcing summary
- 本輪問題一句：每次登入成功都要記錄 `last_login_at`。
- 已掃過並收斂 impact 的 boundary 規格檔：`web-backend` 下 contracts／data／packages（見 `reports/discovery-sourcing.md` 內 **`Impact matrix`**）。
- 本輪 function package：`packages/member-login`（職責邊界見 `Function package charters`；拍板見 `Resolved sourcing decisions`）。

Pointer：`reports/discovery-sourcing.md`
```

## Notes

- `Impact matrix`：**唯一**表格；每列一個既有規格檔，統一寫本輪 raw idea 對它的 impact（含對齊與變更敘述）。
- `Function package charters`：每個 function package 的職責邊界與本輪增量。
- Plan-side artifacts（`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}`）**不放進** `Impact matrix`。
