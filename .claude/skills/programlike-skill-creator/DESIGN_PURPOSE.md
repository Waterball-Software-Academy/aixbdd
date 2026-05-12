# DESIGN_PURPOSE — 為什麼這支 skill 該存在，以及它真正要證明的事

> **Status**: v0 — 由使用者於 2026-04-29 口述；本文是把那段口述往前推、寫得比口述更銳利的版本。
> **不是**: SOP / 規章 / API spec — 這些已經在 SKILL.md / spec.md。
> **是**: 設計這支 skill 與其產出的所有 skill 時，背後一以貫之的世界觀（worldview）。任何規章修改、verb 增刪、validator 規則調整，都要過得了這份文件的檢驗。

---

## §1 表面任務 vs 深層任務

### 1.1 表面任務
把使用者一句模糊的「我想做一個 X skill」轉成一份 規章-compliant 的 `SKILL.md` + references/ + scripts/ 骨架。

### 1.2 深層任務
強制執行一個**關於 skill 本質的特定理論**：

> **一支 skill 是一個 program，其中絕大多數 line 是 deterministic 的搬運工 —— 讀檔、寫檔、控制流、schema 驗證、path 計算、結構化 I/O —— 只有少數幾條 line 是真正需要 LLM 一行一行去做的 semantic reasoning。**

現行的 AIBDD 規章（program-counter 紀律）做到了 **「程式的形」**：phase 編號、verb 前綴、`#phase.step` 字面 GOTO、references lazy-load。但還沒做到 **「程式的質」** —— **「哪些 line 是 reasoning，哪些只是 mechanics」這件事，源碼本身看不出來**。

---

## §2 現行規章為何不夠

把 D（Deterministic）與 S（Semantic）混在同一種 `1. <VERB> <args>` 語法裡，代價是：

1. **無法機械化盤點「這整個 phase 其實只是檔案搬運，應該抽成一支 Python script」** —— 必須仰賴人工 review。
2. **無法量化一支 skill 的「semantic density」** —— 每支 skill 到底有多少比例真的非 LLM 不可？沒人知道。
3. **skill 無法朝它的精瘦形態演化** —— 我們希望 skill 隨時間變成 *thin reasoning layer over thick deterministic substrate*；但沒有 type 信號，每次重構都靠憑感覺。
4. **無法防止退化** —— 某次 PR 把一個 D-block 改回 prose-form，validator 抓不出來，skill 又胖一圈。
5. **token 成本與 latency 是隱形的浪費** —— D-steps 跑成 LLM turn 與跑成 script 在 token 帳單上差兩個數量級；現在我們沒有把這條成本曲線畫出來給作者看。

---

## §3 我們在賭的假設

對於一支「成熟的 skill」：

| Step 類別 | 比例（假設） | 性質 |
|---|---|---|
| **Deterministic (D)** | 70–90% | `cp` / `regex match` / `JSON parse` / `mkdir` / schema validate / path compute 的偽裝 —— 任何等價 Python script 都能跑出同樣結果 |
| **Semantic (S)** | 5–25% | 需要 LLM 讀 fuzzy 輸入、classify、生 prose、或做 regex 做不到的判斷 |
| **Interactive (I)** | <5% | `[USER INTERACTION]` 已涵蓋 —— yield turn 等 user |

若這個假設成立，那麼 skill 的「正確形狀」就是：

```
thin S-kernel  →  TRIGGER thick D-scripts  →  return to S-kernel
```

而不是現在這種「一切都是 1.x.y 步驟，全靠 LLM 一行行解讀執行」的均質結構。

---

## §4 規章該被升級成的樣貌

我們要讓 規章本身、以及所有由本 skill 產出的 skill，**在源碼層級就把 D/S/I 類型講清楚**：

1. **Type every step at source-code level**
   - 每個 step 強制標 `[D]` / `[S]` / `[I]` 前綴（`[I]` 即現有 `[USER INTERACTION]` 的別名 / 等價）
   - **不是註解、不是慣例 —— 是 validator 強制的 syntactic prefix**

2. **Group contiguous D-steps as `[SCRIPT-CANDIDATE]` blocks**
   - 連續 ≥3 個 `[D]` step 自動形成一個 candidate block
   - 用一行 marker 標出：「這段未來可以整段抽成 `scripts/<lang>/<name>.<ext>`」
   - 「能不能變成 script」從一場 refactor 考古，降為 **一眼可見的問題**

3. **Verb whitelist 加 `kind` 欄位**
   - 每個 verb 標 default mode：`D` / `S` / `Mixed`
   - 大多 verb 的 default mode 就對了；只有 `Mixed` 類 verb 強制每次 step 顯式標 `[D]` 或 `[S]`

4. **Validator 增加「semantic-density report」**
   - 每跑一次 validate，輸出：
     ```
     S-density: 18% (4/22 steps)
     D-blocks ≥3 steps: 3 candidates
       Phase 3 #2..#7  (6 steps)  → suggest extract scripts/python/scaffold_dirs.py
       Phase 5 #1..#3  (3 steps)  → suggest extract scripts/python/populate_refs.py
       Phase 6 #1.1.1..#1.1.3 (3 steps) → suggest extract scripts/python/stub_scripts.py
     ```
   - **低 S-density** = 抽 script 收益高的 skill
   - **高 S-density** = 該再拆 sub-skill 的 skill

5. **D 與 S 不得混在同一個 step**
   - 「one verb, one step」的進階版：「one verb, one **cognitive type**」
   - 違反者：validator 會建議「拆成兩個 step：先 [S] DERIVE 值，再 [D] WRITE 檔」

---

## §5 長期演化方向

每一輪 dogfooding 都應該讓某支 skill 的 D-count 下降、`scripts/` 目錄變厚。一支 skill 不再「進步」的判準，**不是 SKILL.md 變多長**，而是：

> **LLM 只在做「只有 LLM 能做的事」，其他 step 都已經 compile 成一支 script 呼叫**。

理想終局，一支 skill 的 SOP body 看起來像：

```markdown
### Phase 2 — CLASSIFY & SCAFFOLD

1. [D] TRIGGER scripts/python/ingest.py → outputs.json
2. [S] THINK per references/classifier.md → assign category
3. [D] TRIGGER scripts/python/emit_report.py outputs.json category
```

—— 三行，其中兩行 shell-equivalent，唯一一行 irreducibly LLM。

---

## §6 為什麼這件事不只是美學

| 維度 | 不分 D/S 的代價 | 分了之後的收益 |
|---|---|---|
| **成本 / latency** | D-step 跑成 LLM turn = 跟 S-step 同價 | D-step 抽 script 後 = 毫秒級 + 零 token |
| **決定論** | D-block 在不同 model version 可能 silent drift | 抽成 script 後永遠 byte-identical |
| **測試覆蓋** | 「imperative step with verb whitelist」只能跑整個 skill 才測得到 | Python script 可用 pytest 直接 unit test |
| **演化可讀性** | 新增一條 step 時沒人問「這該不該是 script」 | type annotation 強迫作者每次都回答這題 |
| **skill 的「身材」** | 看 SKILL.md 行數沒有 signal | S-density % 是直接的健康指標 |

---

## §7 不是這份設計的目標（避免誤讀）

1. **不是要把 LLM 從 skill 裡踢出去** —— S-kernel 是整支 skill 存在的理由。
2. **不是要禁止 prose / 語言彈性** —— prose 仍然在 S-step 的 body 內自由流動。
3. **不是要強迫立刻把所有 D-block 抽成 script** —— annotation 是 *measurement*，不是 *action*。抽不抽，看 audit 結果與 ROI 再決定。
4. **不是要把 skill 變成 makefile** —— D/S 區分是為了讓 reasoning 更聚焦，而不是把 skill 簡化成 build pipeline。

---

## §8 一條檢驗每次規章修改的快速問題

> *這次的修改，會讓「哪些 line 是 reasoning，哪些只是 mechanics」更明顯，還是更模糊？*

更明顯 → 通過。
更模糊 → 退回去重想。

—— 這是本 skill 所有後續演化的北極星。
