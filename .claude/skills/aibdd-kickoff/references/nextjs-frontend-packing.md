# Next.js Frontend Packing

本檔定義 `/aibdd-kickoff` 的唯一 Next.js + Playwright 前端 top-level boundary packing。Kickoff 只初始化 AIBDD **project config 與 boundary truth skeleton**：`.aibdd/arguments.yml`、architecture truth、唯一 frontend boundary root、`shared/dsl.yml`、`test-strategy.yml`、**空的** `packages/` root；**不**建立 constitution、`bdd-stack/*.md`、任何 `packages/NN-<功能模組描述>/`，也不設定 active `TRUTH_FUNCTION_PACKAGE` / `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR`（由 plan-cycle `/aibdd-discovery` 在 sourcing 後 late-bind）；不建立 plan package，也不做 feature-specific 設計。

## Supported Stack

| Dimension | Value | User-facing meaning |
|---|---|---|
| Frontend language | TypeScript | 建立 TypeScript 前端 |
| Web framework | Next.js 16（App Router）| 前端入口使用 Next.js App Router |
| Component contract | Storybook 10 | 元件合約由 Storybook story export 承載；UI handler `L4.source_refs.component` 指向具體 story |
| Schema runtime | Zod 4 | 資料模型／schema validation 與 OpenAPI 對齊 |
| Mock layer | Playwright `page.route` + fixture closure（**不**使用 MSW、**不**用 dev-server in-process mock） | mock state 住在 `features/steps/fixtures.ts` closure；`page.route` 為 cross-process surface |
| Test strategy | E2E（含 Storybook a11y 與 vitest interaction） | playwright-bdd 端到端 + Storybook addon-a11y / addon-vitest |
| BDD runner | playwright-bdd（≥ 8.5）+ Playwright（≥ 1.45） | feature 與 step definitions 使用 playwright-bdd 慣例；`page.clock` 需 Playwright 1.45+ |

非 Next.js / 非 Playwright 選項可在說明文字中標示「尚未支援」，但不會進入 artifact render，也不得成為可選選項。

## Unique TLB Model

| Field | Value rule |
|---|---|
| `id` | 使用者確認的 frontend service id；建議 kebab-case（同時被當作 `arguments.yml#PROJECT_SLUG`，給 `${PROJECT_SLUG}-sb-mcp` MCP 工具使用） |
| `level` | `1` |
| `role` | `frontend` |
| `type` | `web-app` |
| `description` | `<id> Next.js + Playwright frontend application` 的白話描述 |
| `parent_id` | omitted |

Kickoff 永遠只建立一筆 frontend boundary。多 TLB / backend / external provider 由後續 architecture planning / promotion 能力處理，不在 kickoff 內支援。

## Boundary Root Rule

Kickoff 的唯一 boundary root 永遠是 `${SPECS_ROOT_DIR}/${id}/`。

`type` 只寫入 `boundary.yml` 作為 boundary metadata。Kickoff **不得**自動建立 `${SPECS_ROOT_DIR}/${id}/packages/NN-*`。Functional package 目錄與對應的 `arguments.yml` 鍵只在 `/aibdd-discovery` 綁定後出現。禁止產生 `${SPECS_ROOT_DIR}/${id}/${id}/`、或 `${SPECS_ROOT_DIR}/${id}/${id}/${type}/` 這類多層 root。

## Artifact Pack

| Artifact | Path | Shape |
|---|---|---|
| `arguments.yml` | `${FRONTEND_ROOT}/.aibdd/arguments.yml` | `STARTER_VARIANT: nextjs-playwright` + `PRESET_KIND: web-frontend` + `PROJECT_SPEC_LANGUAGE` + `PROJECT_SLUG` + config root + strategy refs + runtime refs + common parameters + Next.js / Playwright parameters only（mirror python；用 `FE_*` 鍵取代 `PY_*`，用 `FRONTEND_PRESET_CONTRACT_REF` 取代 `BACKEND_PRESET_CONTRACT_REF`） |
| `boundary.yml` | `${ARCHITECTURE_DIR}/boundary.yml` | `version: 2` with one frontend `web-app` boundary |
| `component-diagram.class.mmd` | `${ARCHITECTURE_DIR}/component-diagram.class.mmd` | Mermaid `classDiagram` with one `<<web-app>>` class（檔名副檔名見 `aibdd-core::diagram-file-naming.md`） |
| boundary root | `${SPECS_ROOT_DIR}/${id}/` | truth skeleton for the only frontend boundary |

注意：上表中的 `${FRONTEND_ROOT}` 等於 `${PROJECT_ROOT}/${FRONTEND_SUBDIR}`；當 `FRONTEND_SUBDIR == ""`（預設），退化為 `${PROJECT_ROOT}`。`${ARCHITECTURE_DIR}` / `${SPECS_ROOT_DIR}` 都是 frontend_root 相對的子路徑（與 backend packing 的 `convention-mapping.md` §Backend Root 組合規則同形態）。

## Boundary Folder Skeleton

Frontend stack 沿用 backend 的 4-folder boundary skeleton（**不另開 frontend-專屬 layout**），維持 plan / red-execute pipeline 對 boundary skeleton 的單一 SSOT：

| Folder | Purpose for `web-app` boundary |
|---|---|
| `contracts/` | boundary operation contract root（**consumer 側 OpenAPI**）；kickoff writes `contracts/.gitkeep` placeholder。對 `web-app`，consumer 端 OpenAPI 由團隊從上游 backend 取得或由 `/aibdd-form-api-spec` 共享產出 |
| `data/` | boundary state truth root（**Zod schema spec 引用**）；kickoff writes `data/.gitkeep` placeholder。前端用此目錄存放 Zod schema 文件指引（指向 `${FE_SCHEMAS_DIR}` 內具體 .ts），對偶 backend 的 DBML 角色 |
| `shared/` | boundary-level shared assets；kickoff creates `shared/dsl.yml` placeholder（其後由 `/aibdd-plan` Phase 6 從 `aibdd-core/assets/boundaries/web-frontend/shared-dsl-template.yml` 補入 `route-given` / `viewport-control` / `success-failure` / `time-control` 等 boundary-shared entries） |
| `packages/` | functional package **root only**；kickoff writes `packages/.gitkeep`；**不包含**任一 `packages/NN-*/` |

Kickoff writes `.gitkeep` in `contracts/`, `data/`, and `packages/` so that the empty boundary skeleton survives `git add -A` and fixture filesystem comparison. `.gitkeep` is an empty file. Any non-empty file in these directories is the responsibility of downstream skills (`/aibdd-form-api-spec`, `/aibdd-plan`, `/aibdd-discovery`).

Kickoff does not create a boundary-level `actors/` catalog. Discovery derives Activity actors from the raw idea / impact scope for each plan cycle; an actor catalog can be introduced later only by a dedicated planning or promotion step.

## Frontend-specific delegation

After kickoff completes the boundary skeleton, the next step in the frontend pipeline is `/aibdd-auto-starter`（以 `STARTER_VARIANT: nextjs-storybook-cucumber-e2e` 分流到 frontend variant）。Frontend variant 負責：

- Walking skeleton（Next.js 16 + React 19 + Storybook 10 + Tailwind 4）
- `playwright.config.ts` + `features/steps/fixtures.ts`（內含 `mockApi` fixture + `page.route` 攔截；fixture scope = test 自動 per-scenario reset，滿足 I3）
- `src/lib/api-client.ts`（純 fetch wrapper；**無** transport switch、**無** mock dispatch 路徑）
- `src/lib/schemas/**`（Zod schema SSOT）
- `bdd-stack/*.md`（acceptance-runner / step-definitions / fixtures / feature-archive / prehandling-before-red-phase）
- `dev-constitution.md`

Kickoff **不**建立任一上述檔；它只宣告 path token，讓 frontend starter 與下游 `/aibdd-plan`、`/aibdd-red-execute` 用同一組 token 溝通。

## What this packing does NOT include

- **不**建立 backend stack（無 `app/` / `pom.xml` / `pyproject.toml` / Alembic / Flyway 等）
- **不**啟用 boundary-level `aggregate-given` / `aggregate-then` / `external-stub` 等 backend handler（前端對應 handler 由 `aibdd-core::preset-contract/web-frontend.md` 規範）
- **不**設定 MSW（boundary-level `mock-state-given` / `api-stub` / `api-call-then` 透過 `features/steps/fixtures.ts` 內 `mockApi` + `page.route` 提供，mock state 住在 fixture closure）
- **不**寫死 `data/` 內容（前端 stack 此目錄留 `.gitkeep`；Zod schema 落在 `${FE_SCHEMAS_DIR}` 內，由 starter / plan 後續產生）
