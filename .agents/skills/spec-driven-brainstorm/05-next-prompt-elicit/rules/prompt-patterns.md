# Prompt Patterns 規則

每輪 phase 5 emit 之 prompt **必須**從下表中選擇對應 pattern（依 `$classify_summary.action × $target_subsection` 與 ambiguity 狀況）；**禁止**自由發揮、**禁止**含 hedging 詞、**禁止**重述已寫入 spec 的內容。

## §1 chat-text 模式 patterns

| (action, target_subsection 落點) | Prompt pattern（語意；文字可微調） |
|---|---|
| `create-issue` → `definition` | 「我已開啟 issue #N「<title>」並起了 Definition；它想達成的事，目前寫成 1 條 fact — 你還有別的目的要加進去嗎？」 |
| `append-fact` → `definition` | 「Definition 已加上這條 fact。Definition 還要繼續補嗎？」 |
| `append-fact` → `problem-space` | 「Problem Space 已加上 P<n>。關於 Problem Space 還有什麼要繼續聊的嗎？」 |
| `append-fact` → `brainstorming` | 「S<n> 已加進 Brainstorming。要再展開更多方案，還是就這幾個方向決定？」 |
| `append-fact` → `solution` / `examples` / `implementation` / `implementation-package-structure` | 「已加進 `<subsection name>`。這條 subsection 還要補嗎？」 |
| `advance-subsection` → `problem-space` | 「我們離開 Definition，進入 Problem Space — 你想先說目前不夠好的點是什麼？或我來提幾條觀察讓你修？」 |
| `advance-subsection` → `brainstorming` | 「Problem Space 收尾，進入 Brainstorming — 我先依 Problem Space 排幾個候選方案 S1 / S2 / S3 給你看，AI 推薦排序 S1 最符合需求，由你決定走哪條。」 |
| `advance-subsection` → `solution` | 「方案落地為 Solution — 要不要看 Examples？」 |
| `advance-subsection` → `examples` | 「Examples 已寫；要進到 Implementation 嗎？」 |
| `advance-subsection` → `implementation` | 「Implementation 已寫；要進到 Implementation Package Structure 嗎？」 |
| `advance-subsection` → `implementation-package-structure` | 「Implementation Package Structure 已寫；本 issue 進度收尾。要回頭 revise 或開新 issue？」 |
| `commit-variant` → `solution` | 「已採納 S<n> 為 Solution、brainstorming 已 archive。要看 Examples 嗎？」 |
| `revise` | 「已依你說的改寫 `<target>`；級聯 sweep 順便更新了 `<cascade_targets>`。還有要再 revise 的點嗎？」 |
| `defer` (pivot-section) | 「跳回 `<target_issue>` × `<target_subsection>` — 你想動哪部分？」 |
| `defer` (meta-question) | 直接回答 user 的查詢；結尾不主動推進對話。 |

## §2 ask-user-question 模式 patterns

`$elicit_mode = ask-user-question` 時，**必須**用 host 之 `AskUserQuestion`（或等效）一次性提出所有待澄清題目；**禁止**多輪逐題往返。

| 觸發情境 | Question 組裝模板 |
|---|---|
| `ambiguous` due to multi-intent（如 user 同時 commit 又 add fact）| 1 題：「你想先 <intent 1> 還是 <intent 2>？」選項列出兩個 intent 各一個。 |
| `ambiguous` due to `pivot violates progressive disclosure` | 1 題：「目前 active 在 `<current_subsection>`，你想跳到的 `<requested_subsection>` 尚未開啟。要：(a) 留在 `<current>` 完成、(b) 跳階直接開 `<requested>`、(c) revise `<current>` 為已完成。」 |
| `ambiguous` due to `target_issue unresolvable` | 1 題：「我找不到對應的 issue。現有 issue 是 `<list of titles>`，你指的是哪一個？」選項列出既有 issue + 「開新 issue」選項。 |
| `advance-subsection` → `brainstorming`，AI 已提案 S1 / S2 / S3 | 1 題：「Brainstorming 三個方向：S1 `<name>`（推薦）／S2 `<name>`／S3 `<name>`，你想 commit 哪一個？」選項對應 S1 / S2 / S3 + 「想再多展開」。 |

## §3 Prompt 寫作紀律

- 每個 prompt **必為**單一具體問句或敘述句；**禁止**塞入 hedging 詞、**禁止**含「你覺得呢？」「希望你能 …？」之模糊措辭、**禁止**重述已寫入 spec 的內容。
- chat-text 模式之 prompt **必須**附 1 行本輪 spec 變更摘要於問句前（譬如 "已寫入 issue 1 × Problem Space P3"）。
- ask-user-question 模式選項數**必為** 2–4；**禁止**單選項假提問、**禁止**塞 5+ 選項（user UX 過載）。
- Archive 行為**必須**主動於 chat-text 結尾提及（譬如「已 archive 至 ...」），讓 user 知道 brainstorming 不會永久遺失。

## Good

- Action = `append-fact` → `problem-space`，phase 4 無 archive：
  > 已寫入 issue 1 × Problem Space P3（part 必須錨定於 Contract 或 Data）。
  >
  > 關於 Problem Space 還有什麼要繼續聊的嗎？
- Action = `commit-variant` → `solution`，phase 4 archive 了 brainstorming：
  > 已採納 S2（套件級 plugin）為 Solution；brainstorming 完整 archive 至 `${ARCHIVE_DIR}/issue-1-brainstorm-20260520T103412Z.md`。
  >
  > 要看 Examples 嗎？
- Action = `ambiguous`（multi-intent），phase 5 走 ask-user-question：
  - Question 1：「你想先 commit S2，還是先補 P4？」選項：(a) 先 commit S2、(b) 先補 P4、(c) 兩者都做（請說順序）。

## Bad

- AI emit「我覺得 Problem Space 可能還有些細節，你覺得呢？我建議你想想看 …」— 含 hedging（「可能」「建議」「想想看」）+ 模糊問句，違反 §3「禁止 hedging」。
- AI emit 「Problem Space 完成了嗎？」附帶把整個 P1 / P2 / P3 內容貼一次出來 — 違反 §3「禁止重述已寫入 spec 的內容」。
- AI 走 ask-user-question 一次只給 1 個假選項（「要 commit 嗎？」選項只有「是」）— 違反 §3「禁止單選項假提問」；應改為 chat-text 模式或補充其他選項。
- AI commit-variant 後 emit chat-text 但沒提 archive — 違反 §3「Archive 行為必須主動提及」；user 不知道 brainstorming 去哪了。
- AI 跑 ambiguous 路徑時用 chat-text「你剛剛說的我不太懂，可以再說一次嗎？」— 違反 ambiguous 必走 ask-user-question batch 提問；應用 AskUserQuestion 給出 2–4 個選項讓 user 點選釐清方向。
