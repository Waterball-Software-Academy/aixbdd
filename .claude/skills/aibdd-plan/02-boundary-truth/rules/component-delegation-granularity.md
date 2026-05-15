# Component 委派顆粒度（僅 frontend boundary）

- **適用條件**：`$BOUNDARY_PROFILE.component_contract_specifier.skill = /aibdd-form-story-spec`；其他 boundary（譬如 `web-service`）此 rules **不適用**，`$BOUNDARY_DELTA.components` 必須為空。
- **唯一寫入管道**：`${TRUTH_BOUNDARY_ROOT}/contracts/components/**` 之任何 `.tsx`／`.stories.tsx`，**必須**由 `/aibdd-form-story-spec` 寫；本 skill **不得**手寫。
- **一個 component 一次 DELEGATE**：每個獨立 component identifier 為一次 DELEGATE；caller payload 必含 `identifier`／`title`／`props[]`／`render_hints.{root_element, children_layout}`／`stories[]`（每 story 含 `export_name`／`role`／`accessible_name`／`accessible_name_arg`）／`design_source`（`kind=pen` 時帶 `path`／`screen_id`／`style_profile_path`，否則 `kind=none`）。
- **design 來源**：當 `${CURRENT_PLAN_PACKAGE}/design.pen` 存在 → 先 `DELEGATE /aibdd-pen-to-storybook` 取 `component_table + tokens`；再 THINK 合成 `$BOUNDARY_DELTA.components` × `feature_truth` × `activity_truth` × `uiux-prompt.md` 為 enriched payload。
- **stories 必非空**：每個 component **至少一條** story export；ui-action／ui-readmodel-then DSL 之 component source_ref 必指向具體 story export，故無 story 即無法 anchor。

# 反例

- 為 `web-service` boundary 產生 component payload——對應 specifier 為 `none`，產出即為違規。
- 一次 DELEGATE 帶 5 個 component——specifier 之單位是 single component；多 component 包裝會讓 story 之 accessible-name granularity 失焦。
- `stories[]` 為空——boundary invariant I4 要求 UI handler 之 component source_ref 必指向具體 story export；無 story 即無 anchor。
- `accessible_name` 寫成 `"按鈕"` 而非具體業務語意（例如 `"送出訂單"`）——下游 ui-action handler 無法 deterministic 定位元素。

# 禁止自生

- **不得**自填 raw 未授權之 prop 名／role；每個 prop 必須在 atomic rule、design.pen 或 uiux-prompt.md 中找得到對應出處。
- **不得**為「美觀」自加 design token；token 必須來自 design.pen 或 `style-profile.yml` 真相，否則保留 default by variant。
- **不得**自加 raw 未提之互動行為（譬如 atomic rule 沒提 hover state，payload 不得加 hover story 變體）。
