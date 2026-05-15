# Quality Gate Rubric（執行 rubric）

本檔是 05 step 7 之**執行視角**規則；veto／dimension／verdict shape 之 SSOT 為 `../references/contracts/quality.md`（避免重抄）。本檔只 expose 執行時最需要的精簡判定流程與常見誤判反例。

## §1 判定流程（依序）

1. **Veto 掃描**（任一命中即 `VETO`，仍計算 dimension scores 以利 fix_hints）：
   - 對照 `../references/contracts/quality.md` §3 veto 清單逐條檢，每命中一筆寫入 `vetoes[]`，含 `condition` + `evidence: <path:line — sentence>`。
2. **Dimension scoring**（每項 0.0–1.0）：
   - Q1 Truth fidelity：atomic rule wording / feature path / DSL / contract / data / test-strategy 全 byte-identical
   - Q2 Example completeness：每條 atomic rule × dimension 矩陣填滿或標 CiC；BVA／State Transition／Decision Table 之必備維度齊
   - Q3 Binding traceability：每個 step／Examples 欄位有 `dsl_binding_trace` 指 L4 binding 或 OpenAPI／DBML
   - Q4 Minimal rule-target focus：每條 example 只驗其 atomic rule axis；跨 axis 旁路必為 dynamic-id bridge 並 trace
3. **Verdict 決定**：
   - 任一 veto → `VETO`
   - 無 veto 但任一 Q < 0.7 → `SOFT_FAIL`
   - 無 veto 且 Q1–Q4 ≥ 0.7 → `PASS`

## §2 容易誤判之邊界

- **dynamic-id bridge 例外**：state-rule example 含 `When response.body.orderId = ?` 並接 `Then DB.orders[?].status = ...` → **不**算違 `MINIMAL_RULE_TARGET_EXAMPLE` veto，因為 state verifier 必須用 dynamic id；但必須在 `binding_trace` 標 `dynamic_id_bridge: true`，否則仍 veto。
- **`@ignore` 在 stub Scenario 上**：04 規劃時尚未填 example 之 stub Scenario 帶 `@ignore` tag 不算違 veto（合法待填）；05 DELEGATE 完成後仍存 `@ignore` 才算違 `ATOMIC_RULE_EXAMPLE_COVERAGE`。
- **`dimension_na` 註記**：rule 只描述禁止行為時，`happy_path` dimension 可標 `dimension_na` 並附理由；matrix 不視為空格。

## §3 fix_hints 寫法

- 每筆 `{ target: <path:line>, hint: <≤120 字> }` 必須指明**具體下一步**，譬如「在 `${BOUNDARY_PACKAGE_DSL}` 為 entity X 加 state-builder builder」「在 `${CONTRACTS_DIR}/orders.yml` operation `op_create_order` 之 responses.400 補 `description`」。
- **不得**寫抽象 hint（譬如「改善 binding」）——不可執行 hint = 無價值。

# 反例

- ✗ veto 命中卻只報 `condition` 不附 `evidence` 之檔案路徑+行號。**應改為**：`{ condition: "DSL_BINDING_TRACE", evidence: "specs/orders/feature.feature:42 — Examples 欄位 'priority' 無 DSL binding 對應" }`。
- ✗ Q1 給 1.0 但發現 rule body 有改一字——Q1 必須是「byte-for-byte」評，任一字差即 < 0.7（甚至直接 VETO `NO_RULE_WORDING_CHANGE`）。
- ✗ `verdict = PASS` 但 `vetoes[]` 非空——任一 veto 必為 `VETO`，邏輯互斥。
- ✗ fix_hints 寫「rule 寫得不夠清楚」——不可執行；應寫「rule_anchor `<...>` 在 `${FEATURE_SPECS_DIR}/orders.feature:10` 中描述含『可能』，hedging 不明，請回 `/aibdd-discovery` 重新表述」。
- ✓ `verdict = VETO`，`vetoes` 列 2 筆具體 evidence，dim scores 仍計算，fix_hints 給 3 個可執行下一步。

# 禁止自生

- **不得**在本 skill 自己定義 veto／dimension（譬如加 Q5 `developer ergonomics`）——SSOT 在 `../references/contracts/quality.md`，本檔只執行；新增 veto／dim 走 references 修改。
- **不得**把 SOFT_FAIL 強升為 PASS 來通過 gate——SOFT_FAIL 必須在 quality 報告誠實標記，由 caller decide 是否續跑下游。
- **不得**省略 evidence 之檔案路徑+行號——evidence 必須 actionable。
- 違反處置：quality 報告本身視為不可信；重跑 step 7。
