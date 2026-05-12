# Anti-patterns — Storybook CSF3 / AIBDD frontend

| 反例 | 為什麼不行 | 改寫方向 |
|---|---|---|
| 沒 accessible-name args 的 Story | step-def 無法派生 `getByRole(role, { name })` | 在 caller 推理包補 `accessible_name_arg` |
| 用 CSS class / nth-child 當 locator | 違反 boundary I4 與 nextjs-playwright variant 的 locator 優先序 | 改 `getByRole` / `getByLabelText` |
| `as Meta<typeof Component>` | 吞掉 TS 型別檢查，args 寫錯不會被抓 | 用 `satisfies Meta<typeof Component>` |
| `export default { ... }` 不指派給 `meta` | type alias `StoryObj<typeof meta>` 無法引用，story args 失去型別 | 用 `const meta = { ... } satisfies Meta<...>; export default meta;` |
| `import { storiesOf }` | CSF2 已棄用，Storybook 10 不再支援 | 用 CSF3 named export |
| 從 `@storybook/test` 匯入 `fn` / `expect` | Storybook 10 已搬到 `"storybook/test"` | 改 `import { fn, expect } from "storybook/test";` |
| 在 module scope 初始化 fetch / mock store | 渲染順序不可預期；mock 屬 `features/steps/fixtures.ts` SSOT | 把 mock 放回 fixture；story 只表達「給定狀態下的視覺」 |
| 跨 stories 共享 mutable closure（如全域計數器） | story 不再 deterministic；視覺 / a11y 回歸測試全部受牽連 | 每個 story self-contained；用 args 表達不同狀態 |
| `tags: ["autodocs"]` 同檔配 `parameters.docs.disable: true` | autodocs 與 docs-disable 互斥 | 二擇一；caller 先決定 |
| Story export 撞 `default` / `meta` | reserved 名稱 | 換 PascalCase 狀態名 |
| `play` 內寫業務驗收 assertions | story play 用於視覺 / docs；BDD assertion 屬 `.feature` + step-def | play 只展示交互後的顯示狀態；驗收歸 Cucumber |
| `play` 用 `setTimeout` 等候 async | 不可預期、會 flaky | 用 `await waitFor(...)` 或對 DOM expect |
| Story export name 用動詞句（如 `ClickToSubmit`） | 讀起來像 scenario，不像 state | 改 `Submitting` / `WithSubmitClicked` |
| 一個 component 一檔但塞 10+ stories 涵蓋 design tokens | tokens 應用 `parameters.backgrounds` / Chromatic 變體驗 | 拆出真正狀態差異；其餘走 parameters |
| 在 story 內 import product API client / repository | 違反「story 是純視覺合約」原則；綁實作會讓視覺回歸誤報 | 改用 args + Storybook MSW addon（若需要假資料） |
| `decorators` 注入跨 story 認證 / Provider 但帶共享狀態 | 違反 deterministic 原則 | Provider OK，但 state 隨 args 重建 |
