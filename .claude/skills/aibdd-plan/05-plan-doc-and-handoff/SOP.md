# 參數設定

- **產出錨點** → 同 SKILL.md **PRINCIPLE: CWD 為產出錨點**；下列 `${…}` 均錨定於 **`CWD`**。
- **plan.md** → `${CURRENT_PLAN_PACKAGE}/plan.md`
- **research.md** → `${CURRENT_PLAN_PACKAGE}/research.md`
- **quality 報告** → `${CURRENT_PLAN_PACKAGE}/reports/aibdd-plan-quality.md`
- **deterministic 檢查腳本** → `scripts/python/check_*.py`（本 skill `scripts/python/` 目錄提供；若尚未提供，腳本缺失即 STOP 並報 scaffolding 不全）

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. **THINK：Impacted Feature Files**
   - **READ** `rules/impacted-feature-files-granularity.md`。
   - 從本輪 `$BOUNDARY_DELTA`／`$DSL_DELTA`／`$IMPLEMENTATION_MODEL` **FAITHFUL REASONING** 推出**本輪計畫實際驅動**之 `.feature` 子集；每條為 canonical repo-relative path，order 對齊預期 TDD phase order；每條 path **必可**在 `${FEATURE_SPECS_DIR}` 下解析。
   - 輸出 `$IMPACTED_FEATURE_FILES`（每筆含 `path` 與 optional `rationale`）。

2. **THINK：plan.md／research.md 內容**
   - **READ** `rules/plan-md-section-granularity.md`。
   - DRAFT `$PLAN_DOC`：必含 `## Discovery Sourcing Summary`（pointer）、`## Boundary Delta`、`## External Surface Model`、`## Implementation Paths`（逐 sequence 一行）、`## DSL Delta`（計數＋readability gate 警示）、`## Impacted Feature Files`（依 step 1 輸出逐條 bullet）、`## Quality Gate Verdict`（占位，step 4 後 finalize）。若 caller payload 含 reconcile context（`session_id`／`earliest_planner`／`cascade_chain`／`archive_path`）→ 補 `## Reconciliation Context` 章節。
   - DRAFT `$RESEARCH_DOC`：必含 `## Decisions`、`## Trade-offs`、`## Blocked Reasons`（合流 `$IMPLEMENTATION_MODEL.blocked_reasons[]`）、`## Open Questions`。

3. **TRIGGER：deterministic 腳本 gate**
   - TRIGGER 下列 `python3 scripts/python/...` 腳本，PARSE 結果合流為 `$SCRIPT_VERDICT`：`check_plan_phase.py`、`check_impacted_feature_files.py`、`check_truth_ownership.py`、`check_dsl_entries.py`、`check_handler_routing_consistency.py`、`check_${PRESET_KIND}_preset_refs.py`、`check_external_mock_policy.py`、`check_fixture_upload_mapping.py`、`check_sequence_diagrams.py`、`check_shared_dsl_template.py`。
   - IF `$SCRIPT_VERDICT.ok == false` → 列出 violations（rule_id／file／message），**禁止**弱化 gate 或繞過腳本，**STOP**。

4. **JUDGE：semantic quality verdict**
   - **READ** `rules/quality-gate-rubric.md`。
   - 對 `$BOUNDARY_DELTA`／`$EXTERNAL_SURFACE_MODEL`／`$IMPLEMENTATION_MODEL`／`$DSL_DELTA`／`$IMPACTED_FEATURE_FILES` 評 6 個 dimension（Q1 Role coherence／Q2 Owner-scoped truth／Q3 Planning completeness／Q4 DSL physical mapping quality／Q5 Preset use／Q6 Downstream handoff precision）。
   - Veto 命中即 `verdict = VETO`；無 veto 但任一 dimension < 0.7 → `SOFT_FAIL`；全部 ≥ 0.7 → `PASS`。
   - IF `verdict == VETO` → 列出 vetoes（含 evidence），**STOP**。

5. **WRITE FILES：plan.md／research.md／quality 報告**
   - 把 step 3 + step 4 verdict 合流回 `$PLAN_DOC` 之 `## Quality Gate Verdict`（含 actual script verdict evidence 與 dimension scores）。
   - CREATE `${CURRENT_PLAN_PACKAGE}/reports/`（若未存在）。
   - WRITE `${CURRENT_PLAN_PACKAGE}/plan.md`、`${CURRENT_PLAN_PACKAGE}/research.md`、`${CURRENT_PLAN_PACKAGE}/reports/aibdd-plan-quality.md`。

6. **EMIT 給使用者**（fire-and-forget，不等回覆）：列出本輪 truth／plan 變更摘要 — `boundary-map.yml`、`contracts/`（specifier 寫入）、`data/`（specifier 寫入）、`test-strategy.yml`、local／shared DSL、sequence diagrams、`internal-structure.class.mmd`、`plan.md`／`research.md`／quality 報告、blocking gaps、Git diff focus pointer。然後回到上層 SKILL.md step 6 之 handoff 一句話。
