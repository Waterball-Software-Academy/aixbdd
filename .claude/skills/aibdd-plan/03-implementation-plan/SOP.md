# SOP

緣由：02 已把 boundary 對外契約（operation / state）落地，但只到 e2e 可驗證面；要讓下游 GREEN 不只「過測」、還能「結構 fit」，必須再做一層 internal design——以多條情境的 sequence diagram 為先導，收斂成一張類別圖（C4-Level class diagram）作為實作骨架，遵守 tidy-first（make the change easy, then make the easy change）。

1. READ `${DEV_CONSTITUTION_PATH}`；後續內部結構與分層須與之一致。

2. THINK：設計實作路徑與內部結構
   - READ `rules/sequence-path-granularity.md`、`reasoning/implementation-path-design.md`（SSOT、impact 覆蓋、path 可追溯、`$IMPLEMENTATION_MODEL` 形狀）。
   - 依上列規範 faithful reasoning 產出 `$IMPLEMENTATION_MODEL`；本步不寫檔。

3. CREATE `${PLAN_IMPLEMENTATION_DIR}`、`${PLAN_SEQUENCE_DIR}`；僅目錄，不預建空 `.mmd`。

4. WRITE sequence diagrams
   - FOR EACH path in `$IMPLEMENTATION_MODEL.paths`：寫入 `${PLAN_SEQUENCE_DIR}/<scenario_slug>.<category>.sequence.mmd`（Mermaid sequence）。每張必含：actor、boundary entry operation、internal collaborators、provider contract calls、state changes、response verifier candidates。
   - 不得把多條主要路徑塞入同一 `.mmd`；不得使用 `*.backend.sequence.mmd` 命名。

5. WRITE `${PLAN_INTERNAL_STRUCTURE}`
   - READ `rules/internal-structure-union.md`（其中定義「結構聯集」並附示意例）；依該定義把 `$IMPLEMENTATION_MODEL.paths` 收成單一 class diagram（collaborators／operations／state surfaces），供下游 GREEN 定位類別／模組／operation。
   - 不得含 product code patch、step definition 內容、test queue 狀態。

6. ASSERT 可追溯性
   - 每個 implementation target（actor、operation、collaborator、provider call、state change）至少可追溯至一條 activity path、atomic rule、provider contract 或 boundary-map dispatch。
   - 無法追溯者寫入 `$IMPLEMENTATION_MODEL.blocked_reasons[]`（含 target、原因），供後續 phase 在 `${PLAN_REPORTS_DIR}` 下由上游指定之 research 檔顯式落地；禁止靜默忽略。
