# Quality Gate Rubric

本 sub-SOP step 4 之 `JUDGE` 依下列 dimension 評分（每 dimension 範圍 `0.0–1.0`）。最終 verdict：

- 任一 veto 命中 → `VETO`
- 無 veto 但任一 dimension < 0.7 → `SOFT_FAIL`
- 無 veto 且全部 dimension ≥ 0.7 → `PASS`

## Veto conditions（任一命中即 VETO）

- **Plan/truth path overlap**：技術真相被寫在 `${CURRENT_PLAN_PACKAGE}` 內。
- **Shadow truth**：contracts／data／test-strategy／DSL 之決策只存在 plan package、未落 boundary 真相。
- **Specifier bypass**：boundary profile 宣告 specifier 但本 skill 手寫 contract／data／story 檔。
- **Role boundary leak**：寫了 Discovery behavior／SbE Examples／tasks／product code／step definitions／runtime fixture。
- **DSL not red-usable**：entry 缺 L1—L4／`source_refs`／bindings／registry path，或 `check_dsl_entries.py` fail（含 operation required-input exact coverage 失敗）。
- **DSL mirrors API payload**：L1 暴露技術 request shape／過量 parameter。
- **DSL defaults without justification**：`default_bindings` 缺 atomic-rule reason／override policy。
- **DSL readability pressure failure**：L1 sentence parameters > 3、datatable parameters > 6（after defaults）、或用 default 隱藏 atomic rule 實際 vary 之行為。
- **DSL statelessness failure**：L1／Then／And 句子無法 stateless 解讀 subject／lookup identity／expected value。
- **DSL identity opacity**：ID-like target 之 key 不含 `ID`，或 dynamic ID 用 ambiguous alias（`$id`／`$previous.id` 等）。
- **DSL self-generation**：命中 `dsl-禁止自生.md` 之五類任一（動詞介面詞／數值技術欄位／隱性前提／hedging／同 boundary mock）。
- **Raw technical datatable payload**：datatable cell 含 JSON／YAML／DTO／DB-shape 而非業務 column。
- **Preset asset drift**：`handler-routing.yml` consistency check fail，或 entry `L4.preset` 無法解析。
- **Sequence path incompleteness**：happy／alt／err 合畫一張、用 legacy `*.backend.sequence.mmd` 命名、或主要路徑缺漏。
- **Impacted feature scope gap**：缺 `## Impacted Feature Files`、bullets 非 canonical repo-relative path、或路徑落在 `${FEATURE_SPECS_DIR}` 外。
- **External mock violation**：同 boundary 內部協作者被列為 mock target。
- **Fixture upload gap**：upload contract 存在但 DSL 缺 fixture／invocation／verifier。
- **Persistence coverage failure**：`$COVERAGE_GATE == not-null-columns` 但 NOT-NULL 覆蓋未達 100%（且非豁免項）。
- **Test-plan dependency**：completion 要求 `/aibdd-test-plan` 或 `speckit-aibdd-test-plan`。

## Weighted dimensions（每項 0.0–1.0）

- **Q1 Role coherence**：本 skill 表現為 technical planning orchestrator，不吞下 task／implementation／discovery behavior。
- **Q2 Owner-scoped truth**：所有真相寫到 owner-scoped 檔；Git diff 在實際真相檔上可審。
- **Q3 Planning completeness**：external surface／provider contracts／test strategy／sequence diagrams／internal-structure 皆 task-usable granularity；contract／state／component 格式對齊 boundary profile（透過 specifier 委派）。
- **Q4 DSL physical mapping quality**：bindings 對齊 contracts／data／response／fixture／stub_payload／literal；operation 之 required-input exact coverage；L1 keys 對齊 `$DSL_KEY_LOCALE`；readability／statelessness／identity 皆達標。
- **Q5 Preset use**：DSL entries 對齊 `${PRESET_KIND}` 之 handler 與 variant；無 boundary-local sentence-parts inventory；frontend invariants I1–I4 達標。
- **Q6 Downstream handoff precision**：plan.md／research.md／impacted features／contracts／data／test strategy／DSL／sequences／internal-structure／quality report／blocking gaps／Git diff focus 齊備可供 `/aibdd-spec-by-example-analyze` 直接消費。

## Verdict shape（寫入 `${CURRENT_PLAN_PACKAGE}/reports/aibdd-plan-quality.md`）

```json
{
  "verdict": "PASS | SOFT_FAIL | VETO",
  "vetoes": [{ "condition": "string", "evidence": "string" }],
  "dimension_scores": {
    "Q1": 1.0, "Q2": 1.0, "Q3": 1.0, "Q4": 1.0, "Q5": 1.0, "Q6": 1.0
  },
  "fix_hints": []
}
```
