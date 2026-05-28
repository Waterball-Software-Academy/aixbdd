# clarify-loop sub-skill: SpecFormula-Fork

此文件只定義 `specformula-fork` 路徑。外層 router 已完成 payload intake / 排序 / 白話文重寫，這裡只做 SpecFormula `fork` 工具專屬驗證與派發。

## Inputs

- `normalized_payload.questions[]`
- 每題包含外層共通欄位，且具備 SpecFormula-Fork route 必要 anchor：
  - `located_file_type`
  - `located_file_path`
  - `location`（必須是 `readGraph` verbatim id）

## References

- [`references/payload-schema.md`](references/payload-schema.md)：SpecFormula-Fork route 專屬 payload 契約
- [`references/fork-question-format.md`](references/fork-question-format.md)：`fork.question` 四要素模板與 invariant

## Route-specific invariants

1. 每題 `options` 數量必須在 2..4。
2. 禁止 `OTHER` / `free_text: true`。
3. `location` 不可使用 legacy 格式（例如 `STEP:1`、`Scenario: ...`、`file:line`）。
4. `recommendation` 必須對應現有 option id。

任一條件不成立，回傳：

```yaml
status: incomplete
route: specformula-fork
missing:
  - "<具體欄位或違規原因>"
```

## Dispatch SOP

1. LOOP 每題 `q`：
   1.1 依 [`references/fork-question-format.md`](references/fork-question-format.md) 組出 `fork_question`（四要素模板）。
   1.2 TRIGGER `fork` with:
       - `question: fork_question`
       - `located_file_type: q.located_file_type`
       - `located_file_path: q.located_file_path`
       - `location: q.location`
2. 計數 `dispatched_count`，ASSERT `dispatched_count == questions.length`。
3. RETURN：

```yaml
status: fired
route: specformula-fork
count: <dispatched_count>
summary: "已以 SpecFormula fork 工具批次派發 N 題澄清問題"
```

## Message rendering guidance

- 問句維持對話語氣，避免純技術術語。
- 選項使用離散錨點（A/B/C/D），保留使用者在 thread 補充自然語言的空間。
- 推薦句必須寫出「為何此決策影響下游」。
