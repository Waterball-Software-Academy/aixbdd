# Authentication Binding — Actor Key 作為前置條件的共用慣例

跨 skill 共用 SSOT。當某流程把「使用者已認證」視為環境前置時，**一律**以 actor key binding 表達；不寫入 Gherkin step、不列為 Rule。

由 `aibdd-discovery::flow-tree-format.md`、`aibdd-form-feature-spec::format-reference.md`、`aibdd-form-feature-spec::patterns/rule-only-format.md`、`speckit-aibdd-bdd-analyze::feature-syntax.md` 共同 LOAD。

---

## §慣例

認證（登入 / 已註冊 / session 有效）**不是**業務前置條件，而是 actor 的**身分屬性**。actor 本身即隱含「已通過認證」；流程無需重複聲明。

- **結帳 / 加購 / 下單流程**：登入 = 環境前置 → actor `@buyer` / `@logged-in-user` 本身已載明
- **登入流程 / 註冊流程 / 密碼重設 / MFA 流程**：認證 = 主題前置 → 登入 / 註冊本身就是 action，正常寫 STEP / Given / When / Then

---

## §表達方式

**Scenario / Step header**：用帶認證語義的 actor key（`@buyer` / `@admin` / `@logged-in-user`）標記觸發者，表達「此 actor 已通過認證」。

```gherkin
Scenario: 送出結帳
  When @buyer 點擊「結帳」送出
  Then 訂單應新增一筆紀錄
```

**Tag layer**（可選）：`@actor:buyer` / `@actor:admin` 作為 feature / scenario 層級的標籤，便於 runtime 注入 actor context。

**不寫**：

```gherkin
❌ Given 使用者已登入
❌ Given 使用者持有有效 session
❌ Given 使用者已通過認證
```

---

## §實作映射

actor key → authentication adapter 的綁定落在 step def 層，由 backend preset（JWT / session / OAuth）決定：

| Actor Key | Adapter（典型實作） |
|---|---|
| `@buyer` / `@admin` / `@logged-in-user` | JWT adapter（注入 `Authorization: Bearer <token>`） |
| `@admin`（後台系統） | session adapter（注入 `Cookie: session=<id>`） |
| `@guest` | 不注入認證 header |

step def 實作細節由 `/aibdd-plan` 產出的 boundary handler assets（`L4.preset.name` → `assets/boundaries/<preset>/...`）與 runner 契約決定；本檔僅規範 feature file 層的表達慣例。

---

## §Rule 豁免

4-rules pattern（`前置（狀態）` / `前置（參數）` / `後置（回應）` / `後置（狀態）`）**不包含**認證。

```
❌ Rule: 前置（狀態）- 使用者必須已登入
❌ Rule: 前置（狀態）- 使用者必須持有有效 session
```

原因：認證由 actor key binding 表達，重複列為 Rule 會造成：
- **語意冗餘**：actor `@buyer` 已隱含「已認證」
- **測試冗餘**：每條 Example 都會重複驗證同一件事
- **維護冗餘**：認證機制變更時需同步改 Rule 文字

---

## §例外

當流程**本身就是**認證主題時（登入 / 註冊 / 密碼重設 / MFA），login.feature / register.feature **正常**寫 Given / When / Then，認證本身是流程的主題而非前置：

```gherkin
Feature: 登入

  Scenario: 使用者輸入正確帳密後登入成功
    Given 系統中有使用者：
      | email | password |
      | a@b.c | pw123    |
    When @guest 輸入 email「a@b.c」與密碼「pw123」
    And @guest 點擊「登入」
    Then 回應應包含 JWT token
```

此類 feature 的 Rule 可以正當列出認證相關條件（`前置（參數）- email 必須為合法格式`、`後置（回應）- token 必須為有效 JWT`）— 因為這些是**流程本身的規則**，不是「重複聲明 actor 已認證」。
