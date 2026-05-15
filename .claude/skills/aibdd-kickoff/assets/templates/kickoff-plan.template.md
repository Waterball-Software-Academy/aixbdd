<!-- INSTRUCT: Render this template to `${PROJECT_ROOT}/KICKOFF_PLAN.md`. Fill every {{PLACEHOLDER}} before writing. Keep this file as a temporary interview plan, not a formal spec artifact. -->

# KICKOFF_PLAN

## Status

{{STATUS}}

## Context

| Field | Value |
|---|---|
| Project root | `{{PROJECT_ROOT}}` |
| Backend subdir | `{{BACKEND_SUBDIR}}` |
| Backend root | `{{BACKEND_ROOT}}` |
| Frontend subdir | `{{FRONTEND_SUBDIR}}` |
| Frontend root | `{{FRONTEND_ROOT}}` |
| Plan path | `{{PLAN_PATH}}` |
| Arguments path | `{{ARGS_PATH}}` |
| Boundary path | `{{BOUNDARY_YML_PATH}}` |
| Component diagram path | `{{COMPONENT_DIAGRAM_PATH}}` |
| Supported stacks | Python + FastAPI + SQLAlchemy + Behave E2E ｜ Java + Spring Boot 4 + JdbcClient + Cucumber E2E ｜ TypeScript + Next.js + Storybook + Playwright BDD |

## Questions

<!-- INSTRUCT: Each question is written before the single kickoff batch ASK is called. After the user answers the whole batch, fill Answer / Resolved decision / Status for every question. -->

### q1-tech-stack

Prompt: 要建立哪一種技術 stack？

Context:
- python_e2e：Python + FastAPI + SQLAlchemy + Alembic + Behave E2E。
- java_e2e：Java + Spring Boot 4 + JdbcClient + Flyway + Cucumber E2E。
- nextjs_playwright：TypeScript + Next.js 16 + React 19 + Storybook 10 + Tailwind 4 + Zod 4 + playwright-bdd + Playwright。
- 其他 frontend 框架、Unit Test only、Mobile 尚未支援。

Options:
| Option | Meaning |
|---|---|
| `python_e2e` | Python 後端 stack |
| `java_e2e` | Java 後端 stack |
| `nextjs_playwright` | TypeScript / Next.js 前端 stack |

Ask payload:
- title: Tech stack
- prompt: 要建立哪一種技術 stack？
- options: [`python_e2e`, `java_e2e`, `nextjs_playwright`]
- allow_other: false

Answer:
- raw: {{Q1_RAW_ANSWER}}
- received_at: {{Q1_RECEIVED_AT}}

Resolved decision:
- key: stack
- value: {{Q1_RESOLVED_STACK}}
- affects:
  - arguments.yml
  - boundary.yml
  - component-diagram.class.mmd

Status: {{Q1_STATUS}}

### q2-project-spec-language

Prompt: 專案規格主要用哪一種語言撰寫？

Context:
- 此設定會成為 `PROJECT_SPEC_LANGUAGE`。
- 此設定會推導 Gherkin executable step prose 與 feature filename title 的 language asset。
- `DSL_KEY_LOCALE` 預設為 `prefer_spec_language`。

Options:
| Option | Meaning |
|---|---|
| `zh-hant` | 繁體中文 |
| `zh-hans` | 簡體中文 |
| `en-us` | 美式英文 |
| `ja-jp` | 日文 |
| `ko-kr` | 韓文 |

Ask payload:
- title: Project spec language
- prompt: 專案規格主要用哪一種語言撰寫？
- options: [`zh-hant`, `zh-hans`, `en-us`, `ja-jp`, `ko-kr`]
- allow_other: false

Answer:
- raw: {{Q2_RAW_ANSWER}}
- received_at: {{Q2_RECEIVED_AT}}

Resolved decision:
- key: project_spec_language
- value: {{Q2_RESOLVED_PROJECT_SPEC_LANGUAGE}}
- affects:
  - arguments.yml

Status: {{Q2_STATUS}}

### q3-backend-service-name

Prompt: 這個 top-level boundary 要叫什麼名字？

Context:
- 這個名稱會成為唯一 top-level boundary id。
- 名稱必須是 kebab-case，例如 `course-api` 或 `course-ui`。
- 後端 stack 若未指定，預設為 `backend`；Next.js stack 若未指定，預設為 `frontend`。
- Java stack 會把此值當作 Maven artifactId；Next.js stack 會把此值當作 `PROJECT_SLUG`。

Options:
| Option | Meaning |
|---|---|
| `backend` | 使用後端預設名稱 |
| `frontend` | 使用前端預設名稱 |
| `custom` | 使用自訂 kebab-case 名稱 |

Ask payload:
- title: Boundary name
- prompt: 這個 top-level boundary 要叫什麼名字？
- options: [`backend`, `frontend`, `<custom-kebab-case>`]

Answer:
- raw: {{Q3_RAW_ANSWER}}
- received_at: {{Q3_RECEIVED_AT}}

Resolved decision:
- key: tlb_id
- value: {{Q3_RESOLVED_TLB_ID}}
- affects:
  - boundary.yml
  - component-diagram.class.mmd
  - boundary truth skeleton folders

Status: {{Q3_STATUS}}

### q4-backend-layout

Prompt: 程式碼要放在 repo root 還是子目錄？

Context:
- 預設 `repo_root`：選定 stack 與 specs/ 直接掛在 repo root。
- 後端 stack 使用 `BACKEND_SUBDIR` / `BACKEND_ROOT`。
- Next.js stack 使用 `FRONTEND_SUBDIR` / `FRONTEND_ROOT`。
- 選 `subdir`：必須提供子目錄名（kebab-case，例如 `backend` 或 `frontend`），所有 code 與 specs/ 都掛在 `${PROJECT_ROOT}/<subdir>/`。
- 此決定影響 `arguments.yml` 寫入位置與 `/aibdd-auto-starter` same-repo guard。

Options:
| Option | Meaning |
|---|---|
| `repo_root` | 選定 stack 在 repo root；對應 subdir="" |
| `subdir` | 選定 stack 在子目錄；後續以自由輸入提供 subdir 值 |

Ask payload:
- title: Project layout
- prompt: 程式碼要放在 repo root 還是子目錄？
- options: [`repo_root`, `subdir`]
- allow_other: false（若選 `subdir`，使用批次回答格式 `Q4: subdir:<kebab-case-dir>`）

Answer:
- raw: {{Q4_RAW_ANSWER}}
- received_at: {{Q4_RECEIVED_AT}}

Resolved decision:
- key: stack_subdir
- value: {{Q4_RESOLVED_STACK_SUBDIR}}
- affects:
  - arguments.yml location
  - all path-derived directories under specs/
  - selected stack code/test directories
  - starter same-repo guard

Status: {{Q4_STATUS}}

## Resolved Decisions

```yaml
stack: {{RESOLVED_STACK}}
test_strategy: e2e
project_spec_language: {{RESOLVED_PROJECT_SPEC_LANGUAGE}}
tlb_id: {{RESOLVED_TLB_ID}}
boundary_role: {{RESOLVED_BOUNDARY_ROLE}}
boundary_type: {{RESOLVED_BOUNDARY_TYPE}}
stack_subdir: {{RESOLVED_STACK_SUBDIR}}
backend_subdir: {{RESOLVED_BACKEND_SUBDIR}}
frontend_subdir: {{RESOLVED_FRONTEND_SUBDIR}}
```

## Artifact Plan

Files:
- `{{ARGS_PATH}}`
- `{{BOUNDARY_YML_PATH}}`
- `{{COMPONENT_DIAGRAM_PATH}}`
- `{{BOUNDARY_SHARED_DSL}}`
- `{{TEST_STRATEGY_FILE}}`

Folders:
- `{{TRUTH_BOUNDARY_ROOT}}/contracts/`
- `{{TRUTH_BOUNDARY_ROOT}}/data/`
- `{{TRUTH_BOUNDARY_ROOT}}/shared/`
- `{{TRUTH_BOUNDARY_PACKAGES_DIR}}/` （僅 functional package root，不預先建立 `NN-<功能模組描述>/`）

Note: `TRUTH_FUNCTION_PACKAGE` / package 內 `activities`/`features`/`test-plan`/`dsl.yml` 由 `/aibdd-discovery` 在 sourcing 後 late-bind。

## Execution Log

Created:
{{CREATED_PATHS}}

Updated:
{{UPDATED_PATHS}}

Errors:
{{ERRORS}}
