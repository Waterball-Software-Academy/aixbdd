# Kickoff Plan Contract

`KICKOFF_PLAN.md` is the temporary interview state file for `/aibdd-kickoff`.
Kickoff asks all initial questions in one batch round; it must not ask them one
by one.

## File Identity

| Field | Value |
|---|---|
| Path | `${PROJECT_ROOT}/KICKOFF_PLAN.md` |
| Owner | `/aibdd-kickoff` |
| Lifetime | Temporary during kickoff |
| Formal artifact | No |

## Status Values

| Value | Meaning |
|---|---|
| `drafting_questions` | Questions are being rendered into the plan |
| `collecting_answers` | At least one question is waiting for user answer |
| `ready_to_execute` | All questions have resolved decisions |
| `artifacts_created` | Kickoff artifacts have been written |
| `confirmed` | User accepted the created artifacts |

## Required Sections

| Section | Required content |
|---|---|
| `## Status` | one status value |
| `## Context` | project root, plan path, artifact paths, supported stack statement |
| `## Questions` | question records keyed by stable question id |
| `## Resolved Decisions` | machine-readable decisions derived from answers |
| `## Artifact Plan` | files and folders to create |
| `## Execution Log` | created / updated / error records |

## Question Record Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | stable question id |
| `prompt` | yes | short question prompt recorded in the plan |
| `context` | yes | long explanation kept in the plan file |
| `options` | yes | selectable options; single-answer questions list one option |
| `ask_payload` | yes | short per-question payload fragment used to compose the one batch kickoff prompt |
| `answer.raw` | after answer | raw user answer |
| `answer.received_at` | after answer | timestamp |
| `resolved_decision.key` | after answer | machine-readable decision key |
| `resolved_decision.value` | after answer | normalized value |
| `resolved_decision.affects` | after answer | affected artifacts or decisions |
| `status` | yes | `unanswered` or `answered` |

## Batch Reply Contract

Kickoff collects Q1-Q4 in one user interaction round.

The rendered batch prompt must tell the user to reply in four labeled lines:

```text
Q1: python_e2e
Q2: zh-hant
Q3: backend
Q4: repo_root
```

Allowed normalized value shapes:

- `Q1`: one of `python_e2e`, `java_e2e`
- `Q2`: one of `zh-hant`, `zh-hans`, `en-us`, `ja-jp`, `ko-kr`
- `Q3`: `backend` or any kebab-case service name（Java stack 同時作為 Maven `<artifactId>`）
- `Q4`: `repo_root` or `subdir:<kebab-case-dir>`

If any question is missing, duplicated, or ambiguous, kickoff must mark the
plan unresolved and stop instead of silently continuing.

## Question IDs

| ID | Purpose | Required option shape |
|---|---|---|
| `q1-tech-stack` | Pick backend stack | exactly two selectable options (`python_e2e` / `java_e2e`), no `Other` |
| `q2-project-spec-language` | Collect project specification language | one BCP 47 option from `zh-hant`, `zh-hans`, `en-us`, `ja-jp`, `ko-kr` |
| `q3-backend-service-name` | Collect the only TLB id | kebab-case free-text answer or default acceptance（Java stack 同時作為 Maven `<artifactId>`） |
| `q4-backend-layout` | Decide whether backend lives at `${PROJECT_ROOT}` or `${PROJECT_ROOT}/${BACKEND_SUBDIR}` | two options (`repo_root` / `subdir`); `subdir` requires a kebab-case directory name |

## Final Confirmation Replies

Final confirmation goes through `/clarify-loop` as a single-question batch payload
(per the program-like verb glossary rule that planner-level skills must DELEGATE
`/clarify-loop` for any user-facing question). The three allowed normalized
replies remain the canonical option ids:

| Reply | Meaning |
|---|---|
| `confirm` | accept artifacts and delete `KICKOFF_PLAN.md` |
| `revise_plan` | return to plan revision |
| `show_plan` | keep plan and ask user to inspect it |
