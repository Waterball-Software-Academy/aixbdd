# Forbidden Mutations

> 純 declarative reference。本 skill 全程禁止寫入以下檔案。
>
> 來源：原 SKILL.md `## Forbidden mutations`。

## §1 禁寫範圍

- `${BOUNDARY_PACKAGE_DSL}` / `${BOUNDARY_SHARED_DSL}` — `/aibdd-plan` owner。缺 L4 binding → 停下並回上游，不得就地補
- `${CONTRACTS_DIR}/**` — `/aibdd-plan` + contract specifier owner。缺 OpenAPI operation/field → 停下並回上游
- `${DATA_DIR}/**` — `/aibdd-plan` + entity specifier owner。缺 DBML table/field → 停下並回上游
- `${TEST_STRATEGY_FILE}` — `/aibdd-plan` owner。缺 dependency edge / external stub policy → 停下並回上游
- `${CURRENT_PLAN_PACKAGE}/plan.md` / `research.md` / `implementation/**` / `reports/aibdd-plan-quality.md` — `/aibdd-plan` owner
- `${PLAN_SPEC}` / `${PLAN_REPORTS_DIR}/discovery-sourcing.md` / `${ACTIVITIES_DIR}/**` — `/aibdd-discovery` owner
- `${FEATURE_SPECS_DIR}/**/*.feature` 的既有 Rule 本體 — 只得移除 `@ignore`、移除 analyzer-only comment、補 Scenario / Scenario Outline / Examples；不得改 Rule 字詞（NO_RULE_WORDING_CHANGE gate）

## §2 違反處理

違反上列 → 本 skill 立即 abort + REPORT 違反路徑 + STOP。

## §3 理由

per 本檔 §1 禁寫範圍與 artifact owner 邊界 — 上游 artifact 在下游 phase 不得被修改。
