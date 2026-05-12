# DSL Best Practice — Tailwind 4 / CSF3 / Next.js 16 慣例

> 純 declarative reference。Phase 7 RENDER 時 LOAD 取規則。

## §1 Component file 慣例

```tsx
// components/PlayerCard.tsx
export type PlayerCardProps = {
  name: string;
  state: "turn" | "waiting" | "critical" | "defeated";
  hp: number;
  attempts: number;
};

export function PlayerCard({ name, state, hp, attempts }: PlayerCardProps) {
  return (
    <div className="rounded-cipher bg-panel p-4 text-text-primary">
      <span className="font-mono text-accent-cyan">{name}</span>
      ...
    </div>
  );
}
```

| 規則 | 說明 |
|---|---|
| 不 `import React` | Next.js 16 + React 19 自動 JSX runtime |
| `interface` for object props | 對齊 project rules（unions 才用 `type`） |
| className 走 `@theme` 派生 utility | `text-<color>` / `bg-<color>` / `rounded-<radius>` / `font-<role>` |
| 不引入 `clsx` / `cn` | 模板字串拼接已足夠；額外 deps 屬 caller 指定範圍 |
| named export | 與檔名同 PascalCase；單檔單組件 |
| 不寫 `default export` | story 端用 named import 才能拿到型別 |

## §2 Story file 慣例（CSF3）

```tsx
// stories/PlayerCard.stories.tsx
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { PlayerCard } from "../components/PlayerCard";

const meta = {
  title: "Battle/PlayerCard",
  component: PlayerCard,
} satisfies Meta<typeof PlayerCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Turn: Story = {
  args: { name: "Alice", state: "turn", hp: 80, attempts: 2 },
};

export const Waiting: Story = {
  args: { name: "Bob", state: "waiting", hp: 60, attempts: 0 },
};
```

| 規則 | 說明 |
|---|---|
| `import type` for `Meta` / `StoryObj` | type-only；無 runtime side effect |
| `satisfies Meta<typeof Component>` | 不用 `as`（會吞掉 TS 檢查） |
| 一檔一 component；多 component 拆檔 | 對應 §1 規則 |
| `title` 用 `<Domain>/<Component>` 兩段 | 兩段以上有 sidebar 階層 |
| Story export name = PascalCase 狀態名 | `Turn` / `Waiting` / `WithError`；不要動詞句 |
| 群組構圖（Roster 等）走 `render:` | 不要把多 component 塞進 `args` |

### 群組構圖範例

```tsx
export const Roster: Story = {
  args: { name: "_", state: "turn", hp: 0, attempts: 0 },  // dummy 滿足 meta
  render: () => (
    <div className="flex flex-col gap-2 w-[280px]">
      <PlayerCard name="Alice" state="turn"     hp={80} attempts={2} />
      <PlayerCard name="Bob"   state="waiting"  hp={60} attempts={0} />
      <PlayerCard name="Cara"  state="critical" hp={12} attempts={3} />
      <PlayerCard name="Dan"   state="defeated" hp={0}  attempts={3} />
    </div>
  ),
};
```

## §3 Tailwind 4 `globals.css` 結構

```css
/* app/globals.css */
@import url("https://fonts.googleapis.com/css2?family=Inter&family=JetBrains+Mono&display=swap");
@import "tailwindcss";

@theme {
  --color-bg-void: #060812;
  --color-accent-cyan: #00E5FF;
  --color-text-primary: #E8ECF7;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --font-body: "Inter", system-ui, sans-serif;
  --radius-cipher: 10px;
  --spacing-section: 32px;
}

@layer base {
  body {
    background: var(--color-bg-void);
    color: var(--color-text-primary);
    font-family: var(--font-body);
  }
}

@utility scanlines {
  background-image: repeating-linear-gradient(
    to bottom, transparent 0, transparent 2px,
    rgba(112,144,255,.04) 2px, rgba(112,144,255,.04) 3px
  );
}
```

| 規則 | 說明 |
|---|---|
| 字型 `@import url(...)` 必須**最前** | 放在 `@import "tailwindcss";` 之前；放後面瀏覽器忽略 |
| `@import "tailwindcss";` | Tailwind 4 入口；不再有 `@tailwind base; @tailwind components; @tailwind utilities;` |
| `@theme { ... }` | tokens SSOT；每筆 `--<namespace>-<name>: <value>;` 自動產 utility |
| `@layer base { ... }` | global element 樣式（body / html） |
| `@utility name { ... }` | Tailwind 4 自訂 utility 語法；v3 的 `@layer utilities` 不再生效 |

## §4 命名

| 對象 | 慣例 | 範例 |
|---|---|---|
| Component identifier | PascalCase；與檔名 export 同名 | `PlayerCard` / `ResultChip` / `HPBar` |
| Story export name | PascalCase；狀態名詞或形容詞 | `Turn` / `Waiting` / `Critical` |
| Story `title` | `<Domain>/<Component>` 兩段以上 | `Battle/PlayerCard` |
| Tailwind token name | kebab-case；與 `.pen` variable 名同步 | `accent-cyan` → `--color-accent-cyan` |
| 不用動詞句作 export | ❌ `ClickToSubmit` | ✅ `Submitting` |

## §5 Storybook 10 / CSF3 specific surface

- Story 檔 type import：`import type { Meta, StoryObj } from "@storybook/nextjs-vite";`（**不**從 `@storybook/react-vite`）
- Test API：`import { fn, expect, userEvent, waitFor } from "storybook/test";`（**不**從 `@storybook/test` — Storybook 10 已搬路徑）
- `tags: ["autodocs"]` 替代 `parameters.docs.autodocs: true`
- `satisfies Meta<typeof Component>` 替代 `as Meta<typeof Component>`
- `play({ canvas, userEvent })` 的 `canvas` 為 Testing Library `within(...)` wrapper；不要 `canvasElement.querySelector`

## §6 Component → Story 數量

- 一檔一 component；多 component 群組請拆檔
- 一個 component 至少一個 story；典型上限 3–6（`Default` / `Loading` / `Empty` / `Error` / `Disabled`）
- 群組構圖（Roster / Gallery）走 `render:`，不展開 args
