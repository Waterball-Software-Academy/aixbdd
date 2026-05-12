# R13 — Mock-Arming Completeness（Phase 5 invariant）

> 純 declarative reference。Phase 5 Subagent semantic validation 用此規則檢驗。
>
> 來源：原 SKILL.md `## Step 4 — R13`。

## §1 規則本體

對 testability-plan.md §3 中每個 op 的 `decision_delegate != none`，其 response 內非確定性欄位（verdict / score / classification / verifyResult.* 等）若被任何 Scenario 的 `Then` step assert，則同 Scenario 的 Background 或前置 Given step 必須引用對應的 mock-setup 類 DSL entry（L2 = `mock-setup` 且 L4 `ref:` 指向 §7.5 中對應的 `internal-decision-*` anchor）來 arm 該決策。

## §2 範例

「Then MCP 回傳 verdict 應為 "pass"」前必須有引用 mock-setup DSL 的 Given。

## §3 違反處理

違反 → `R13_MISSING_MOCK_ARMING`（hard-fail）；指示使用者回 Phase 4 補 Given，並在缺對應 DSL entry 時回 `/speckit.aibdd.bdd-analyze` 補 mock-setup entry。
