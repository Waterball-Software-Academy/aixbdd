# Storybook CSF3 最佳實踐

> 純 declarative reference。Phase 2 RENDER 時 LOAD 取規則。

## §1 命名

| 對象 | 慣例 | 範例 |
|---|---|---|
| Meta `title` | `<Domain>/<Component>` 兩段以上 | `Auth/LoginForm`、`Marketing/Hero` |
| Component identifier | PascalCase；與 component file export 同名 | `LoginForm` |
| Story export name | PascalCase；以**狀態名詞**或**形容詞**為主 | `Empty` / `Submitting` / `Disabled` / `WithError` |
| 不要用動詞句 | ❌ `ClickToSubmit` | ✅ `Submitting` |

## §2 args / argTypes

- 用 `args` 表達**狀態**；用 `argTypes` 表達**控制元件 + 描述**。
- 一個 story = 一個確定狀態；avoid `args: { ...someConditional }` 的條件展開。
- meta 層 `args` 放跨 story 共用（如 `onClick: fn()`）；story 層 `args` 放 override。
- 對於 callback prop，使用 `fn()`（from `"storybook/test"`）讓 actions panel 自動記錄事件。

## §3 accessible-name 與 boundary I4

每個 Story export **必須**至少在 `args` 內含一個能解析為 accessible name 的欄位 — 例如 `label`、
`aria-label`、`name`、或 component prop 內被映射到 DOM accessible name 的欄位。

```ts
// ✅ accessible name 來自 label arg
export const Primary: Story = {
  args: { label: "Submit", primary: true },
};

// ❌ 沒有任何 accessible-name args；step-def 無法派生 getByRole(role, { name })
export const Primary: Story = {
  args: { primary: true },
};
```

完整規範見 [`patterns/binding-anchor.md`](patterns/binding-anchor.md)。

## §4 play function

- `play` 用於展示交互後的最終視覺狀態（i.e. 為了 docs / 視覺回歸），**不**用於寫業務 BDD assertions。
- 業務驗收歸 Cucumber `.feature` + step-def，story `play` 不替代它。
- play 的 locator **必須**走 `getByRole / getByLabelText / getByText / getByTestId`，禁用 CSS class selector。
- play 之內若需要等候 async：`await waitFor(...)`，不要 `setTimeout`。

```ts
// ✅
play: async ({ canvas, userEvent }) => {
  await userEvent.click(canvas.getByRole("button", { name: "Submit" }));
  await expect(canvas.getByRole("alert")).toHaveTextContent(/required/i);
};

// ❌ 直接挑 class
play: async ({ canvasElement }) => {
  canvasElement.querySelector(".submit-btn")?.click();
};
```

## §5 parameters

| parameter | 用途 |
|---|---|
| `layout: "centered"` | 中心置放，常用於 button / form 等小元件 |
| `layout: "fullscreen"` | 整頁元件（page-level） |
| `layout: "padded"` | 默認，加邊距 |
| `backgrounds.options` | 提供切換背景 |
| `viewport.viewports` | 切換 viewport profile（mobile/tablet/desktop） |
| `docs.disable: true` | 該 story 不出現在 autodocs；與 `tags: ["autodocs"]` 互斥 |

## §6 Storybook 10 / CSF3 特有 API surface

- `import { fn, expect, userEvent, waitFor } from "storybook/test";` — 不從 `@storybook/test` 匯入
- `play({ canvas, userEvent })` 的 `canvas` 為 Testing Library `within(...)` wrapper；不要 `canvasElement.querySelector`
- `tags: ["autodocs"]` 替代舊的 `parameters.docs.autodocs: true`
- `satisfies Meta<typeof Component>` 替代 `as Meta<typeof Component>` —— TS 型別檢查更嚴

## §7 Component 對 Story 數量

- 一個檔對應一個 component；多 component 群組請拆檔。
- 一個 component 至少一個 story；上限視可區分狀態而定（典型 3–6 個 — `Default` / `Loading` / `Empty` /
  `Error` / `Disabled` / `WithLongContent`）。
- 細節判準見 [`patterns/states-and-variants.md`](patterns/states-and-variants.md)。
