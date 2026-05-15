# Userflow Rule Coverage Matrix

> 純 declarative — 規範 frontend Rule 對 has-ui operation 的 coverage 維度與必填項。**不含**任何步驟流程；步驟流程在 SKILL.md Phase 3。

---

## §1 Coverage 維度

對每個 has-ui operation，atomic rule 集合必須在下列 5 個維度有對應 Rule：

| 維度 | Rule 必填條件 | 對應 verification_mode | 缺失影響 |
|---|---|---|---|
| `happy` | 至少 1 條 — 操作主成功路徑 | 至少 1 條 `locator` + 至少 1 條 `visual-state` 或 `route` | 必填 — 缺則 gate fail |
| `error` | 至少 1 條 — BE 拒絕 / validation 失敗的 UI 反應 | `visual-state`（error-visual / toast） | 條件必填 — 對應 BE feature 有 error path 時必填 |
| `state-transition` | 至少 1 條 — UI 狀態變化（loading → loaded / disabled → enabled / collapsed → expanded） | `visual-state` 或 `locator` | 條件必填 — operation 涉及狀態變化時必填 |
| `a11y` | 至少 1 條 — 鍵盤可達性 / aria-live announce / focus management | `locator` 或 `visual-state` | 條件必填 — operation 涉及 dialog / async 反應時必填 |
| `cross-actor` | 至少 1 條 — 訪客 vs 登入使用者 vs 不同角色的合法性差異 | `locator` 或 `route` | 條件必填 — operation 有 actor permission gate 時必填 |

---

## §2 「必填條件」的判定來源

| 維度 | 觸發必填的訊號 |
|---|---|
| `happy` | 永遠必填 |
| `error` | BE `.feature` 有 `❌` / 失敗 Scenario；BE `.activity` DECISION 有失敗分支；OpenAPI 有 4xx / 5xx response |
| `state-transition` | BE operation 是 async / 長時 / 改變物件狀態（toggle / publish / archive） |
| `a11y` | operation 觸發 dialog / 跳轉 / 異步反饋；TLB.role 為 frontend 且 a11y 為產品宣告 baseline |
| `cross-actor` | OpenAPI security 有條件分支；BE `.feature` Background 含多角色 |

---

## §3 Coverage matrix 表達

每個 has-ui operation 在 `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` 的 `## Coverage Matrix` 章節以下表呈現：

| op_id | happy | error | state-transition | a11y | cross-actor |
|---|---|---|---|---|---|
| `submitRefund` | ✅ 2 rules | ✅ 1 rule | ✅ 1 rule | ✅ 1 rule | ➖ 不適用 |
| `listOrders` | ✅ 1 rule | ❌ MISSING | ➖ 不適用 | ➖ 不適用 | ✅ 1 rule |

### §3.1 標記語意

| 標記 | 涵義 |
|---|---|
| `✅ N rules` | 必填維度有 N 條 Rule 覆蓋（N ≥ 1） |
| `❌ MISSING` | 該維度依 §2 觸發必填但實際 0 條 — Phase 5 `F1_HAPPY_PATH` / `F2_EDGE_CASES` 等 gate 會 fail |
| `➖ 不適用` | 該維度依 §2 不觸發必填 — 不算缺失 |

---

## §4 跨 operation 的整體 coverage 統計

`reports/discovery-uiux-sourcing.md` 結尾必須給出整體統計：

| 統計項 | 含義 |
|---|---|
| `total_has_ui_ops` | has-ui operation 總數 |
| `total_no_ui_ops` | no-ui operation 總數 |
| `rules_total` | atomic rule 總條數 |
| `rules_by_verification_mode.locator` | verification_mode == locator 的 rule 數 |
| `rules_by_verification_mode.visual-state` | verification_mode == visual-state 的 rule 數 |
| `rules_by_verification_mode.route` | verification_mode == route 的 rule 數 |
| `rules_by_verification_mode.api-binding` | verification_mode == api-binding 的 rule 數 |
| `coverage_gap_ops` | 至少一個必填維度為 MISSING 的 operation 清單 |

---

## §5 Coverage 違規處置

| 違規 | rule_id（Phase 5 §5.B） | 處置 |
|---|---|---|
| `happy` 為 MISSING | `F1_HAPPY_PATH` | 必補；回 Phase 4 落檔重做 |
| `error` 為 MISSING 且 §2 觸發 | `F2_EDGE_CASES` | 補或以 explicit `CiC(BDY: ...)` 標出 boundary gap |
| `state-transition` 為 MISSING 且 §2 觸發 | `F4_STATE_TRANSITIONS` | 必補；回 Phase 4 |
| `a11y` 為 MISSING 且 §2 觸發 | （無對應 rule_id；歸 SOFT gap） | 在 sourcing report 標 GAP；不阻擋通關但下游 plan / draw 必須處理 |
| `cross-actor` 為 MISSING 且 §2 觸發 | `F3_ACTOR_RULES` | 必補；回 Phase 4 |
| has-ui operation 完全沒對應 feature | `UIUX_BE_OPERATION_COVERAGE` | HARD fail；回 Phase 4 |
| Rule 缺 `verification_mode` | `UIUX_VERIFICATION_MODE_PRESENT` | HARD fail；回 Phase 4 |

---

## §6 不在本檔範疇

- 「Rule 句型怎麼寫」 — 屬 [`verification-semantics-presets.md`](verification-semantics-presets.md)
- 「BE operation 怎麼判 has-ui / no-ui」 — 屬 [`be-to-fe-mapping.md`](be-to-fe-mapping.md)
- 「UI verb catalog」 — 屬 [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §2
- 「Atomic Rule 定義」 — 屬 [`aibdd-core::atomic-rule-definition.md`](aibdd-core::atomic-rule-definition.md)
