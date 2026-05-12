---
description: 接收 planner 的批次疑問 payload，先做共通 schema 檢查與白話文轉譯，再依可用工具分流。優先走 fork；若無 fork，改走 AskUserQuestion／AskQuestion 類互動工具。任何 planner 要向使用者提問都必須 DELEGATE 此 skill，不得自行逐題提問。
metadata:
  source: project-level dogfooding
  user-invocable: true
name: clarify-loop
---

# clarify-loop

外層 `SKILL.md` 只負責 intake + routing，不承載 route-specific SOP。互動細節全部在 `sub-skill/`。

## §1 SOP (Router Only)

### Phase 1 — INTAKE payload

1. READ payload from caller.
2. VALIDATE payload against [`references/payload-schema.md`](references/payload-schema.md) 的共通核心欄位。
3. IF 缺欄，RETURN `{status: "incomplete", missing: [...]}`。
4. ASSERT 每題 options 在 2..4 範圍內。

### Phase 2 — NORMALIZE questions

1. SORT questions per [`references/question-priority.md`](references/question-priority.md)。
2. TRANSLATE `context/question/options/recommendation_rationale` per [`references/simplified-wording.md`](references/simplified-wording.md)。
3. 產出 `translated_questions`（僅資料準備，不派發工具）。

### Phase 3 — DETECT tooling + ROUTE + route payload validate

1. DETECT runtime tool capabilities（由系統工具清單判斷）。
2. ROUTE 規則（固定優先序）：
   2.1 IF 可用工具包含 `fork`：route=`specformula-fork`。  
   2.2 ELSE IF 可用工具包含 `AskUserQuestion` 或 `AskQuestion`（或等價 ask-question tool）：route=`ask-user-question`。  
   2.3 ELSE：RETURN `{status: "unsupported_tooling", required: ["fork", "AskUserQuestion|AskQuestion"]}`。
3. IF route=`specformula-fork`，VALIDATE normalized payload against [`sub-skill/SpecFormula-Fork/references/payload-schema.md`](sub-skill/SpecFormula-Fork/references/payload-schema.md)；IF 不符，RETURN `{status: "incomplete", route: "specformula-fork", missing: [...]}`，不自動降級。
4. IF route=`ask-user-question`，VALIDATE normalized payload against [`sub-skill/AskUserQuestion/references/payload-schema.md`](sub-skill/AskUserQuestion/references/payload-schema.md)；IF 不符，RETURN `{status: "incomplete", route: "ask-user-question", missing: [...]}`。

### Phase 4 — DELEGATE to sub-skill

1. IF route=`specformula-fork`，DELEGATE [`sub-skill/SpecFormula-Fork/SKILL.md`](sub-skill/SpecFormula-Fork/SKILL.md) with normalized payload。
2. IF route=`ask-user-question`，DELEGATE [`sub-skill/AskUserQuestion/SKILL.md`](sub-skill/AskUserQuestion/SKILL.md) with normalized payload。
3. 透傳子技能回傳結果給 caller。

## §2 FAILURE CONTRACT

- `incomplete`: payload 欄位不齊或 route-specific 契約不成立。
- `unsupported_tooling`: 環境缺少可用互動工具。
- `route_failed`: 子技能執行失敗，附上 `route` 與 `reason`。

## §3 CROSS-REFERENCES

- 不限定 caller。description（line 3）已涵蓋「任何 planner 要向使用者提問都必須 DELEGATE 此 skill」；分流規則由 §1 Phase 3.2 的 runtime capability detection 一錘定音，與 caller 身分無關。
- 外層 router 不處理 sync/async resolve；該邏輯由 `sub-skill/AskUserQuestion/SKILL.md` 承擔。
