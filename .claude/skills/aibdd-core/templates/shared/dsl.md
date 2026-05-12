# dsl.md（shared / project-wide）

> **Project-wide DSL registry**（shared tier，SSOT）。四層 mapping schema（L1 / L2 / L3 / L4）
> 權威來源見 `plan.md` Chapter 1 §1.5.2 與 `test-plan-rules.md §3.3`。
>
> Entry 由各 spec package 的 boundary `dsl.md` **promote** 而來，流程為
> `/speckit.aibdd.promote-dsl`，需有 `/speckit.aibdd.bdd-analyze` Step 6 DSL Promotion Gate
> 簽核的 `promotion-proposal.md`。
>
> **除淘汰 entry 外勿手動編輯。** 經 promotion 新增才可追溯。

---

## Schema reminder

```yaml
- id: <snake-case-id>
  L1:                            # Business Sentence Pattern — feature-surface Gherkin
    given: "..."                 # optional
    when:  "..."
    then:  ["..."]
  L2:                            # DSL Semantics
    context: "..."
    role:    "..."
    scope:   "..."
  L3:                            # Technical Pattern
    type: mock | direct-call | state-check | state-setup | ui-interaction | ...
  L4:                            # Contract / payload (mock: concrete; non-mock: one-line summary)
    ...
```

---

## Entries

<!--
  Keep alphabetical by `id`. Each entry must carry all four layers.
  Entries here are reused by every feature package in this project.
-->

- id: example_user_logged_in
  L1:
    given: "使用者已登入為「{role}」"
  L2:
    context: "任何需要認證才能進入的頁面 / 端點"
    role:    "end-user"
    scope:   "system"
  L3:
    type: state-setup
  L4:
    summary: "在 test fixture 中注入一個有效的 session token；細節依 bdd-constitution.md 規範的 auth fixture 工具處理"

- id: example_order_created
  L1:
    when: "使用者送出訂單「{order_id}」"
    then:
      - "訂單狀態顯示為「已建立」"
  L2:
    context: "結帳頁送出後"
    role:    "end-user"
    scope:   "boundary"
  L3:
    type: direct-call
  L4:
    summary: "觸發前端 submit action；後端 API 呼叫由 test-double / real backend 處理；具體 endpoint 見 contracts/orders.yml"
