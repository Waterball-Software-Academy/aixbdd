# Starter Variant: Next.js + Storybook + Cucumber + Playwright E2E

技術棧：Next.js 16 + React 19 + TypeScript 5 + Tailwind CSS 4 + Storybook 10 (Vite) + Playwright + playwright-bdd 8 + Vitest 4 + Zod 4 + ESLint 9

---

## 目錄結構

```
${PROJECT_ROOT}/
├── .aibdd/
│   ├── arguments.yml                       # kickoff project config；starter 只讀
│   ├── dev-constitution.md                 # 產品架構 bridge（前端層級、依賴；對齊 DEV_CONSTITUTION_PATH）
│   └── bdd-stack/
│       ├── project-bdd-axes.md             # `${BDD_CONSTITUTION_PATH}`：§5.1 檔名軸、§5.2 Red Pre-Hook 軸
│       ├── acceptance-runner.md            # playwright-bdd runner 定義
│       ├── step-definitions.md             # step pattern preset
│       ├── fixtures.md                     # playwright fixtures pattern
│       ├── feature-archive.md
│       ├── pre-red-checklist.md            # Pre-Red gate 檢核清單
│       └── prehandling-before-red-phase.md
├── src/
│   ├── app/                                # Next.js 16 App Router
│   │   ├── layout.tsx                      # Root layout：Geist font、metadata、html/body
│   │   ├── page.tsx                        # 落地頁（"It works!" smoke）
│   │   └── globals.css                     # Tailwind 4 全域樣式 + light/dark token
│   ├── lib/
│   │   ├── api-client.ts                   # apiFetch helper（fetch + Zod validate + ApiError）
│   │   ├── env.ts                          # 環境變數 schema（server/client 分離）
│   │   ├── api/                            # 業務 API client placeholder（empty；由 /aibdd-plan 填入）
│   │   └── schemas/                        # Zod schemas placeholder（empty；由 /aibdd-plan 填入）
│   ├── components/                         # Storybook stories colocated；business 元件由 /aibdd-plan 填入
│   └── hooks/                              # 業務 hooks placeholder（empty）
├── public/                                 # 靜態資源（Storybook staticDirs，empty）
├── features/                               # Cucumber Gherkin（playwright-bdd 來源）
│   ├── home.feature                        # smoke：頁面元素 / 響應式
│   └── steps/
│       ├── fixtures.ts                     # createBdd(test) → Given/When/Then
│       └── home.steps.ts                   # 共用 step definitions
├── .storybook/
│   ├── main.ts                             # @storybook/nextjs-vite framework；stories glob = src/components/**
│   └── preview.ts                          # parameters / a11y addon
├── ${SPECS_ROOT_DIR}/                      # 規格檔案（例：specs/）；starter 不建立業務子目錄
│   ├── architecture/
│   │   ├── boundary.yml
│   │   └── component-diagram.class.mmd
│   └── <boundary>/                         # boundary truth root（例：frontend）
│       ├── actors/
│       ├── contracts/
│       ├── data/
│       ├── shared/
│       │   └── dsl.yml
│       ├── test-strategy.yml
│       └── packages/                       # Discovery late-bind `NN-<功能模組描述>/`
├── package.json                            # next/react/vite/storybook/playwright/vitest 依賴
├── tsconfig.json                           # strict、bundler resolution、@/* alias
├── next.config.ts                          # Next.js 16 config
├── postcss.config.mjs                      # @tailwindcss/postcss
├── eslint.config.mjs                       # ESLint 9 flat config (next + storybook)
├── playwright.config.ts                    # playwright-bdd defineBddConfig + chromium/firefox/webkit
├── vitest.config.ts                        # storybook-test plugin + browser mode
├── vitest.shims.d.ts                       # @vitest/browser-playwright types
├── .env.example                            # NEXT_PUBLIC_API_BASE_URL / API_BASE_URL / API_TOKEN
├── .gitignore                              # Next/Playwright/Cucumber/.features-gen/.omc/storybook
├── README.md
├── AGENTS.md                               # nextjs-agent-rules + Storybook MCP guidance
└── CLAUDE.md                               # `@AGENTS.md`
```

---

## 依賴（package.json）

**Runtime**
- `next@16.2.6`
- `react@19.2.4`、`react-dom@19.2.4`
- `zod@^4.4.3`

**Dev / Tooling**
- `typescript@^5`、`@types/node`、`@types/react`、`@types/react-dom`
- `tailwindcss@^4`、`@tailwindcss/postcss@^4`
- `eslint@^9`、`eslint-config-next@16.2.6`、`eslint-plugin-storybook@^10.3.6`

**Storybook**
- `storybook@^10.3.6`、`@storybook/nextjs-vite`、`@storybook/addon-a11y`、`@storybook/addon-docs`、`@storybook/addon-onboarding`、`@storybook/addon-mcp`、`@storybook/addon-vitest`、`@chromatic-com/storybook`

**Testing**
- `@playwright/test@^1.59.1`、`playwright@^1.59.1`、`playwright-bdd@^8.5.0`
- `vitest@^4.1.5`、`vite@^8.0.11`、`@vitest/browser-playwright@^4.1.5`、`@vitest/coverage-v8@^4.1.5`

安裝指令：`npm install`（首次需另外跑 `npx playwright install` 下載瀏覽器）

---

## 設定檔說明

### `package.json` scripts

| Script | Command | Purpose |
|---|---|---|
| `dev` | `next dev` | 開發伺服器（port 3000） |
| `build` | `next build` | Production 打包 |
| `start` | `next start` | Production 啟動 |
| `lint` | `eslint` | ESLint 9 flat config |
| `storybook` | `storybook dev -p 6006` | Storybook 開發 |
| `build-storybook` | `storybook build` | Storybook 靜態打包 |
| `bddgen` | `bddgen` | playwright-bdd 從 features 生成 Playwright tests |
| `test:e2e` | `bddgen && playwright test` | Cucumber → Playwright 端對端 |
| `test:e2e:ui` | `bddgen && playwright test --ui` | 互動式 |
| `test:e2e:report` | `playwright show-report` | 報表 |

### `playwright.config.ts`

- `defineBddConfig({ features: 'features/*.feature', steps: 'features/steps/*.ts' })`
- 三個 browser projects：`chromium` / `firefox` / `webkit`
- `webServer` 自動啟動 `npm run dev`、`reuseExistingServer: !CI`
- Cucumber HTML reporter 輸出至 `cucumber-report/index.html`
- `BASE_URL` 環境變數覆寫（預設 `http://localhost:3000`）

### `vitest.config.ts`

- 使用 `@storybook/addon-vitest/vitest-plugin` 整合 Storybook stories 為 vitest tests
- `browser.provider: playwright()`，chromium headless
- 專案命名 `storybook`

### `tsconfig.json`

- `strict: true`、`moduleResolution: bundler`、`jsx: react-jsx`、`isolatedModules: true`
- `paths: { "@/*": ["./src/*"] }` — 對應 `src` 根目錄的 import alias
- include `next-env.d.ts`、`**/*.ts`、`**/*.tsx`、`.next/types/**/*.ts`、`.next/dev/types/**/*.ts`

### `eslint.config.mjs`

- ESLint 9 flat config
- `eslint-config-next/core-web-vitals` + `eslint-config-next/typescript`
- `eslint-plugin-storybook` flat/recommended
- 預設忽略 `.next/**`、`out/**`、`build/**`、`next-env.d.ts`

### `.storybook/main.ts`

- Framework: `@storybook/nextjs-vite`
- Stories glob: `../src/components/**/*.mdx` + `../src/components/**/*.stories.@(js|jsx|mjs|ts|tsx)`（colocated 於 `src/components/`；不使用集中式 `src/stories/`）
- Addons: a11y、docs、onboarding、mcp、vitest、chromatic
- `staticDirs: ["../public"]`

---

## arguments.yml 變數對照

| Placeholder | 來源 | 說明 | 範例 |
|---|---|---|---|
| `${STARTER_VARIANT}` | arguments.yml | starter variant，固定為 `nextjs-storybook-cucumber-e2e` | `nextjs-storybook-cucumber-e2e` |
| `${PROJECT_NAME}` | 詢問使用者（或 caller payload） | 專案顯示名稱（注入 `package.json.name`、`metadata.title`、home.feature scenario、README） | `Acme` |
| `${PROJECT_SLUG}` | 從 PROJECT_NAME 推導 | URL-safe 識別碼（小寫、連字號）；用於 `package.json.name` | `acme` |
| `${SPECS_ROOT_DIR}` | arguments.yml | 規格檔案根目錄 | `specs` |
| `${BOUNDARY_YML}` | arguments.yml | boundary 清單 | `specs/architecture/boundary.yml` |
| `${SRC_DIR}` | arguments.yml | 前端原始碼根目錄 | `src` |
| `${FRONTEND_FEATURES_DIR}` | arguments.yml | 前端 Gherkin features 目錄 | `features` |
| `${DEV_CONSTITUTION_PATH}` | arguments.yml | 開發基礎建設 bridge guideline | `.aibdd/dev-constitution.md` |
| `${BDD_CONSTITUTION_PATH}` | arguments.yml | bdd-stack 憲法樹之 §5.1 檔名軸錨點 | `.aibdd/bdd-stack/project-bdd-axes.md` |
| `${AIBDD_ARGUMENTS_PATH}` | arguments.yml | starter 自我定位用 | `.aibdd/arguments.yml` |

推導規則：
- `PROJECT_SLUG` = PROJECT_NAME 轉小寫、空格換連字號、移除特殊字元

Starter 安全邊界：
- `${PROJECT_ROOT}/.aibdd/arguments.yml` 必須已存在；starter 不建立、不改寫 `specs/`。
- `project_dir` 必須是已 kickoff 的 frontend repo root；若 arguments path 不在同一 repo root，停止並要求重新指定。

---

## 驗證步驟（dry-run）

完成骨架建立後，依序確認以下事項：

1. **檔案完整性**：所有 template 對照表中的檔案都已寫入目標路徑
2. **Placeholder 替換**：專案中不應殘留 `${PROJECT_NAME}`、`${PROJECT_SLUG}` 字串
3. **JSON 可解析**：`package.json` 與 `tsconfig.json` 必須是合法 JSON
4. **目錄完整**：`src/app/`、`src/lib/`、`src/lib/api/`、`src/lib/schemas/`、`src/components/`、`src/hooks/`、`features/steps/`、`.storybook/`、`public/` 皆存在
5. **TypeScript 設定一致**：`@/*` alias 指向 `./src/*`、`strict: true`

dry-run 預設指令（不需網路、不安裝套件）：

```bash
node -e "JSON.parse(require('fs').readFileSync('package.json'))" \
  && node -e "JSON.parse(require('fs').readFileSync('tsconfig.json'))" \
  && test -d src/app -a -d src/lib -a -d src/lib/api -a -d src/lib/schemas \
        -a -d src/components -a -d src/hooks \
        -a -d features/steps -a -d .storybook
```

退出碼 0 視為通過。完整套件安裝、TypeScript 編譯與 Playwright 測試非 starter dry-run 範疇——交由使用者於本機執行 `npm install` 與 `npm run test:e2e` 完成。

---

## 安全規則

- 不覆蓋已存在的檔案（跳過並回報）
- 不建立 feature-specific 程式碼（業務頁面、業務 API client、業務元件、業務 step definitions）
- 例外：`features/home.feature` + `features/steps/home.steps.ts` 為 **walking skeleton starter smoke**，僅驗證落地頁元素，不屬於產品需求 BDD
- `src/components/`、`src/hooks/`、`src/lib/api/`、`src/lib/schemas/`、`public/` 由 `create_empty_dirs_nextjs` 建立為空目錄（不再放 `.gitkeep`）；業務內容由下游 `/aibdd-plan` × Pre-Red gate 補入
- 例外：`.aibdd/dev-constitution.md`、`.aibdd/bdd-stack/*.md`（含 `project-bdd-axes.md`、`pre-red-checklist.md`、`prehandling-before-red-phase.md`）為 **AIBDD bridge／runtime guideline**，非產品程式碼亦非業務 BDD
- 不執行 `npm install` 或 `npx playwright install`

---

## Template 檔案對照表

| Template 檔名（`__` = `/`） | 輸出路徑 | 含 placeholder |
|---|---|---|
| `package.json` | `package.json` | ✓ `${PROJECT_SLUG}` |
| `tsconfig.json` | `tsconfig.json` | — |
| `next.config.ts` | `next.config.ts` | — |
| `postcss.config.mjs` | `postcss.config.mjs` | — |
| `eslint.config.mjs` | `eslint.config.mjs` | — |
| `playwright.config.ts` | `playwright.config.ts` | — |
| `vitest.config.ts` | `vitest.config.ts` | — |
| `vitest.shims.d.ts` | `vitest.shims.d.ts` | — |
| `.gitignore` | `.gitignore` | — |
| `.env.example` | `.env.example` | — |
| `README.md` | `README.md` | ✓ `${PROJECT_NAME}` |
| `AGENTS.md` | `AGENTS.md` | ✓ `${PROJECT_SLUG}` |
| `CLAUDE.md` | `CLAUDE.md` | — |
| `.storybook__main.ts` | `.storybook/main.ts` | — |
| `.storybook__preview.ts` | `.storybook/preview.ts` | — |
| `.aibdd__dev-constitution.md` | `.aibdd/dev-constitution.md` | — |
| `.aibdd__bdd-stack__project-bdd-axes.md` | `.aibdd/bdd-stack/project-bdd-axes.md` | — |
| `.aibdd__bdd-stack__acceptance-runner.md` | `.aibdd/bdd-stack/acceptance-runner.md` | — |
| `.aibdd__bdd-stack__step-definitions.md` | `.aibdd/bdd-stack/step-definitions.md` | — |
| `.aibdd__bdd-stack__fixtures.md` | `.aibdd/bdd-stack/fixtures.md` | — |
| `.aibdd__bdd-stack__feature-archive.md` | `.aibdd/bdd-stack/feature-archive.md` | — |
| `.aibdd__bdd-stack__pre-red-checklist.md` | `.aibdd/bdd-stack/pre-red-checklist.md` | — |
| `.aibdd__bdd-stack__prehandling-before-red-phase.md` | `.aibdd/bdd-stack/prehandling-before-red-phase.md` | — |
| `features__home.feature` | `features/home.feature` | ✓ `${PROJECT_NAME}` |
| `features__steps__fixtures.ts` | `features/steps/fixtures.ts` | — |
| `features__steps__home.steps.ts` | `features/steps/home.steps.ts` | — |
| `src__app__layout.tsx` | `src/app/layout.tsx` | ✓ `${PROJECT_NAME}` |
| `src__app__page.tsx` | `src/app/page.tsx` | — |
| `src__app__globals.css` | `src/app/globals.css` | — |
| `src__lib__api-client.ts` | `src/lib/api-client.ts` | — |
| `src__lib__env.ts` | `src/lib/env.ts` | — |

外加由 `create_empty_dirs_nextjs` 建立、無對應 template 檔的空目錄（前次 `.gitkeep` 模板職責改由此函式接管）：

| 路徑 | 用途 |
|---|---|
| `public/` | Storybook `staticDirs: ["../public"]` 與 Next.js 靜態資源 |
| `src/lib/api/` | API client 業務 module placeholder |
| `src/lib/schemas/` | Zod schemas placeholder |
| `src/components/` | Storybook stories colocated；業務元件 placeholder |
| `src/hooks/` | 業務 React hooks placeholder |
| `features/steps/` | playwright-bdd step definitions（含 `fixtures.ts`、`home.steps.ts`） |
| `src/app/` | Next.js App Router root |
| `src/lib/` | shared utilities root |
| `.storybook/` | Storybook config 目錄 |

說明：模板使用 Python `string.Template` 的 `safe_substitute`；JS 模板字面量 `${expr.attr}` 因含 `.` 不會被誤觸（`Template` braced 形式僅匹配 `[a-z_][a-z0-9_]*` 後緊接 `}`）。

---

## 完成後引導

```
Frontend walking skeleton 已建立完成。

下一步：
1. cd ${PROJECT_ROOT} && npm install
2. npx playwright install        # 首次安裝瀏覽器
3. npm run dev                   # 啟動 Next.js 16 開發伺服器（port 3000）
4. npm run storybook             # 啟動 Storybook（port 6006）
5. npm run test:e2e              # 跑 Cucumber + Playwright 冒煙測試
6. /aibdd-discovery — 開始需求探索
```
