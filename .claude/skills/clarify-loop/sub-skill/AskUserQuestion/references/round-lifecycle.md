# Round Lifecycle

Round Opener、Question 與 Sub-question、Consistency Sweep、Round Closer、紀錄格式。

---

## Round Opener

Step 3 呼叫 AskUserQuestion 前，主 agent 先 inline 呈現：

```
--- Round <R> 開始（共 <M> 張待解便條紙，本回合處理 <N> 張）---
```

緊接著呼叫 AskUserQuestion（N 題 + 1 題 update_mode）。Opener 不單獨彈卡片，作為 AskUserQuestion 的前導敘述。

---

## Question vs Sub-question

| 類型 | 計入 `MAX_QUESTIONS_PER_ROUND` | 定義 |
|------|------------------------------|------|
| Question | ✓ | 為了推進一個新的追蹤地圖項目（便條紙）而提出 |
| Sub-question | ✗ | 仍在解決同一個追蹤地圖項目的延伸互動 |

### Sub-question 情境

- AskUserQuestion 回傳含 OTHER（free-text）→ 追問該題的自由文字
- 使用者回答模糊 → 追問釐清
- subagent 失敗 → 追問 retry / skip / manual
- 使用者糾正 clarify-loop 的處置 → 修正循環

**判定原則**：仍在解決同一便條紙 → Sub-question。切換至新便條紙 → 下一 Question。

---

## Sub-round Lifecycle

Round 內若因 AskUserQuestion 工具硬限（每 call ≤ 4 題）拆批，每批為一個 Sub-round。每個 Sub-round 完成（Step 4 解析回傳）時**立即**執行以下 hooks，不得延後至 Round Closer：

### 1. Append Log（crash-safe）

不論 `update_mode=sync | async`，將本 Sub-round 的 Q&A 即時 append 至 session 檔：

```markdown
## Round <R>

update_mode: <sync|async>

### Sub-round <R>.1
- Q1 (BDY @...): ... → <answer>
- Q2 (GAP @...): ... → <answer>
- Q3 ...
- Q4 ...

### Sub-round <R>.2
- Q5 ...
```

Compaction / crash 後可從 session 檔恢復已完成進度；未 log 的 Sub-round 視為未完成，需重問。

### 2. Emit partial_result

向呼叫方（Planner）回傳：

```yaml
partial_result:
  round_id: <R>
  sub_round_id: <S>
  update_mode: sync | async
  answered:
    - question_id: Q1
      answer: <label | {choice, text}>
    - ...
  pending:
    - question_id: Q5
    - ...
```

Planner 依 `update_mode` 決定是否增量 sync artifact：

- **sync** → 每收到 partial_result 即對 `answered` 題對應 artifact 做更新
- **async** → 累積至 Round Closer 再一次性 sync

### 3. 非阻斷

Sub-round 間不等待 Planner 確認；clarify-loop 立即進入下一 Sub-round（Step 3）。Planner sync 由 `update_mode` 語義保證，不佔 clarify-loop 時間軸。

### 與 Round Closer 的關係

Round Closer（Step 6）只做**彙整 + Consistency Sweep**，不重複 append log（已於每個 Sub-round 完成）。Closer 呈現的「已解決 N 張便條紙」數字為所有 Sub-round 累積。

---

## Consistency Sweep

Step 6 執行：

### 1. 掃描

```bash
python .claude/skills/clarify-loop/sub-skill/AskUserQuestion/scripts/grep_sticky_notes.py ${SPECS_ROOT_DIR}
```

### 掃描器約定

- 預設掃描 `${SPECS_ROOT_DIR}/{activities,features}/`，比對 `*.activity *.mmd *.feature *.md`
- Pattern：`CiC(KIND): <text>`，KIND ∈ `{ASM, GAP, BDY, CON}`
- 輸出 stdout JSON：`{ok, summary, violations[]}`；exit code 0/1 對應 `ok`
- 可選旗標：`--paths <subdirs...>`、`--globs <patterns...>`、`--kinds ASM GAP ...`
- `violations[]` 為剩餘便條紙清單 `{file, line, kind, msg}`

### 常見用法

| 場景 | 指令 |
|------|------|
| 全部掃描（預設） | `grep_sticky_notes.py ${SPECS_ROOT_DIR}` |
| 只看矛盾 | `grep_sticky_notes.py ${SPECS_ROOT_DIR} --kinds CON` |
| 只看 activities | `grep_sticky_notes.py ${SPECS_ROOT_DIR} --paths activities` |

### 2. 比對差異

Round 開始時記下便條紙清單 `before`，Sweep 後取 `after`：

- `before - after` = 已移除的便條紙（預期）
- `after - before` = 新增的便條紙（需通知使用者）

### 3. 自動移除過時便條紙

若某便條紙的底層疑問已因某題答案被解答，但 subagent / sync 更新未連帶清除：

- clarify-loop 自動移除
- inline 通知：
  ```
  Sweep: 移除 <N> 張過時便條紙（因 Q<ID>=<answer> 已涵蓋）
    - activities/結帳.mmd:<line> (BDY): <原便條紙訊息>
  ```

### 4. 重新計算優先序

剩餘便條紙若 `priority_score` 因定案變動 → 重新計算排序（影響下一 Round）。

---

## Round Closer

Step 6 最後呈現：

```
--- Round <R> 完成 ---

已解決 <A> 張便條紙（含 Sweep 自動移除 <B> 張）。
剩餘 <C> 張待解。
```

- `C > 0` 且有下一批 → 跳 Step 2
- `C == 0` → Step 7 Return
- Sub-round（因 AskUserQuestion 題數上限拆分）不計入 Round 編號

---

## 紀錄格式

Session 檔位於 `${CLARIFY_DIR}/<YYYY-MM-DD-HHMM>.md`，首次 Round 開始時建立，檔頭寫入呼叫方傳入的 idea 全文（逐字不改寫）：

```markdown
# Clarify Session <YYYY-MM-DD HH:MM>

## Idea

<使用者原始 idea 全文，逐字複製>

## Round 1

update_mode: sync

- Q1 (BDY @activities/結帳.mmd:19): 訪客觸發登入歸屬哪個資料夾 → B (features/checkout/)
- Q2 (BDY @activities/結帳.mmd:53): 訂單何時建 → A (送出即建)
- Q3 (OTHER): 付款逾時處理 → "希望 admin 收到 email 通知"
  subagent#3: -1 便條紙, 變更 1 檔

Sweep: 移除 1 張過時便條紙（因 Q1=B 已涵蓋）

## Round 2

...
```

async 模式下，subagent 完成時在對應題目下補記 diff summary。
