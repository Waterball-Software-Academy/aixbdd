# SOP

緣由：在推導完 system boundary 的 operation / data contracts 之後，就算是定義好了測試此邊界上最關鍵的兩個重要部位(operation for endpoint verifier, data for state verifier)，不過如果要建構更穩定的實作計劃，我們不能只有 e2e test，還要有 internal structural design，如此才能遵守 "tidy-first" (make changes easy then make easy change) 原則，讓程式不只能通過測試，還能有精準、fit-design、的好架構。

此步驟的目的是產出針對此實作計劃的 "程式實作類別圖 (C4-Level class diagram)"，以及作為更領先指標、用於推導出此類別圖的多個不同情境下的 Sequence diagram。

1. READ dev constitution：READ `${DEV_CONSTITUTION_PATH}`，後續內部結構與分層須與之一致。

2. THINK：設計實作路徑與內部結構
   - READ `rules/sequence-path-granularity.md`。
   - READ `reasoning/implementation-path-design.md`（SSOT、impact 覆蓋、path 可追溯、`$IMPLEMENTATION_MODEL` 形狀）
   - 依上列規範 faithful reasoning 產出 `$IMPLEMENTATION_MODEL`；本步不寫檔。

3. CREATE：`${PLAN_IMPLEMENTATION_DIR}`、`${PLAN_SEQUENCE_DIR}`。僅目錄；不預建空 `.mmd`。

4. WRITE：sequence diagrams
   - FOR EACH path in `$IMPLEMENTATION_MODEL.paths`：寫入 `${PLAN_SEQUENCE_DIR}/<scenario_slug>.<category>.sequence.mmd`（Mermaid sequence）。每張必含：actor、boundary entry operation、internal collaborators、provider contract calls、state changes、response verifier candidates。
   - 不得將多條主要路徑塞入同一 `.mmd`；不得使用 `*.backend.sequence.mmd` 命名。

5. WRITE：`${PLAN_INTERNAL_STRUCTURE}`
   - READ `rules/internal-structure-union.md`（相對本 `03-implementation-plan/`）：其中定義「結構聯集」並附示意例子；將 `$IMPLEMENTATION_MODEL.paths` 依該定義收成單一 class diagram（collaborators／operations／state surfaces），供下游 GREEN 定位類別／模組／operation。
   - 不得含 product code patch、step definition 內容、test queue 狀態。

6. ASSERT：可追溯性
   - 每個 implementation target（actor、operation、collaborator、provider call、state change）須至少可追溯至一條 activity path、atomic rule、provider contract 或 boundary-map dispatch。
   - 無法追溯者寫入 `$IMPLEMENTATION_MODEL.blocked_reasons[]`（含 target、原因），供後續 phase 在 plan package 內約定之 research 類工件顯式落地（例如 `${PLAN_REPORTS_DIR}` 下由上游指定的檔案）；禁止靜默忽略。
