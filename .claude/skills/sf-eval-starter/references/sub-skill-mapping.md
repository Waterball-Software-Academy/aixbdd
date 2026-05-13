# Sub-skill Mapping — phase → DELEGATE target

> Defines which sub-skill to DELEGATE for each TDD phase. Pure declarative.
>
> 這三個 sub-skill 必須存在於 worker project 的 `.claude/skills/`（non-empty SKILL.md）。Claude Code 從 worker 的 CWD 自動載入 `.claude/skills/`，所以路徑 == worker project 根目錄相對 `.claude/skills/<name>/SKILL.md`。

---

## §phase mapping

| Goal phase | DELEGATE target | Sub-skill 位置 |
|---|---|---|
| `RED` | `/aibdd-red-execute` | `<worker project>/.claude/skills/aibdd-red-execute/SKILL.md` |
| `GREEN` | `/aibdd-green-execute` | `<worker project>/.claude/skills/aibdd-green-execute/SKILL.md` |
| `REFACTOR` | `/aibdd-refactor-execute` | `<worker project>/.claude/skills/aibdd-refactor-execute/SKILL.md` |

---

## §BOOT 自我檢測指令

SKILL.md Phase 1 step 4 (`MATCH 三個 sub-skill 皆存在`) 對應的具體檢測（從 worker CWD 跑）：

```bash
test -f .claude/skills/aibdd-red-execute/SKILL.md \
  && test -f .claude/skills/aibdd-green-execute/SKILL.md \
  && test -f .claude/skills/aibdd-refactor-execute/SKILL.md
```

任一失敗即視為 `$sub_skills_present == false`，BOOT 階段 STOP 並 EMIT 缺 sub-skill 錯誤訊息。

---

## §payload 傳遞契約

DELEGATE 時傳入：

| Key | 來源 | 用途 |
|---|---|---|
| `current_goal` | `$$current_goal`（SKILL.md Phase 2 產出） | sub-skill 從中取 `file_path` 與 `phase` |
| `plan` | `$$plan`（SKILL.md Phase 4 產出） | sub-skill 已知 worker 已做的 in-head 推理脈絡 |

Sub-skill 同步回傳：execution report 物件（含改動檔案清單、測試結果）或 error 物件（含失敗原因）。caller 收到回傳的當輪 turn 即繼續 Phase 6（組 test command）→ Phase 7（dispatch verify_goal）→ Phase 2（下一個 goal），不需要 user 介入、不需要 polling 等待。

→ Phase 6 PREPARE_TEST_COMMAND 不解析 sub-skill 的回傳物件 — 它只組裝可執行的 test command 字串送 verify_goal。**sub-skill 失敗不直接 STOP**：evaluator chat seat 跑 command 後看到測試 fail 即回 verdict=`failed`，由 verdict 決定下一步。

---

## §Phase 5 BRANCH unknown 路徑

若 `$$current_goal.phase` 不在 `RED` / `GREEN` / `REFACTOR` 三者之列（例如 evaluator 回傳新 phase 字面值），SKILL.md Phase 5 step 2 的 `*unknown*` 分支會 STOP 並 EMIT 錯誤。這是 fail-loud 設計，避免 worker 用錯 sub-skill 造成靜默劣化。
