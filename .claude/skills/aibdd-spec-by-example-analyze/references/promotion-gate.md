# DSL Promotion Gate 規則

> 純 declarative reference。Phase 6 LOAD 取 promotion 判定規則。
>
> 來源：原 SKILL.md `## Step 6 — DSL Promotion Gate`。

## §1 目的

掃描**跨 package** 的 boundary `dsl.yml` entry 使用頻率 + 結合 AI 基建判定（infrastructure utility heuristic）。

若某 entry 達門檻且新版 `dsl.yml` promotion scanner 可用 → **產出**（不自動 apply）一份 `${CURRENT_PLAN_PACKAGE}/promotion-proposal.md` 供人工 review 後以 `/speckit.aibdd.promote-dsl` 指令執行真實晉升。

> 目前若既有 scanner 只支援舊 `dsl.md` flat layout，本 phase 必須 no-op，並在 REPORT 中說明「promotion gate 尚未支援 boundary package dsl.yml」。禁止為了 promotion gate 寫回舊路徑。

## §2 6a — Cross-package reuseability scan（Script）

```bash
bash .claude/skills/aibdd-core/scripts/bash/promote-gate-scan.sh \
  --specs-root ${SPECS_ROOT_DIR} \
  --dsl-glob "${TRUTH_BOUNDARY_PACKAGES_DIR}/*/dsl.yml" \
  --threshold ${PROMOTION_REUSEABILITY_THRESHOLD:-20}
```

## §3 6b — Infrastructure utility judgement（AI）

對每個 candidate，AI 依 L2 DSL Semantics 判斷是否屬於「專案基礎建設」。

Gate 觸發條件 = **AND**：

- candidate 的跨 package 出現次數 ≥ `${PROMOTION_REUSEABILITY_THRESHOLD}`
- AI 判定為 infrastructure utility = true

## §4 6c — Emit proposal

 Gate 觸發 → 寫 `${CURRENT_PLAN_PACKAGE}/promotion-proposal.md`。Gate 未觸發或 scanner 不支援 `dsl.yml` → no-op。

## §5 6d — 結束行為

- **本 skill 在此 Step 6 結束；不呼叫** `/speckit.aibdd.promote-dsl`
- REPORT 要告知使用者：若 proposal 存在，下一步建議跑 `/speckit.aibdd.promote-dsl`
