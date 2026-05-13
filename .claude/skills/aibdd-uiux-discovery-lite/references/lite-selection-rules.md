# Lite Selection Rules — happy-path / feature-mentioned visual scope

本檔定義 `aibdd-uiux-discovery-lite` 如何從 discovery 產物收斂成最小可畫 scope。核心原則：**只畫 `.feature` 明確提到的畫面；若沒有明確畫面，才畫每個 feature 的 happy path 主流程**。

## §1 Explicit screen extraction

從 `.feature` 中抽 screen/frame/page candidates。命中任一條即視為 feature 明確提到畫面：

- Gherkin tag：`@screen:<slug>`、`@page:<slug>`、`@frame:<slug>`、`@ui:<slug>`
- Scenario / Rule / Step 文字含：`畫面`、`頁面`、`screen`、`page`、`view`、`frame`、`panel`、`dialog`、`modal`
- Step pattern 呈現可視 UI：`看到`、`顯示`、`進入`、`打開`、`點選`、`輸入`、`選擇`、`press`、`click`、`enter`、`select`、`see`、`show`

輸出 schema：

```yaml
explicit_screens:
  - frame_slug: checkout-payment
    source_feature: checkout.feature
    source_scenario: "Successful payment"
    source_steps: ["When 使用者輸入信用卡資料", "Then 顯示付款成功畫面"]
    reason: "step mentions 畫面"
```

## §2 Happy scenario fallback

若同一 feature 沒有 explicit screen，選取一條 happy scenario：

1. 優先選 tag 含 `@happy`、`@success`、`@main`、`@golden-path` 的 Scenario。
2. 其次選 Scenario 名稱含 `happy`、`success`、`successful`、`正常`、`成功`、`主流程`、`順利`。
3. 排除 tag 或名稱含 `@error`、`@sad`、`@edge`、`@invalid`、`@validation`、`@rejected`、`失敗`、`錯誤`、`例外`、`拒絕`、`無效`。
4. 仍無法判定時，取該 feature 的第一條非排除 Scenario。

## §3 Selected scope schema

`$$lite_scope` 必須記錄 selected 與 excluded：

```yaml
lite_scope:
  mode: lite-happy-path
  selected_frames:
    - frame_slug: checkout-payment
      selection_kind: explicit-screen | happy-scenario-fallback
      source_feature: checkout.feature
      source_scenario: "Successful payment"
      source_rules: ["R1"]
      selected_steps: [string]
      purpose: string
  excluded:
    - source_feature: checkout.feature
      source_scenario: "Invalid card is rejected"
      reason: "sad/error path excluded by lite mode"
```

## §4 Component candidate extraction in lite mode

只從 `lite_scope.selected_frames[*].selected_steps` 抽 component。不要從 excluded scenarios、error rules、全 activity graph 補元件。

Role mapping：

| Step intent | Component role | Primary state |
|---|---|---|
| click / 點選 / 送出 / 建立 / 開始 | button | idle |
| enter / 輸入 / 填寫 | textbox | filled |
| select / 選擇 | combobox / radiogroup | selected |
| see / 顯示 / 看到 list | list | populated |
| see / 顯示 / 看到 status/result | status | visible |
| page / screen / region shell | region | visible |
| dialog / modal | dialog | open |
| form | form | pristine |

## §5 Lite component inventory schema

每個 component 只允許一個 `primary_state`。若 happy path step 明確提到 loading/error（例如成功畫面需顯示 loading spinner），可以保留，但必須在 `source_step` 中有原文證據。

```yaml
component_inventory:
  - id: SubmitOrderButton
    role: button
    states:
      - code: idle
        source: "checkout.feature / Successful payment / When 使用者送出訂單"
        visual_hint: "primary CTA"
    anchor_role: button
    anchor_source_rule_id: checkout.R1
    used_by_frames: [checkout-payment]
    lite_reason: "happy path primary action only"
```

## §6 Lite frame composition schema

每個 selected frame 只畫一張組合圖；所有 component 使用其 primary_state。

```yaml
frame_composition:
  - frame_slug: checkout-payment
    source_feature: checkout.feature
    source_scenario: "Successful payment"
    layout_hint: "single-column happy path form"
    uses_components:
      - component_id: CardNumberInput
        canonical_state: filled
      - component_id: SubmitOrderButton
        canonical_state: idle
      - component_id: PaymentResultStatus
        canonical_state: visible
    purpose: "讓使用者完成付款主流程"
```

## §7 Invariants

- `lite_scope.selected_frames` 不可為空。
- selected frame 必須有 `.feature` 來源；禁止從 designer intuition 新增畫面。
- component 來源必須來自 selected steps；禁止從 excluded scenario 補 error component。
- 每個 component 只保留一個 primary/canonical state，除非 selected step 原文明確提到額外 state。
- frame `uses_components[*].component_id` 必須存在於 `component_inventory[*].id`。
- lite mode 不負責完整 UX coverage；error/empty/loading/rejected 應交 full `/aibdd-uiux-discovery`。
