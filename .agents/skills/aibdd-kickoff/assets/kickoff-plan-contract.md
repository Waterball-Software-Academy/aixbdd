# KICKOFF_PLAN.md Contract

File First 暫存訪談檔。`/aibdd-kickoff` 一次問完 Q1–Q4，**禁止**逐題往返。

## File Identity

| Field | Value |
|---|---|
| Path | `${PROJECT_ROOT}/KICKOFF_PLAN.md` |
| Owner | `/aibdd-kickoff` |
| Lifetime | Temporary（02-execute-layout 完成後 DELETE） |
| Formal artifact | No |

## Required Sections

| Section | Content |
|---|---|
| `## Status` | `collecting_answers` / `answered` / `executed` |
| `## Context` | project root / boundary codebase subdir / plan path / supported stacks |
| `## Questions` | 每題 question record（id / prompt / context / options / answer / status） |
| `## Resolved Decisions` | machine-readable YAML 給 `kickoff_layout.py` 消費 |

## Question Record Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | stable question id（見 `questions.yml`） |
| `prompt` | yes | 短問題 |
| `context` | yes | 長說明（從 `questions.yml` `.context` 取） |
| `options` | yes | 可選項；free-text 題填 `kind: FREE` |
| `answer.raw` | after answer | user 原始回答 |
| `resolved_decision.key` | after answer | machine-readable key |
| `resolved_decision.value` | after answer | normalized value |
| `status` | yes | `unanswered` / `answered` |

## Batch Reply Format

```text
Q1: python_e2e | java_e2e | nextjs_playwright
Q2: zh-hant | zh-hans | en-us | ja-jp | ko-kr
Q3: <kebab-case>            # java_e2e 同時為 Maven artifactId；nextjs_playwright 同時為 PROJECT_SLUG
Q4: repo_root | subdir:<kebab-case-dir>
```

## Resolved Decisions YAML（給 script 用）

```yaml
stack: python_e2e | java_e2e | nextjs_playwright
project_spec_language: zh-hant | zh-hans | en-us | ja-jp | ko-kr
tlb_id: <kebab-case>
boundary_codebase_subdir: "" | <kebab-case>
# Optional Java overrides（缺則由 script 推導）：
# group_id: com.example
# base_package: com.example.<tlb-id without hyphens>
# db_name: <tlb_id with - replaced by _>
```

## Question IDs（SSOT 詳見 `questions.yml`）

| ID | Purpose | Option shape |
|---|---|---|
| `q1-tech-stack` | Pick stack | 三選一：`python_e2e` / `java_e2e` / `nextjs_playwright`；無 `Other` |
| `q2-project-spec-language` | Spec language | BCP-47 五選一 |
| `q3-backend-service-name` | TLB id | kebab-case free-text；預設 `backend` |
| `q4-codebase-layout` | Codebase root | `repo_root` 或 `subdir:<dir>` |

模糊／重複／缺題 → 標 `unresolved` 並 STOP，**禁止**靜默繼續。
