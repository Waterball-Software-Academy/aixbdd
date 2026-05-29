<!-- INSTRUCT: 01-ask-config/SOP.md 把每個 {{PLACEHOLDER}} 填好後 WRITE 到 ${PROJECT_ROOT}/KICKOFF_PLAN.md。
     此檔為 File First 暫存訪談檔；落檔後就是 kickoff 題庫與答案的唯一 SSOT。
     schema 詳見 ../assets/kickoff-plan-contract.md。 -->

# KICKOFF_PLAN

## Status

{{STATUS}}

## Context

| Field | Value |
|---|---|
| Project root | `{{PROJECT_ROOT}}` |
| Boundary codebase subdir | `{{BOUNDARY_CODEBASE_SUBDIR}}` |
| Boundary codebase root | `{{BOUNDARY_CODEBASE_ROOT}}` |
| Plan path | `{{PLAN_PATH}}` |
| Supported stacks | python_e2e ｜ java_e2e ｜ nextjs_playwright |

## Questions

### q1-tech-stack

- prompt: 要建立哪一種 stack？
- context: |
    python_e2e：Python + FastAPI + SQLAlchemy + Alembic + Behave E2E + Testcontainers。
    java_e2e：Java + Spring Boot 4 + JdbcClient + Flyway + Cucumber 7 + Testcontainers。
    nextjs_playwright：Next.js 16 + Storybook 10 + playwright-bdd + Zod 4。
    其他 frontend / Unit Test only / Mobile 尚未支援；本輪不提供選擇。
- options:
    - `python_e2e` — Python 後端 stack（FastAPI + Behave）
    - `java_e2e` — Java 後端 stack（Spring Boot 4 + Cucumber）
    - `nextjs_playwright` — Next.js 前端 stack（Storybook + playwright-bdd）
- recommendation: `python_e2e`
- answer.raw: {{Q1_RAW_ANSWER}}
- resolved_decision: { key: stack, value: {{Q1_RESOLVED_STACK}} }
- status: {{Q1_STATUS}}

### q2-project-spec-language

- prompt: 專案規格主要用哪一種語言撰寫？
- context: |
    決定 Gherkin executable step prose 與 feature filename title 的 language asset；
    DSL key 預設跟隨規格語言（`DSL_KEY_LOCALE = prefer_spec_language`）。
- options:
    - `zh-hant` — 繁體中文
    - `zh-hans` — 簡體中文
    - `en-us`  — 美式英文
    - `ja-jp`  — 日文
    - `ko-kr`  — 韓文
- recommendation: `zh-hant`
- answer.raw: {{Q2_RAW_ANSWER}}
- resolved_decision: { key: project_spec_language, value: {{Q2_RESOLVED_PROJECT_SPEC_LANGUAGE}} }
- status: {{Q2_STATUS}}

### q3-backend-service-name

- prompt: 這個 service 要叫什麼名字？
- context: |
    kebab-case，例如 `course-api`。寫入 boundary.yml 的 id。
    `java_e2e` 同時作為 Maven `<artifactId>`；`nextjs_playwright` 同時作為 `PROJECT_SLUG`。
- default: `backend`
- answer.raw: {{Q3_RAW_ANSWER}}
- resolved_decision: { key: tlb_id, value: {{Q3_RESOLVED_TLB_ID}} }
- status: {{Q3_STATUS}}

### q4-codebase-layout

- prompt: 程式碼要放在 repo root 還是子目錄？
- context: |
    `repo_root`：程式碼與 `specs/` 直接掛在 repo root（`BOUNDARY_CODEBASE_SUBDIR=""`）。
    `subdir`：所有程式碼與 `specs/` 掛在 `${PROJECT_ROOT}/${BOUNDARY_CODEBASE_SUBDIR}/`。
- options:
    - `repo_root` — 在 repo root（預設；`BOUNDARY_CODEBASE_SUBDIR=""`）
    - `subdir:<kebab-case-dir>` — 子目錄（回答格式：`Q4: subdir:<dir-name>`）
- recommendation: `repo_root`
- answer.raw: {{Q4_RAW_ANSWER}}
- resolved_decision: { key: boundary_codebase_subdir, value: {{Q4_RESOLVED_BOUNDARY_CODEBASE_SUBDIR}} }
- status: {{Q4_STATUS}}

## Resolved Decisions

```yaml
stack: {{RESOLVED_STACK}}
project_spec_language: {{RESOLVED_PROJECT_SPEC_LANGUAGE}}
tlb_id: {{RESOLVED_TLB_ID}}
boundary_codebase_subdir: {{RESOLVED_BOUNDARY_CODEBASE_SUBDIR}}
```
