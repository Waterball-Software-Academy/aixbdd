# Anchor Naming Rules — lite component-keyed accessible names

Lite 版沿用 full `aibdd-uiux-discovery` 的 component-keyed anchor contract，但只針對 lite scope 內的 interactive components。

## §1 候選來源

從 `lite_scope.selected_steps` 的 imperative verb + object 抽候選：

| Step example | Component id | role | anchor candidates |
|---|---|---|---|
| 使用者送出訂單 | SubmitOrderButton | button | 送出訂單 |
| 使用者輸入房間名稱 | RoomNameInput | textbox | 房間名稱 |
| 使用者選擇付款方式 | PaymentMethodSelect | combobox | 付款方式 |

Schema：

```yaml
anchor_candidates:
  - component_id: SubmitOrderButton
    role: button
    name_candidates: ["送出訂單"]
    source_rule_id: checkout.R1
    source_step: "When 使用者送出訂單"
```

## §2 強制條款

1. accessible name 必須包含 source step / source rule 的關鍵動詞或欄位名。
2. 同一 `component_id` 只能有一個鎖定 name。
3. 同 role + 同 name 不可對應到不同 component；必要時用括號消岐。
4. 禁止「按這裡」、「OK」、「Cancel」、「More」等無領域語意名稱，除非 source step 原文就是如此。
5. Lite mode 只鎖 happy path anchor；full state/error anchor 之後由 full discovery 或 plan 補。

## §3 下游合約

鎖定後的 anchor name 會進：

- Pencil 文字節點
- Storybook args label/children
- Playwright locator：`getByRole(role, { name })`

任何改寫都會破壞測試合約。
