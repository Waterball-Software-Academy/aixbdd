### q3-backend-service-name
- prompt: 這個 service 要叫什麼名字？
- kind: FREE
- default: backend
- answer.raw: {{Q3_ANSWER}}
- resolved_decision: { key: tlb_id, value: {{TLB_ID}} }
- status: {{Q3_STATUS}}

<!-- @guideline -->
**kebab-case**（全小寫、連字號分詞）。此值寫進 `boundary.yml` 的 `id`；`java_e2e` 同時作 Maven `<artifactId>`，`nextjs_playwright` 同時作 `PROJECT_SLUG`。
- good：`course-api`
- bad：`CourseAPI`（PascalCase）／`course_api`（snake_case）／`courseApi`（camelCase）／`course api`（含空白）
- expected（壞例修正）：一律轉成全小寫、以連字號分詞 → `course-api`

非 kebab-case 又無法安全正規化（如含空白或特殊字元）→ 標 unresolved 重問，不要自行猜一個。
reply token：`Q3: <kebab-case>`
