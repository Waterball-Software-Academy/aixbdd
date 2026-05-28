# Storybook CSF3 格式 — Meta / StoryObj / args / play / autodocs

> 純 declarative reference。Phase 2 RENDER 時 LOAD 取語法骨架。
>
> 來源：Storybook 10 官方文件 `https://storybook.js.org/docs`（CSF3、writing-stories、parameters、play、autodocs）。

## §1 檔案骨架 — TypeScript（一個 component → 一個 stories 檔）

```ts
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";          // 僅 action arg 需要
import { expect } from "storybook/test";      // 僅 play function 需要

import { Button } from "./Button";

const meta = {
  title: "Example/Button",
  component: Button,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    backgroundColor: { control: "color" },
  },
  args: {
    onClick: fn(),
  },
} satisfies Meta<typeof Button>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    primary: true,
    label: "Submit",
  },
};
```

### 強制條款

| 條款 | 說明 |
|---|---|
| `import type { Meta, StoryObj }` | type-only 匯入，避免 runtime side-effect |
| `satisfies Meta<typeof Component>` | TS 型別推導；不要用 `as Meta<...>`（會吞掉 args 的型別檢查） |
| `export default meta` | 必須出現一次且只一次 |
| `type Story = StoryObj<typeof meta>` | 名稱固定為 `Story`，繫到 meta 推導出 story args 的型別 |
| named export = story | export 名為 PascalCase；export name = sidebar story name（Storybook 自動 humanize） |
| reserved 不可作為 export name | `default` / `meta` |

## §2 Meta 區塊欄位

| 欄位 | 必填 | 說明 |
|---|---|---|
| `title` | 否（搭配 CSF auto-title 時可省） | Storybook sidebar 路徑，斜線分層；`/` 為層級分隔；不可重複 |
| `component` | 是 | 對應 React component identifier；驅動 autodocs 與 argTypes 推導 |
| `parameters` | 否 | 例：`layout: "centered" \| "fullscreen" \| "padded"`、`backgrounds: { ... }` |
| `tags` | 否 | 常見：`["autodocs"]`；可加 `"!autodocs"` 否定繼承 |
| `argTypes` | 否 | 控制 control（`"color"` / `"select"` / `"boolean"` / `"text"` / `"number"`）與 description |
| `args` | 否 | meta 層 args = 所有 story 的 baseline；story 層 args 可 override |
| `decorators` | 否（少用） | 若一定要用，請保證 deterministic、無共享 mutable state |

## §3 Story 區塊欄位

```ts
export const StoryName: Story = {
  args: { ... },                 // story-specific override；I4 accessible-name arg 必須出現
  parameters: { ... },           // story-specific 例：viewport、layout、backgrounds
  tags: [ ... ],                 // story-specific tag override（autodocs 可在 story 層停用）
  play: async ({ canvas, userEvent }) => { ... },
  render: (args) => <Component {...args} />,  // 罕用；只在無法用 args 表達時
};
```

### `play` function 簽名（CSF3）

```ts
play: async ({ canvas, userEvent }) => {
  await userEvent.type(canvas.getByRole("textbox", { name: "Email" }), "alice@example.com");
  await userEvent.click(canvas.getByRole("button", { name: "Submit" }));
  await expect(canvas.getByText("Welcome, Alice")).toBeInTheDocument();
};
```

- `canvas` 為 Testing Library 的 `within(storyRoot)` 結果，提供 `getByRole / getByLabelText / getByTestId / getByText`
- `userEvent` 隨參數注入（不需另 import）
- `expect` 從 `"storybook/test"` 匯入

## §4 Tags & Autodocs

- 預設 meta 加 `tags: ["autodocs"]` → 自動產生 docs page
- 個別 story 想退出 autodocs → 該 story 加 `tags: ["!autodocs"]`
- `parameters.docs.disable: true` 與 `tags: ["autodocs"]` **不可同時** — 視為 conflict（caller error）

## §5 `.tsx` 何時必要

| 情境 | 副檔名 |
|---|---|
| 純 args 不寫 JSX | `.stories.ts` |
| 使用 `render: (args) => <Wrapper>...</Wrapper>` | `.stories.tsx` |
| `decorators: [(Story) => <Provider><Story/></Provider>]` | `.stories.tsx` |

副檔名由 caller 在 `target_path` + `format` 同步指定；本 skill 只校驗一致，不改副檔名。

## §6 reserved / 禁止

- 禁 `import { storiesOf }`（CSF2 / 已棄用）
- 禁 `export default { ... } as Meta<...>`（用 `satisfies Meta<...>`）
- 禁直接從 `@storybook/test` 匯入；統一從 `"storybook/test"`（Storybook 10 起的 API surface）
- 禁在 module scope 直接初始化 mock store / DOM；mock 應屬 `features/steps/fixtures.ts`
