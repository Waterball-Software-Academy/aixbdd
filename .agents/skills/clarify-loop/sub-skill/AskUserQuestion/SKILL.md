# clarify-loop sub-skill: AskUserQuestion

此文件只定義 ask-question 路徑。外層 router 已完成 payload intake / 排序 / 白話文重寫，這裡承接互動、回收答案、resolve 與 sweep。

## Tool preference in this route

1. 優先使用 `AskUserQuestion`。
2. 若環境沒有 `AskUserQuestion`，可用 `AskQuestion`（或等價 ask-question tool）承接同一批問題。
3. 若 ask-question 工具不可用，回傳：

```yaml
status: unsupported_tooling
route: ask-user-question
required:
  - AskUserQuestion
  - AskQuestion
```

## Inputs

- `normalized_payload.questions[]`
- route-specific 欄位：
  - `location`（ask route 使用 `file:line` 或可回溯定位字串）
  - 可選 `OTHER` / `free_text: true`（若 caller 提供）

## References

- [`references/payload-schema.md`](references/payload-schema.md)：AskUserQuestion route 專屬 payload 契約
- [`references/ask-user-question-usage.md`](references/ask-user-question-usage.md)
- [`references/round-lifecycle.md`](references/round-lifecycle.md)
- [`references/async-subagent-protocol.md`](references/async-subagent-protocol.md)
- [`references/config-schema.md`](references/config-schema.md)
- `scripts/grep_sticky_notes.py`

## SOP

### Phase A — Batch ask

1. 依 [`references/ask-user-question-usage.md`](references/ask-user-question-usage.md) 做 Sub-round batching。
2. 每個 tool call 最多 4 題；首次 Sub-round 追加 `update_mode` 題。
3. [USER INTERACTION] 觸發 ask-question tool，等待使用者回覆。

### Phase B — Parse + log

1. 解析答案並還原 option id（含 `OTHER` free-text 情況）。
2. 依 [`references/round-lifecycle.md`](references/round-lifecycle.md) append Sub-round log。
3. EMIT `partial_result{round_id, sub_round_id, answered, pending, update_mode}`。

### Phase C — Resolve

1. `update_mode == sync`：
   - 直接計算 mini-plan、套用更新、回傳 inline diff。
2. `update_mode == async`：
   - 依 [`references/async-subagent-protocol.md`](references/async-subagent-protocol.md) 委派 subagents。
   - 收斂並回傳進度事件與結果。

### Phase D — Sweep + close

1. 執行 `scripts/grep_sticky_notes.py` 掃描便條紙變化。
2. 發送 Round Closer。
3. 全部題目完成後 RETURN：

```yaml
status: completed
route: ask-user-question
rounds: <R>
sticky_notes_remaining: <K>
files_changed: [...]
```
