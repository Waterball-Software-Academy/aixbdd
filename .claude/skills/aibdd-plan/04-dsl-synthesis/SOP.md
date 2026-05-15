# 參數設定

- **產出錨點** → 同 SKILL.md **PRINCIPLE: CWD 為產出錨點**；下列 `${…}` 均錨定於 **`CWD`**。
- **package DSL** → `${BOUNDARY_PACKAGE_DSL}`（YAML registry；副檔名須為 `.yml`）
- **shared DSL** → `${BOUNDARY_SHARED_DSL}`（YAML registry；副檔名須為 `.yml`）
- **preset routing SSOT** → `aibdd-core/assets/boundaries/${PRESET_KIND}/handler-routing.yml`（`${PRESET_KIND}` 缺則 default `web-backend`）
- **DSL key locale** → `$DSL_KEY_LOCALE`（解析順序：arguments.yml `DSL_KEY_LOCALE` → 規格檔名 script profile → `DELEGATE /clarify-loop`）
- **persistence handler** → `$BOUNDARY_PROFILE.persistence_handler.{handler_id, state_ref_pattern, coverage_gate}`（其中 `coverage_gate` ∈ `not-null-columns | deferred-v1 | none`）

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. **DERIVE：`$DSL_KEY_LOCALE`**
   - 1.1 IF arguments.yml 已含 `DSL_KEY_LOCALE`（`prefer_spec_language`／`zh-hant`／`zh-hans`／`en-us`／`ja-jp`／`ko-kr`）→ 直取，GOTO step 2。
   - 1.2 ELSE 從 `${FEATURE_SPECS_DIR}`／`${ACTIVITIES_DIR}`／`${PLAN_SPEC}` 取最多 40 個 basenames，依 non-ASCII codepoint 比例分類為 `latin-heavy`／`non-latin-heavy`。`latin-heavy` → `$DSL_KEY_LOCALE = en-us`，GOTO step 2。
   - 1.3 ELSE → **DELEGATE** `/clarify-loop`，`delegated_intake.profile = aibdd-plan`、`phase = dsl-locale`，`raw_items` 含一題 `prefer_spec_language` vs `en-us` 之選擇（context 解釋規格檔名非英文時鍵名選擇）；回 `completed` 後取 `$DSL_KEY_LOCALE`。

2. **READ：preset routing policy**
   - PARSE `${PRESET_KIND}`（無則 default `web-backend`）。
   - READ `aibdd-core/assets/boundaries/${PRESET_KIND}/handler-routing.yml` 為 `$HANDLER_ROUTING`。
   - DERIVE `$PERSISTENCE_HANDLER = $BOUNDARY_PROFILE.persistence_handler.handler_id`、`$STATE_REF_PATTERN`、`$COVERAGE_GATE`。
   - ASSERT 三者皆非空且 `$COVERAGE_GATE ∈ {not-null-columns, deferred-v1, none}`；缺則 **STOP**。

3. **THINK：DSL delta**
   - **READ** `rules/dsl-entry-granularity.md`、`rules/dsl-binding-granularity.md`、`rules/dsl-禁止自生.md`。
   - 對 `$PLAN_INPUTS.feature_truth` 之**每條 atomic rule** **FAITHFUL REASONING** 產一筆 DSL entry，含 `id`／`source.{rule_id, boundary_id, feature_path}`／`L1`／`L2`／`L3.type`／`L4.{surface_id, surface_kind, callable_via, param_bindings, datatable_bindings, default_bindings, assertion_bindings, source_refs, preset}`。
   - **L1 placeholder ↔ binding key 為 1:1**（每個 `{placeholder}` 對應 `param_bindings` 或 `assertion_bindings` 之**恰好一筆**，never both、never none）。
   - 輸出 `$DSL_DELTA = { local_entries: [...], shared_entries: [...], no_op_reason: ... }`。本步**只**產推理結論，**不寫檔**。

4. **ASSERT：deterministic gates（語意層）**
   - 每條 entry：L1—L4 齊備；L4 binding target 限制前綴 `contracts/`、`data/`、`response`、`fixture`、`stub_payload`、`literal`。
   - operation 類 entry：`param_bindings + datatable_bindings + default_bindings` **恰好覆蓋** contract `request.params + request.body.fields + non-transport headers (required=true)`，多／少一個皆 fail；L1 sentence parameters ≤ 3；datatable parameters ≤ 6（after defaults）；defaults 必含 `target`／`value`／`reason`（指回 atomic rule）／`override_via`。
   - external dependency entry：surface_kind 對齊 preset 之 stub handler（`web-backend` → `external-stub`；`web-frontend` → `api-stub`），且**不得**指向同 boundary 內部協作者。
   - frontend UI handler（`ui-action`／`ui-readmodel-then`）：`L4.source_refs.component` 必指向具體 Story export（譬如 `Button.stories.ts::Primary`），非單一 component 檔（boundary invariant I4）。
   - persistence coverage（僅當 `$COVERAGE_GATE == not-null-columns`）：**READ** `rules/persistence-coverage.md`，逐 entity 驗 builder 之 NOT-NULL 覆蓋（豁免唯二：`[pk, increment]`、`[default: ...]`；FK NOT-NULL **不**得 lookup-chain 豁免）。
   - 任一 ASSERT 失敗 → 列出違規 entry／column／reason，**禁止**寫弱 placeholder DSL 讓下游 bypass，**STOP**。

5. **WRITE FILES：DSL registries**
   - IF `$DSL_DELTA.local_entries` 非空 → WRITE `${BOUNDARY_PACKAGE_DSL}`（merge 既有 entries）。
   - IF `$DSL_DELTA.shared_entries` 非空 → WRITE `${BOUNDARY_SHARED_DSL}`（merge 既有 entries）。
   - IF 兩者皆空 → ASSERT `$DSL_DELTA.no_op_reason` 非空，否則 **STOP**。
