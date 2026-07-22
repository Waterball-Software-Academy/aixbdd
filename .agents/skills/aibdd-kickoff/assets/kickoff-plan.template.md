# KICKOFF_PLAN

## Status
{{STATUS}}   <!-- collecting_answers | answered | executed -->

## Context
| 項目 | 值 |
|------|----|
| project root | {{PROJECT_ROOT}} |
| boundary codebase subdir | {{BOUNDARY_CODEBASE_SUBDIR}} |
| boundary codebase root | {{BOUNDARY_CODEBASE_ROOT}} |
| plan path | {{PLAN_PATH}} |
| supported stacks | python_e2e ｜ java_e2e ｜ nextjs_playwright |

## Questions
<!-- 依序插入 q1–q3 與條件式 q4–q5 各自的 question record（來源：assets/questions/q*-*.template.md）；-->
{{Q1_RECORD}}

{{Q2_RECORD}}

{{Q3_RECORD}}

{{Q4_RECORD}}

{{Q5_RECORD}}

## Resolved Decisions
<!-- machine-readable，給 kickoff_layout.py 消費 -->
```yaml
stack: {{STACK}}                              # python_e2e | java_e2e | nextjs_playwright
project_spec_language: {{PROJECT_SPEC_LANGUAGE}}  # zh-hant | zh-hans | en-us | ja-jp | ko-kr
tlb_id: {{TLB_ID}}                            # kebab-case
boundary_codebase_subdir: {{BOUNDARY_CODEBASE_SUBDIR}}   # "" | <kebab-case>
data_schema_format: {{DATA_SCHEMA_FORMAT}}    # web-service: dbml | postgresql | mysql | mssql ；其他 type: n/a
install_spectrum: {{INSTALL_SPECTRUM}}        # true | false（Q5；僅 java_e2e 生效，由 SOP 回填 arguments.yml 的 INSTALL_SPECTRUM）
# Optional Java overrides（缺則由 script 推導）：
# group_id: com.example
# base_package: com.example.<tlb-id without hyphens>
# db_name: <tlb_id with - replaced by _>
```

<!-- @guideline -->
**File Identity**：本檔是 File-First 的暫存訪談檔，Owner = `/aibdd-kickoff`，**非正式 artifact**，Phase 5 完成後刪除。落點 `${PLAN_PATH}` = `${PROJECT_ROOT}/KICKOFF_PLAN.md`。

**組裝**：`## Questions` 段由 `assets/questions/q1..q3-*.template.md` 與條件式 `q4..q5-*.template.md` question record 依序填入；Q4／Q5 為條件式第二輪：Q4 僅 `type: web-service`、Q5 僅 stack `java_e2e`，不符即留空）；每支題目本文與 reply token 以該檔為 SSOT，本殼不重述題目細節。

**Batch Reply Format**（`/clarify` 一次問完 Q1–Q3，禁逐題往返）：
```text
Q1: python_e2e | java_e2e | nextjs_playwright
Q2: zh-hant | zh-hans | en-us | ja-jp | ko-kr
Q3: <kebab-case>            # java_e2e 同時為 Maven artifactId；nextjs_playwright 同時為 PROJECT_SLUG
```

**Q4 Reply Format**（僅 `type: web-service` 才在第二輪 `/clarify` 提問；其他 type 不問）：
```text
Q4: dbml | ddl:postgresql | ddl:mysql | ddl:mssql
```

**Q5 Reply Format**（僅 stack `java_e2e`（type `web-service`）才在第二輪 `/clarify` 提問；其他 stack／type 不問）：
```text
Q5: yes | no               # 是否安裝 aibdd-spectrum
```

**Question record 欄位**：`id` / `prompt` / `kind`（`CON` 選項題｜`FREE` 自由題）/ `options` 或 `default` / `answer.raw`（答後）/ `resolved_decision.key` + `.value`（答後）/ `status`（`unanswered` → `answered`，無法解析則 `unresolved`）。
