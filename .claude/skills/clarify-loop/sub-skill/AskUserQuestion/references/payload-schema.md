# Payload Schema — AskUserQuestion Route

本檔只描述 **route=`ask-user-question`**（`AskUserQuestion` / `AskQuestion` 類工具）所需欄位與選項規則。

先讀共通契約：[`../../../references/payload-schema.md`](../../../references/payload-schema.md)。

---

## Route-specific Required Fields

每題在 core 必填欄位之外**另外**必填：

- `location`：便條紙或可回溯定位鍵，慣例為 `file:line` 或可穩定對應 sweep 的字串

---

## Route-specific Options

- 允許在 `options` 內加入 **`OTHER` + `free_text: true`**（仍計入每題最多 4 個選項的上限）
- `OTHER` 若存在，排版與解析細節見同目錄 [`ask-user-question-usage.md`](ask-user-question-usage.md)

---

## Incomplete Response（此 route）

若 runtime 已選定 `ask-user-question`，但 payload 不符合本檔：

```yaml
status: incomplete
route: ask-user-question
missing:
  - "<field or invariant>"
```

---

## Example（ask-route）

```yaml
questions:
  - id: Q2
    kind: BDY
    context: 訂單建立時機會影響 state machine
    question: 訂單何時建立？
    options:
      - id: A
        label: 送出即建
        impact: 有明確生命週期起點
      - id: B
        label: callback 成功才建
        impact: 避免殘留待付款單
      - id: OTHER
        label: 其他（自行填寫）
        impact: N/A
        free_text: true
    recommendation: A
    recommendation_rationale: 送出即建讓下游狀態機較單純
    priority_score: 12
    location: activities/結帳.mmd:53
```
