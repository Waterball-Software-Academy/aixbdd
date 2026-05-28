# Anti-patterns — aibdd-pen-to-storybook

> 純 declarative reference。Phase 8 VERIFY 失敗時對照查 / Phase 6–7 RENDER 前自檢。

## §1 Symptom → Cause → Fix

| Symptom | Cause | Fix |
|---|---|---|
| `TypeError: swc.isWasm is not a function` | 用了 `@storybook/nextjs`（webpack/SWC 路徑），與 Next 16 SWC 不相容 | 改用 `@storybook/nextjs-vite` + 加 `vite` dep；framework 名同步改 |
| Tailwind utility 找不到（如 `bg-accent-cyan` unknown） | `globals.css` 缺 `@import "tailwindcss";` 或 token 沒寫進 `@theme` | 兩者都確認；`@theme { --color-accent-cyan: ... }` 必在 `@import "tailwindcss"` 之後 |
| `@layer utilities { ... }` 內自訂 utility 完全沒生效 | Tailwind 4 改用 `@utility name { ... }` 語法 | 改成 `@utility scanlines { ... }` 等 |
| Build 通過但設計與 .pen 不符 | hex code 拷貝錯字、token 大小寫不一 | 重跑 `jq '.variables' design.pen`，逐字 verbatim 寫進 `@theme` |
| `clsx is not defined` | component 用了 `clsx(...)` 但 `package.json` 無此 dep | 兩擇一：加 `clsx` dep、或改回模板字串拼接 |
| 字型完全沒載入 | Google Font `@import url(...)` 放在 `@import "tailwindcss";` 之後 | 字型 `@import url(...)` 必須在 globals.css **最前** |
| `swc.isWasm` 但 framework 寫對了 | node_modules 殘留舊 framework；快取沒清 | `rm -rf node_modules .next && npm install` 後重 build |
| `tsc --noEmit` 抱怨 `Cannot find module 'next'` | scaffold 完成但 `npm install` 還沒跑 | 先 `npm install` 再 `tsc`；Phase 8 順序固定 |
| `build-storybook` 抱怨 story args 型別錯 | 用了 `as Meta<...>` 而非 `satisfies` | 改 `satisfies Meta<typeof Component>`；`as` 會吞掉型別檢查 |
| Story export 撞名（如 `default` / `meta`） | reserved name 被當 story name | 改 PascalCase 狀態名 |
| 一個 component 30+ 個 story | 把 design tokens / 微小視覺變化展開成獨立 story | 拆成不同 component；或用 `parameters.backgrounds` 切換背景 |
| 多 screen 一次轉，component 抽象混淆 | Phase 4 沒鎖 `screen_id` 就跑 Phase 5 | 每次只跑一個 screen；多 screen 多次呼叫本 skill |
| Heredoc 看到 `$variable` 被展開 | shell heredoc 用 unquoted `<<EOF` | 改 `<<'EOF'`（單引號 token） |

## §2 Framework 鎖定衝突檢查

升級前先確認：

| 套件 | 升級會撞 |
|---|---|
| `next` 16 → 17 | 須重審 SWC API；`@storybook/nextjs-vite` 是否還相容 |
| `react` 19 → 20 | JSX runtime / type defs 對齊；`import React` 省略前提是否仍成立 |
| `tailwindcss` 4 → 5 | `@theme` / `@utility` 語法是否變更 |
| `storybook` 10 → 11 | `storybook/test` import 路徑、CSF3 surface 變動須同步 `aibdd-form-story-spec` 與 `aibdd-auto-starter` template |
| `vite` 8 → 9 | `@storybook/nextjs-vite` peer dep 範圍 |

## §3 命名 / 顆粒度反例（Phase 5）

| 反例 | 為什麼不行 | 改寫方向 |
|---|---|---|
| Component 名小寫開頭（`playerCard`） | JSX 解析會當 HTML element | 強制改 PascalCase |
| Component 只有一個 story 且該 story 無 args | 無變異，不該抽 component | inline 進 page-level layout |
| `topBar` 被抽成 component | Always-inline 規則命中 | 寫進 `app/page.tsx` 不抽 |
| 同 component 抽 30+ story 涵蓋全 design token | story 不是 token catalog | 拆 component / 用 `parameters.backgrounds` |
| component name 含 slash（`Auth/LoginForm`） | `.pen` `id` 規格禁 slash；React identifier 也禁 | 用 PascalCase 連寫；slash 只用於 Story `title` |

## §4 Storybook story 反例（Phase 7）

| 反例 | 為什麼不行 | 改寫方向 |
|---|---|---|
| `as Meta<typeof Component>` | 吞掉 TS 型別檢查 | `satisfies Meta<typeof Component>` |
| `import { storiesOf }` (CSF2) | Storybook 10 不再支援 | 用 CSF3 named export |
| 在 module scope 初始化 fetch / mock store | 渲染順序不可預期 | 用 args 表達狀態；mock 屬 `features/steps/fixtures.ts` SSOT |
| Story 用 CSS class / nth-child 當 locator | 違反「story 是純視覺合約」 | 視覺由 Tailwind utility 表達；BDD locator 屬下游 `aibdd-form-story-spec` |
| `play` 內寫業務驗收 assertion | story play 用於視覺 / docs | 業務驗收歸 Cucumber `.feature` + step-def |

## §5 觀察：本 skill 與 `aibdd-form-story-spec` 的職責邊界

| 議題 | aibdd-pen-to-storybook | aibdd-form-story-spec |
|---|---|---|
| 輸入 | `.pen` 設計檔 | Planner 推理包 |
| 抽 component / 數量 | YES（heuristics） | NO（caller 已決定） |
| 寫 component 檔 | YES | NO |
| 寫 story 檔 | YES（視覺骨架） | YES（BDD-aware，含 `accessible_name_arg`） |
| 綁 `getByRole(role, { name })` locator | NO | YES |
| Storybook 版本 | 10 | 10 |
| Story import path | `@storybook/nextjs-vite` | `@storybook/nextjs-vite` |

兩者不互斥：本 skill 寫完 component + 視覺 story 後，下游可由 `aibdd-form-story-spec` 重寫 story 加上
BDD binding anchor。
