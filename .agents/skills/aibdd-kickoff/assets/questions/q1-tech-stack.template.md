### q1-tech-stack
- prompt: 要建立哪一種 stack？
- kind: CON
- options: python_e2e | java_e2e | nextjs_playwright
- recommendation: python_e2e
- answer.raw: {{Q1_ANSWER}}
- resolved_decision: { key: stack, value: {{STACK}} }
- status: {{Q1_STATUS}}

<!-- @guideline -->
三選一，**無 Other**。各 option 含義：
- `python_e2e` — Python + FastAPI + SQLAlchemy + Alembic + Behave E2E + Testcontainers。
- `java_e2e` — Java + Spring Boot 4 + JdbcClient + Flyway + Cucumber 7 + Testcontainers。
- `nextjs_playwright` — Next.js 16 + Storybook 10 + playwright-bdd + Zod 4。

其他 frontend 框架、Unit-test-only、Mobile 尚未支援，本輪不提供；使用者答這些 → 標 unresolved，不要勉強對映。
reply token：`Q1: python_e2e | java_e2e | nextjs_playwright`
