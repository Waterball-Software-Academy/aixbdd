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
<!-- 依序插入 q1–q4 各自的 question record（來源：assets/questions/q{1..4}-*.template.md） -->
{{Q1_RECORD}}

{{Q2_RECORD}}

{{Q3_RECORD}}

{{Q4_RECORD}}

## Resolved Decisions
<!-- machine-readable，給 kickoff_layout.py 消費 -->
```yaml
stack: {{STACK}}                              # python_e2e | java_e2e | nextjs_playwright
project_spec_language: {{PROJECT_SPEC_LANGUAGE}}  # zh-hant | zh-hans | en-us | ja-jp | ko-kr
tlb_id: {{TLB_ID}}                            # kebab-case
boundary_codebase_subdir: {{BOUNDARY_CODEBASE_SUBDIR}}   # "" | <kebab-case>
# Optional Java overrides（缺則由 script 推導）：
# group_id: com.example
# base_package: com.example.<tlb-id without hyphens>
# db_name: <tlb_id with - replaced by _>
```

<!-- @guideline -->
**File Identity**：本檔是 File-First 的暫存訪談檔，Owner = `/aibdd-kickoff`，**非正式 artifact**，Phase 5 完成後刪除。落點 `${PLAN_PATH}` = `${PROJECT_ROOT}/KICKOFF_PLAN.md`。

**組裝**：`## Questions` 段由 `assets/questions/q1..q4-*.template.md` 四支 question record 依序填入；每支題目本文與 reply token 以該檔為 SSOT，本殼不重述題目細節。

**Batch Reply Format**（`/clarify-loop` 一次問完 Q1–Q4，禁逐題往返）：
```text
Q1: python_e2e | java_e2e | nextjs_playwright
Q2: zh-hant | zh-hans | en-us | ja-jp | ko-kr
Q3: <kebab-case>            # java_e2e 同時為 Maven artifactId；nextjs_playwright 同時為 PROJECT_SLUG
Q4: repo_root | subdir:<kebab-case-dir>
```

**Question record 欄位**：`id` / `prompt` / `kind`（`CON` 選項題｜`FREE` 自由題）/ `options` 或 `default` / `answer.raw`（答後）/ `resolved_decision.key` + `.value`（答後）/ `status`（`unanswered` → `answered`，無法解析則 `unresolved`）。
