# Announce Format — Phase 3 AssistMessage 進度回報

> Defines the markdown format for the per-iter progress report sent to the user via `AssistMessage`. Pure declarative.

---

## §基本格式

```markdown
## 🎯 Goal · {phase}
- **檔案**：`{file_path}`
- **Feature**：{title}
- **接下來會執行**：
  1. {step 1}
  2. {step 2}
  ...
```

### 欄位來源

| 欄位 | 來自 |
|---|---|
| `{phase}` | `$$current_goal.phase`（`RED` / `GREEN` / `REFACTOR`） |
| `{file_path}` | `$$current_goal.file_path` |
| `{title}` | parse 自 `$$current_goal` 的 prompt text，通常是 `Feature:` 行；fallback 為 file basename |
| `{step N}` | `$$plan` 的核心 step（Phase 4 in-head reasoning 結果），3-5 條為宜 |

---

## §⚠️ 紅字提醒

**Phase 3 EMIT 完此訊息後 worker 立刻往下走 Phase 4，不等 user reply、不 sleep、不執行 ScheduleWakeup**。

此訊息純粹是 **單向進度通報**，user 是被動觀眾。違反此原則（例如改成 AskUserQuestion 形式）會破壞 SKILL.md §2 SOP 的 Global INVARIANT「Automated mode」。

---

## §可選擴充

若 phase 為 `RED`，可額外標註：
```markdown
> 💡 RED phase — 預計寫失敗測試以驅動下一步實作
```

若 `$$last_verdict` 含修正指示（前一輪 verdict 是 `failed` 或 `needs_revision`），在「接下來會執行」前加：

```markdown
- **Evaluator 修正指示**：{verdict instructions 摘要}
```

讓 user 看得到 worker 為什麼這輪要做什麼。

---

## §禁止事項

- ❌ 不要把整個 `$$current_goal` 的 prompt text 原樣貼上（太長、雜訊多）
- ❌ 不要包含「請問」「要不要」「確認嗎」字樣
- ❌ 不要列出待選方案讓 user 挑（自動模式自行決定）
- ❌ 不要在訊息結尾加「等待回覆」這類引導語
