---
name: aibdd-form-activity
description: 將 discovery 產出的 Activity modeling elements 逐一翻譯成 `.activity` DSL，寫入檔案並執行語法驗證。
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-form-activity

Formulation skill。只負責把 `discovery.02-activity-analyze` 已完成的 Activity modeling elements 轉成 `.activity` 語法；不重新判斷 actor 合法性、action 顆粒度、reuse、operation partition、或需求語意。

## §1 REFERENCES

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `aibdd-core::spec-package-paths.md` | global | kickoff boundary-aware path SSOT |
| R2 | `aibdd-core::report-contract.md` | global | DELEGATE report 規範 |
| R3 | `references/role-and-contract.md` | Phase 1 | caller payload schema + role boundary |
| R4 | `references/format-reference.md` | Phase 2 | Activity element → `.activity` syntax mapping |
| R5 | `scripts/decoder.py` | Phase 4 | `.activity` DSL decoder（同時為 SKILL.md Phase 4 syntax validator 與 BDD subject；spec SSOT = `scripts/tests/activity-decode.feature` + `scripts/tests/activity-benchmark.feature`） |

## §2 SOP

### Phase 1 — ASSERT intake｜驗證 caller payload
> produces: `$$payload`, `$$target_path`, `$$format`, `$$activity`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$payload` = READ caller payload
3. `$$target_path` = PARSE `$$payload.target_path`
4. `$$format` = PARSE `$$payload.format`
5. `$reasoning` = PARSE `$$payload.reasoning`
6. `$$activity` = PARSE `$reasoning.activity_analysis.activity`
7. `$graph_gaps` = PARSE `$reasoning.activity_analysis.graph_gaps`
8. `$exit_status` = PARSE `$reasoning.activity_analysis.exit_status`
9. `$payload_ok` = JUDGE `$$payload` against `$contract`
10. ASSERT `$payload_ok`
11. ASSERT `$$target_path` non-empty
12. ASSERT `$$format == ".activity"`
13. ASSERT `$$activity.name` non-empty
14. ASSERT `$$activity.initial` exists
15. ASSERT count(`$$activity.finals`) >= 1
16. ASSERT every element in `$$activity.nodes` is one of `Action | Decision | Fork | Merge | Join`
17. ASSERT `$exit_status == "complete"`
18. ASSERT count(`$graph_gaps`) == 0

### Phase 2 — RENDER element by element｜轉成 Activity DSL
> produces: `$$activity_doc`

1. `$syntax_map` = READ [`references/format-reference.md`](references/format-reference.md)
2. `$header` = RENDER `[ACTIVITY] ${$$activity.name}`
3. `$actors` = RENDER one `[ACTOR]` line per `$$activity.actors[]`
4. `$initial` = RENDER `[INITIAL]`
5. `$node_lines` = DERIVE empty line list
6. LOOP per `$node` in `$$activity.nodes`
   6.1 BRANCH `$node.type`
       ui_step | command | query:
         6.1.1 `$line` = RENDER Action as `[STEP:${$node.display_id}] @${actor.name} ${$node.name} {${$node.binds_feature}}`
       decision:
         6.1.2 `$line` = RENDER Decision as `[DECISION:${$node.display_id}] ${$node.condition}`
        6.1.3 `$path_lines` = RENDER every `decision_path` as `[BRANCH:${$node.display_id}:${path.guard}]`
       fork:
         6.1.4 `$line` = RENDER Fork as `[FORK:${$node.display_id}]`
        6.1.5 `$path_lines` = RENDER every `fork_path` as `[PARALLEL:${$node.display_id}]`
       merge:
         6.1.6 `$line` = RENDER Merge as `[MERGE:${$node.display_id}]`
       join:
         6.1.7 `$line` = RENDER Join as `[JOIN:${$node.display_id}]`
   6.2 `$node_lines` = DERIVE append `$line` and `$path_lines`
   END LOOP
7. `$finals` = RENDER one `[FINAL]` line per `$$activity.finals[]`
8. `$$activity_doc` = RENDER `.activity` document from `$header`, `$actors`, `$initial`, `$node_lines`, and `$finals`
9. ASSERT `$$activity_doc` contains `[ACTIVITY]`, `[INITIAL]`, and `[FINAL]`

### Phase 3 — WRITE artifact｜寫入 Activity 檔
> produces: `$$written_paths`

1. `$target_exists` = MATCH path_exists(`$$target_path`)
2. IF `$target_exists` ∧ `$$payload.mode != "overwrite"`:
   2.1 `$msg` = DRAFT "path 衝突：target_path 已存在，caller 需指定 mode=overwrite 或改 target_path"
   2.2 RETURN `$msg`
3. WRITE `$$target_path` ← `$$activity_doc`
4. `$$written_paths` = DERIVE [`$$target_path`]
5. ASSERT `$$target_path` in `$$written_paths`

### Phase 4 — VALIDATE syntax｜語法驗證
> produces: `$$validation_report`

1. `$validator` = COMPUTE `scripts/decoder.py`
2. `$validation_out` = TRIGGER `python3 ${$validator} ${$$target_path}`
3. `$$validation_report` = PARSE `$validation_out`, schema=activity-syntax-validation-report
4. ASSERT `$$validation_report.ok == true`

### Phase 5 — RETURN report｜回傳 caller 訊號
> produces: `$$report`

1. `$$report` = DRAFT report JSON per `aibdd-core::report-contract.md` ← {status: "completed", target_path: `$$target_path`, written_paths: `$$written_paths`, syntax_valid: `$$validation_report.ok`, validation_report: `$$validation_report`}
2. RETURN `$$report`

## §3 FAILURE & FALLBACK

### Phase 1 fail handling
- IF caller payload 完全空: RETURN "empty payload — caller misuse"
- IF `target_path` 未指定: RETURN "target_path missing"
- IF `format != ".activity"`: RETURN "format unsupported"
- IF `reasoning.activity_analysis.activity` 缺失: RETURN "activity modeling elements missing"

### Phase 2 fail handling
- IF Activity element 無法映射到 `.activity` tag: RETURN element formulation error
- IF Actor reference 無法 resolve 成 actor name: RETURN actor reference error

### Phase 3 fail handling
- IF WRITE IO 失敗: RETURN IO error to caller
- IF `target_path` 已存在且 mode != overwrite: RETURN path conflict

### Phase 4 fail handling
- IF validator exit != 0: RETURN syntax validation report to caller
- IF validator JSON parse 失敗: RETURN validator protocol error

### Phase 5 fail handling
- IF RETURN 失敗（caller 已斷線）: WRITE `${$$target_path}.report` ← `$$report`

## §4 CROSS-REFERENCES

- 由 `aibdd-discovery/reasoning/discovery/02-activity-analyze.md` Material Reducer SOP DELEGATE。
- 上游必須先完成 Activity modeling；本 skill 不補需求、不改顆粒度、不新增 model element。
