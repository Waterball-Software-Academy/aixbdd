# Async Subagent Protocol

Step 5 `update_mode: async` 的分支協定：subagent 派發、序列化、inline 回報、錯誤處理。

`update_mode` 在 Round 層級決定（使用者於 AskUserQuestion 選定），套用到本 Round 全部題目。

---

## 派發

收到 `update_mode: async` + N 題答案時：

1. **按題分組**：每題 1 個 subagent，承擔該題答案的變更落地
2. **傳入 subagent 的 context**：
   - 題目 payload（context / question / selected option / impact）
   - 該題對應 artifact 路徑（由 `location` 推算 + sweep 可能擴展）
   - 指令：依答案更新 artifact、移除對應便條紙、不得擅改無關內容
3. **派發方式**：`Agent(subagent_type="general-purpose", run_in_background=true)`，全部於同一訊息內送出以並行

---

## 序列化約束（避免同檔寫入衝突）

若多題影響同一檔案，對應 subagent 須**序列化**：

1. Step 5 派發前建立 artifact → subagent 映射表
2. 同檔案的 subagents 用 `addBlockedBy` 形成鏈（Q3 等 Q2 完成再啟）
3. 跨檔案的 subagents 仍並行

衝突偵測由 payload 的 `location` + 預期 sweep 範圍（推算）判定。若 planner 有更精確的 `affected_files` 欄位，優先採用。

---

## 回報格式

每個 subagent 完成時 inline 呈現一行：

```
[subagent#N 完成 · Q<ID>] <檔案清單> · <便條紙增減>
```

範例：
```
[subagent#2 完成 · Q2] activities/結帳.mmd, features/checkout/送出結帳.feature · -2 便條紙
```

**呈現時機**：
- 若主 agent 正在呈現其他內容（例如下一輪 Round Opener）→ 先輸出 subagent 回報，再繼續
- 若主 agent 閒置等候使用者 → 直接輸出

---

## 錯誤處理

subagent 回傳 `{status: "failed", reason: ...}` 或 timeout：

1. 暫停後續 subagent 派發（若還有 pending）
2. inline 呈現錯誤細節：
   ```
   [subagent#N 失敗 · Q<ID>] reason: <...>
   受影響檔案：<...>
   ```
3. 追問使用者（Sub-question）：
   - `(R) retry` — 重新派發同一 subagent
   - `(S) skip` — 標記此題未解決，進 Round Closer 時列為 pending
   - `(M) manual` — 暫停整個 Round，待使用者手動修正後繼續

---

## Round 結束條件

async 模式：
- Step 5 於派發完成後立即進 Step 6
- Step 6 Sweep 前**必須等所有 subagent 回報完畢**
- 若 Round Closer 時仍有 pending subagent → 顯示：
  ```
  等待 <N> 個 subagent 完成…
  ```
  全部完成後再呈現 Closer

---

## 紀錄

subagent 完成後，在 `${CLARIFY_DIR}/<session>.md` 的該題 entry 補記：

```markdown
- Q2 (BDY @activities/結帳.mmd:53): 訂單何時建 → A (送出即建)
  subagent#2: -2 便條紙, 變更 2 檔
  diff: +18 -7 @ activities/結帳.mmd, +3 -0 @ features/checkout/送出結帳.feature
```
