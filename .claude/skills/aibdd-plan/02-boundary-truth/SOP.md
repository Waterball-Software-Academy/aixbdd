# 參數設定

- **產出錨點** → 同 SKILL.md **PRINCIPLE: CWD 為產出錨點**；下列 `${…}` 均錨定於 **`CWD`**。
- **boundary 真相根** → `${TRUTH_BOUNDARY_ROOT}`
- **boundary-map** → `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`
- **contracts／data 目錄** → `${TRUTH_BOUNDARY_ROOT}/contracts/`、`${TRUTH_BOUNDARY_ROOT}/data/`
- **frontend component contracts** → `${TRUTH_BOUNDARY_ROOT}/contracts/components/<id>/`（僅當 `$BOUNDARY_PROFILE.component_contract_specifier.skill != none`）
- **test strategy** → `${TEST_STRATEGY_FILE}`
- **specifier skills**（由 `$BOUNDARY_PROFILE` 派遣）→ `operation_contract_specifier.skill`、`state_specifier.skill`、`component_contract_specifier.skill`

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. **THINK：拆解本輪 boundary delta**
   - **READ** `rules/boundary-map-granularity.md`，鎖定 boundary-map 顆粒度與「不逐條 atomic rule 落地」原則。
   - 對 `$PLAN_INPUTS` 中每條被 impact 的 atomic rule，**FAITHFUL REASONING** 找其對應 module／contract operation／entity；**僅有**跨 boundary ownership／shared operation／非標準 module／planning gap 才需顯式 `dispatch_overrides`。
   - 輸出至訊息中之 `$BOUNDARY_DELTA`，含鍵：`modules`、`dispatch_overrides`、`provider_edges`、`persistence_ownership`、`components`（後者僅 frontend boundary 才有內容）。
   - 本步**只**產判斷結論，**不寫檔**。

2. **WRITE：boundary-map.yml**
   - 依 `$BOUNDARY_DELTA` 之 `modules` ∪ `dispatch_overrides` ∪ `provider_edges` ∪ `persistence_ownership` 寫入 `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`（merge 既有內容；不覆蓋未被本輪 impact 之區段）。
   - **本步僅允許 WRITE 此一檔**；contracts／data／components／test-strategy 一律走後續 step 委派／寫入。

3. **DELEGATE：operation contract（依 profile 派遣）**
   - **READ** `rules/contract-delegation-granularity.md`。
   - BRANCH `$BOUNDARY_PROFILE.operation_contract_specifier.skill`：
     - 非空（譬如 `/aibdd-form-api-spec`）→ 對 `$BOUNDARY_DELTA` 內每個 contract slice **DERIVE** caller payload（`operation_id`／`endpoint`／`method`／`request.{params, body, headers}`／`response.fields`／`errors`／`source_refs`），**逐 slice** `DELEGATE` 該 skill 寫入 `${TRUTH_BOUNDARY_ROOT}/contracts/`。
     - `none`／空 → ASSERT `$BOUNDARY_DELTA.contracts` 為空；非空則視為 ownership 違規，**STOP**。
     - 其他 → 列出不支援之 specifier，**STOP**。
   - 本步**禁止**手寫 OpenAPI／YAML contract 檔。

4. **DELEGATE：state（依 profile 派遣）**
   - **READ** `rules/state-delegation-granularity.md`。
   - BRANCH `$BOUNDARY_PROFILE.state_specifier.skill`：
     - 非空（譬如 `/aibdd-form-entity-spec`）→ 對 `$BOUNDARY_DELTA` 內每個 aggregate-root entity **DERIVE** caller payload（`entity_name`／`fields`／`relations`／`state_transitions`／`state_subset_visible_to_acceptance`／`source_refs`），**逐 entity** `DELEGATE` 該 skill 寫入 `${TRUTH_BOUNDARY_ROOT}/data/`。
     - `none`／空 → ASSERT `$BOUNDARY_DELTA.entities` 為空；非空則 **STOP**。
     - 其他 → **STOP**。
   - 本步**禁止**手寫 DBML／YAML state 檔。

5. **DELEGATE：component（僅 frontend boundary）**
   - **READ** `rules/component-delegation-granularity.md`。
   - BRANCH `$BOUNDARY_PROFILE.component_contract_specifier.skill`：
     - `/aibdd-form-story-spec`：若 `${CURRENT_PLAN_PACKAGE}/design.pen` 存在 → 先 `DELEGATE /aibdd-pen-to-storybook` 取 `component_table + tokens`，再 THINK 將 design × `$BOUNDARY_DELTA.components` × `$PLAN_INPUTS.feature_truth` × `${CURRENT_PLAN_PACKAGE}/design/uiux-prompt.md`（若存在）合成 enriched component payload；對每個 component **逐 component** `DELEGATE /aibdd-form-story-spec` 寫入 `${TRUTH_BOUNDARY_ROOT}/contracts/components/<id>/`。
     - `none`／空 → ASSERT `$BOUNDARY_DELTA.components` 為空；非空則 **STOP**。
     - 其他 → **STOP**。
   - 本步**禁止**手寫 `.tsx`／`.stories.tsx` 檔。

6. **WRITE：test-strategy.yml**
   - 依 `$BOUNDARY_DELTA.provider_edges` 之 test double policy 寫入 `${TEST_STRATEGY_FILE}`：每條 mockable consumer→provider edge **必有**一筆 strategy entry；同 boundary 內部協作者**不得**被列為 mock target。
