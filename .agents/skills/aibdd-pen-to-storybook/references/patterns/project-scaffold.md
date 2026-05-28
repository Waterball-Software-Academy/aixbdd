# Pattern — Project Scaffold

> 純 declarative reference。Phase 6 LOAD 取 file-tree + 各檔模板。

## §1 目標 file tree

```
<target_dir>/
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── next-env.d.ts
├── .storybook/
│   ├── main.ts
│   └── preview.ts
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css      # 由 Phase 6 step 11 從 $$tokens RENDER；不在本檔模板內
├── components/          # 由 Phase 7 LOOP 寫入；本檔不預置
└── stories/             # 由 Phase 7 LOOP 寫入；本檔不預置
```

## §2 `package.json`

> 與 `aibdd-auto-starter/templates/nextjs-storybook-cucumber-e2e/package.json` 主要 deps 對齊；
> 移除 BDD-specific deps（playwright-bdd / vitest / @vitest/* / eslint），只保留視覺 scaffolding 必要的部分。

```json
{
  "name": "pencil-ui",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  },
  "dependencies": {
    "next": "16.2.6",
    "react": "19.2.4",
    "react-dom": "19.2.4"
  },
  "devDependencies": {
    "@storybook/addon-docs": "^10.3.6",
    "@storybook/nextjs-vite": "^10.3.6",
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "storybook": "^10.3.6",
    "tailwindcss": "^4",
    "typescript": "^5",
    "vite": "^8.0.11"
  }
}
```

> **Critical**：`@storybook/nextjs-vite`（不是 `@storybook/nextjs`）。後者走 webpack/SWC 路徑、在 Next 16
> 下會撞 `swc.isWasm is not a function` 而每個 story build 失敗。鎖定理由見
> [`../format-reference.md`](../format-reference.md) §7 與 [`../anti-patterns.md`](../anti-patterns.md)。
>
> **本 skill 不含的 deps**（屬下游 BDD pipeline 範圍，由 `aibdd-auto-starter` 補）：
> `@playwright/test` / `playwright-bdd` / `vitest` / `@vitest/*` / `@chromatic-com/storybook` / `@storybook/addon-vitest` / `@storybook/addon-a11y` / `@storybook/addon-onboarding` / `@storybook/addon-mcp` / `eslint*`。

## §3 `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

## §4 `next.config.ts`

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

export default nextConfig;
```

## §5 `postcss.config.mjs`

```js
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
export default config;
```

## §6 `next-env.d.ts`

```ts
/// <reference types="next" />
/// <reference types="next/image-types/global" />
```

> Next.js 自動維護此檔；初次 scaffold 預先寫入避免 `tsc` 第一次 run 抱怨缺 reference。

## §7 `.storybook/main.ts`

```ts
import type { StorybookConfig } from "@storybook/nextjs-vite";

const config: StorybookConfig = {
  stories: ["../stories/**/*.stories.@(ts|tsx)"],
  addons: ["@storybook/addon-docs"],
  framework: { name: "@storybook/nextjs-vite", options: {} },
};

export default config;
```

> `@storybook/addon-docs` 為 `tags: ["autodocs"]` 渲染 docs page 必需。
> 如不需要 autodocs，可移除此 addon 並從 [`../dsl-best-practice.md`](../dsl-best-practice.md) §5 拿掉 `tags`。

## §8 `.storybook/preview.ts`

```ts
import type { Preview } from "@storybook/nextjs-vite";
import "../app/globals.css";

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: "void",
      values: [
        { name: "void",  value: "#060812" },
        { name: "panel", value: "#0B1020" },
      ],
    },
    layout: "centered",
  },
};

export default preview;
```

> `backgrounds.values` 為預設骨架；caller 可在 Phase 6 完成後手動改成符合 `.pen` 設計的色階。

## §9 `app/layout.tsx`

```tsx
import "./globals.css";

export const metadata = {
  title: "pencil-ui",
  description: "Generated from .pen by aibdd-pen-to-storybook",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

## §10 `app/page.tsx`

```tsx
export default function Page() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <p className="font-mono text-text-primary">
        See Storybook for components: <code>npm run storybook</code>
      </p>
    </main>
  );
}
```

> page-level 配置由 caller 在 scaffold 完成後依需要重寫；本檔只給 minimal placeholder 確保 `next build` 通過。

## §11 `app/globals.css` 結構（Phase 6 step 11 RENDER）

不在本檔模板，由 Phase 6 從 `$$tokens` 動態 RENDER：

```css
@import url("...font...");          /* L1 — 必須最前 */
@import "tailwindcss";              /* L2 */

@theme {                            /* L3 — LOOP $$tokens */
  --color-<name>: <value>;
  --font-<role>: <value>;
  --radius-<name>: <value>;
  --spacing-<name>: <value>;
}

@layer base {                       /* L4 */
  body { ... }
}

@utility name { ... }               /* L5 — Tailwind 4 自訂 utility 語法 */
```

詳見 [`../dsl-best-practice.md`](../dsl-best-practice.md) §3。
