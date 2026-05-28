# Payload Schema（Core）

Planner → clarify-loop 的批次疑問契約：**本檔只定義所有 route 共用的欄位與全域 invariant。**

完整契約必須再加上選定 route 的專章：

- SpecFormula-Fork：[`../sub-skill/SpecFormula-Fork/references/payload-schema.md`](../sub-skill/SpecFormula-Fork/references/payload-schema.md)
- AskUserQuestion：[`../sub-skill/AskUserQuestion/references/payload-schema.md`](../sub-skill/AskUserQuestion/references/payload-schema.md)

---

## Core Schema

```yaml
questions:
  - id: Q1
    kind: GAP | ASM | BDY | CON
    context: <單句技術語上下文>
    question: <單句技術語提問>
    options:                        # 2 ≤ len ≤ 4
      - id: <option-id>
        label: <選項技術名>
        impact: <單句結構影響>
    recommendation: <option id>
    recommendation_rationale: <單句>
    priority_score: <int>
    dependencies: [<Qid>, ...]      # 可選
```

路由專屬欄位（例如錨點、`OTHER` 選項）**一律**只定義在對應 sub-skill 的 `references/payload-schema.md`。

---

## Core Required Fields

每題至少必填：

`id, kind, context, question, options, recommendation, recommendation_rationale, priority_score`

全域限制：

- `2 <= len(options) <= 4`
- `recommendation` 必須指向既有 option id
- 若有 `dependencies`，不得形成循環

缺項或違反上述全域規則時，clarify-loop 回傳：

```yaml
status: incomplete
missing:
  - "<field or invariant>"
```

---

## Dependency Ordering

若 `Q_i.dependencies = [Q_j]`，caller 應保證 `Q_j` 不晚於 `Q_i`。router 會再做排序，但若發現循環依賴，回傳：

```yaml
status: invalid_dependencies
cycle_or_missing:
  - "<cycle path>"
```
