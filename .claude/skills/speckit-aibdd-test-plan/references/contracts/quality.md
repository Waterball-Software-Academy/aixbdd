# speckit-aibdd-test-plan — Quality Gate Contract

## 5a — Script checks (machine-judgeable)

| Script | Responsibility |
|---|---|
| `clarify-loop/scripts/grep_sticky_notes.py` | `TEST_PLAN_OUT_DIR` 便條紙應為 0（或經使用者同意 defer） |
| `scripts/check_path_policy.py` | 確認輸出 Scenario 數 == parser 報告的 Path 數；policy='node-once' 時驗每節點經過 ≥1 |
| `scripts/check_dsl_reference.py` | 每個 Scenario 的 step 句型可在 shared `dsl.md` ⊕ boundary `dsl.md` 合併視圖中解析；有例外就 fail |

## 5b — Subagent semantic validation

Delegate to subagent with this instruction template (see SKILL.md Step 5b).
Checklist items map 1:1 to `test-plan-rules.md §4 R1–R12`.

### Baseline

- CIC_RESIDUAL — 無 `CiC(*)` 便條紙殘留於 `${TEST_PLAN_OUT_DIR}/*.feature`
- TEST_PLAN_RULES_COMPLIANCE — 每份 `.feature` 通過 R1–R12

### Axis-specific

- R1 PATH_SCENARIO_ONE_TO_ONE
- R2 TIME_ORDER_PRESERVED
- R3 ACTION_WHEN_THEN
- R4 NO_SCENARIO_OUTLINE
- R5 BACKGROUND_SHARED_ONLY
- R6 NO_TECHNICAL_MOCK_SURFACE
- R7 KEYWORDS_EN_DESCRIPTION_ZHTW
- R8 TAGS_COMPLETE
- R9 NO_IMPLEMENTATION_LEAK
- R10 PATH_NUMBER_MONOTONIC
- R11 ACTORS_DERIVED
- R12 SERIALIZATION_ROUND_TRIP

## Failure handling

- Any `ok=false` → 回 Step 3 → 重跑 Step 5 → 3 連敗 → 停下回報，不硬 loop
