# four-rules-prefix

## Rules

- Rule-only features MUST use `@ignore`.
- Rule-only features MUST NOT include `Background`, `Scenario`, `Scenario Outline`, or `Examples`.
- Every `Rule:` line MUST use one of these prefixes:
  - `前置（狀態）`
  - `前置（參數）`
  - `後置（回應）`
  - `後置（狀態）`
  - `後置（狀態：資料）`
  - `後置（狀態：外發）`
  - `後置（狀態：資源）`
  - `後置（狀態：行為）`
- Rule line MUST contain only the prefix and one short atomic assertion.
- Rule body MAY contain details, bullets, branch notes, and concrete values indented under the Rule.
- Preconditions MUST appear before postconditions.
- Description lines, Rule body lines, and bullet lines MUST NOT begin with any keyword or alias reserved by the feature's active Gherkin dialect.
- Authentication status MUST NOT be written as a Rule unless the feature is itself an authentication flow.
- Discovery rule-only features MUST keep example rows and executable scenario data out of the file.
- Rule-only generation MUST NOT create a fixed keyword blacklist in `arguments.yml`; keyword collision is dialect-dependent.
- Rule lines MUST be atomic assertions, not document headings.
- Rule lines MUST NOT merge independent subject/action/consequence assertions.
- Validation SHOULD report `RULE_BODY_KEYWORD_COLLISION` when a description line, Rule body line, or bullet line begins with a keyword reserved by the active Gherkin dialect.
- Validation SHOULD report a rule-only phase violation when a Discovery feature contains executable scenarios before BDD Analysis.

### Prefix Decision Branches

- IF a rule constrains state that must already exist before the operation:
  - USE `前置（狀態）`
- IF a rule constrains an input carried by the current request:
  - USE `前置（參數）`
- IF a rule verifies only the current operation response:
  - USE `後置（回應）`
- IF a rule verifies persisted or observable system state after the operation:
  - IF the state is database row or entity data:
    - USE `後置（狀態：資料）`
  - IF the state is an outbound call, event, email, notification, or third-party side effect:
    - USE `後置（狀態：外發）`
  - IF the state is a limited resource such as stock, seat, quota, balance, or lock:
    - USE `後置（狀態：資源）`
  - IF the state is only observable across repeated execution, retry, expiry, or idempotency:
    - USE `後置（狀態：行為）`
  - ELSE:
    - USE `後置（狀態）`
- IF a rule describes authentication status:
  - IF the feature is login, registration, password reset, MFA, or another authentication flow:
    - ALLOW authentication-related Rules.
  - ELSE:
    - DO NOT write the authentication status as a Rule; express identity through actor binding.

## Examples

### Good: four prefix groups in rule-only feature

```gherkin
@ignore @command
Feature: 指派學員至 CRM 旅程階段

  管理者將學員放入指定旅程階段，以便系統套用該階段 SOP。

  Rule: 前置（狀態） - CRM 旅程必須存在

  Rule: 前置（參數） - 目標階段 ID 必須提供

  Rule: 後置（回應） - 回應應包含學員目前階段

  Rule: 後置（狀態：資料） - 學員旅程階段應更新為目標階段

  # TODO: Example 區段由後續 BDD Analysis 階段補充。
```

### Good: Rule line short, Rule body carries details

```gherkin
Rule: 後置（狀態：外發） - 系統應通知管理者排課
  通知內容包含：
  - 學員姓名
  - 目標課程
  - 預約時段
  - 學員聯絡方式
```

### Good: resource state uses resource subtype

```gherkin
Rule: 後置（狀態：資源） - 課程名額應扣除預約人數
```

### Good: repeated execution uses behavior subtype

```gherkin
Rule: 後置（狀態：行為） - 重複送出同一預約請求應維持同一筆預約
```

### Bad: executable scenario appears too early

```gherkin
@ignore @command
Feature: 指派學員至 CRM 旅程階段

  Rule: 前置（狀態） - CRM 旅程必須存在

  Scenario: 指派成功
    Given CRM 旅程 "標準旅程" 已存在
    When 管理者指派學員 "小明" 至階段 "試聽"
    Then 操作成功
```

Why bad:

- Discovery rule-only feature MUST NOT contain `Scenario`.
- Examples belong to BDD Analysis, not Discovery rule-only formulation.

### Bad: category heading instead of atomic assertion

```gherkin
Rule: 前置（狀態） - CRM 旅程驗證
```

Why bad:

- This reads like a section title.
- It does not state a verifiable subject + condition.

Better:

```gherkin
Rule: 前置（狀態） - CRM 旅程必須存在
Rule: 前置（狀態） - CRM 旅程必須包含目標階段
```

### Bad: merged independent assertions

```gherkin
Rule: 前置（狀態） - CRM 旅程必須存在且目標階段必須啟用
```

Why bad:

- `CRM 旅程必須存在` and `目標階段必須啟用` are separate assertions.

Better:

```gherkin
Rule: 前置（狀態） - CRM 旅程必須存在
Rule: 前置（狀態） - 目標階段必須啟用
```

### Bad: dialect keyword collision in Rule body

```gherkin
Rule: 後置（狀態：外發） - 系統應通知管理者排課
  Given 管理者可看到以下資訊：
  - 學員姓名
  - 預約時段
```

Why bad:

- In English Gherkin dialect, `Given` is a keyword at line start.
- Rule body prose must not begin with active dialect keywords.

Better:

```gherkin
Rule: 後置（狀態：外發） - 系統應通知管理者排課
  管理者可看到以下資訊：
  - 學員姓名
  - 預約時段
```

### Bad: authentication status outside authentication flow

```gherkin
Rule: 前置（狀態） - 使用者必須已登入
```

Why bad:

- Generic authentication state is actor identity, not a domain Rule.
- Use actor binding such as `@admin` or `@logged-in-user`.

Allowed only when the feature itself is authentication-related:

```gherkin
Feature: 使用者登入

  Rule: 前置（參數） - email 必須為合法格式
  Rule: 後置（回應） - 回應應包含 JWT token
```
