# aibdd-auto-starter fixture tests

## Contract

Each scenario uses this structure:

```text
.tests/<scenario>/
  before/
  after/
```

The runner must:

1. Create an isolated sandbox outside `.tests/`.
2. Copy `before/` into the sandbox as the working directory.
3. Invoke `/aibdd-auto-starter` with:
   - `project_dir=<sandbox>`
   - `project_name=AIxBDD Test <Backend|Frontend>`（依 scenario `STARTER_VARIANT` 對應；Python / Java backend → `AIxBDD Test Backend`，Next.js frontend → `AIxBDD Test Frontend`）
   - `arguments_path=<sandbox>/.aibdd/arguments.yml`
4. Compare the final sandbox filesystem with `after/`.
5. Write any execution reports outside scenario fixture directories.

## Oracle Rules

- `before/` represents the output of `/aibdd-kickoff` for the corresponding `STARTER_VARIANT`.
- `after/` represents the expected output after starter skeleton generation.
- `after/` is an oracle only; the target skill must not read it while executing.
- Scenario fixtures must not contain runner reports, gap reports, issue reports, scenario metadata, or README files.
- The runner must treat missing files, unexpected files, and content differences as failures.

## Scenario: python-e2e-from-kickoff

This scenario verifies that the starter consumes a kickoff-generated `.aibdd/arguments.yml`（`STARTER_VARIANT: python-e2e`）and produces a Python E2E walking skeleton without mutating `specs/`.

The oracle should encode not only "can boot" skeleton files, but also the
minimum runtime infrastructure needed so future
`/aibdd-red-execute -> /aibdd-green-execute -> /aibdd-refactor-execute`
runs do not spend their first iteration patching predictable starter gaps.

## Scenario: java-e2e-from-kickoff

This scenario verifies that the starter consumes a kickoff-generated `.aibdd/arguments.yml`（`STARTER_VARIANT: java-e2e`）and produces a Spring Boot 4 + Cucumber + Flyway + Testcontainers walking skeleton without mutating `specs/`.

Oracle 重點：
- `pom.xml` `<groupId>` / `<artifactId>` / `<name>` / `<description>` 與 arguments 對齊
- `src/main/java/${BASE_PACKAGE_PATH}/{Application,controller/HealthController,security/JwtTokenFilter,security/CurrentUser}.java` 完整
- `src/main/resources/application.yaml` 含 `spring.datasource.*`，**不**含 `spring.jpa.*`
- `src/test/java/${BASE_PACKAGE_PATH}/{config,cucumber,steps}/...` 與 `RunCucumberTest.java` 完整
- `src/test/resources/features/HealthCheck.feature` 與 step definitions 對齊
- `.aibdd/dev-constitution.md` + `.aibdd/bdd-stack/*.md`（含 `prehandling-before-red-phase.md`）皆已寫入；`arguments.yml` §9 含 `RED_PREHANDLING_HOOK_REF`
- 空目錄 `src/main/java/${BASE_PACKAGE_PATH}/{model,repository,service}/`、`src/main/resources/{db/migration,static,templates}/` 已建立

## Scenario: nextjs-storybook-cucumber-e2e-from-kickoff

This scenario verifies that the starter consumes a kickoff-generated `.aibdd/arguments.yml`（`STARTER_VARIANT: nextjs-storybook-cucumber-e2e`）and produces a Next.js 16 + Storybook 10 + Playwright BDD walking skeleton without mutating `specs/`.

Oracle 重點：
- `package.json` `name` 為替換後的 `${PROJECT_SLUG}`
- `src/app/{layout.tsx,page.tsx,globals.css}` 完整
- `src/lib/{api-client.ts,env.ts}` 落地 canonical-pattern
- `features/home.feature` + `features/steps/{fixtures.ts,home.steps.ts}` 為 playwright-bdd smoke（`features/home.feature` 含替換後的 `${PROJECT_NAME}`）
- `.storybook/{main.ts,preview.ts}` 設定 `@storybook/nextjs-vite`，stories glob 指向 `../src/components/**`
- 根設定檔（`tsconfig.json` / `next.config.ts` / `playwright.config.ts` / `vitest.config.ts` / `eslint.config.mjs` / `postcss.config.mjs` / `.gitignore` / `.env.example` / `vitest.shims.d.ts` / `README.md` / `AGENTS.md` / `CLAUDE.md`）皆已寫入
- `.aibdd/dev-constitution.md` + `.aibdd/bdd-stack/*.md`（含 `project-bdd-axes.md`、`acceptance-runner.md`、`step-definitions.md`、`fixtures.md`、`feature-archive.md`、`pre-red-checklist.md`、`prehandling-before-red-phase.md`）皆已寫入
- 由 `create_empty_dirs_nextjs` 建立的空目錄：`public/`、`src/components/`、`src/hooks/`、`src/lib/api/`、`src/lib/schemas/`、`features/steps/`、`src/app/`、`src/lib/`、`.storybook/`（不再放 `.gitkeep`）
- `specs/` 不被 starter 改寫

> Frontend fixture（`before/` 與 `after/`）尚未提交；待 `/skill-test-setup` 跑出 frontend kickoff variant 後補上。空目錄在 fixture 中如需保留請依測試 runner 的 oracle 規則處理（例如比對僅針對檔案，或在 `after/` 透過佔位檔顯式表達）。
