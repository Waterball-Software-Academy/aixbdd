---
name: clarify
description: 當需求存在缺漏、矛盾、模糊或尚未拍板的決策時，先整理可理解的上下文、精煉問題與可比較的選項，直接訪談使用者，避免 AI 以腦補方式補完需求。可作為其他 skills 的下游 skill，由呼叫者指定優先提問面向與是否詳記問答紀錄。 Use when the user invokes /clarify, asks the AI to interview for missing requirements, or when another skill needs to resolve incomplete, ambiguous, or conflicting requirements before proceeding.
disable-model-invocation: true
---

# Clarify

當需求仍有細節不足、定義模糊或多種合理解讀時，先補足決策所需的上下文，再用好懂且可比較的選項向使用者提問，讓使用者拍板，而不是由 AI 自行補完。

# SOP

## Phase 1 -- 收斂本輪訪談缺口

1. READ 讀取使用者需求、呼叫者 skill 指示、當前上下文與既有產物，確認本次要澄清的主題、決策邊界、指定提問面向，以及是否需要詳記問答紀錄。
2. THINK 先讀取 `rules/盤點高影響需求缺口與提問排序判準.md`，再依其要求盤點需求中的缺漏、矛盾、模糊與未拍板決策，優先收斂影響範圍最大的 1 至 3 題作為本輪提問，並確保整個 clarify session 累計不超過 5 題。

## Phase 2 -- 產出本輪 clarify 問題

1. WRITE 先讀取 `rules/Context與選項題撰寫判準.md`、`templates/clarify-question-round.md` 與 `templates/clarify-question-round.example.md`，再依骨架與範例直接在對話中輸出本輪問題：每題都要先提供足以協助使用者判斷的 `Context`，再提出一句清楚的 `總結之提問`，最後用 Markdown 表格列出單選或多選 `Options`、標示一個推薦選項與推薦原因，並固定提供 `Others` 讓使用者補充；不得使用 Ask Tool。
2. WRITE 明確請使用者依題號回答選項編號，必要時在 `Others` 補充說明；未收到回答前停止，不自行假設答案。

## Phase 3 -- 依回答決定續問、收斂或記錄

1. READ 讀取使用者對本輪問題的回答，整理已拍板決策、仍未解決缺口與新浮現的限制，判斷是否已足以讓呼叫者 skill 繼續。
2. WRITE 若呼叫者 skill 要求詳記問答紀錄，先讀取 `templates/clarify-log.md` 與 `templates/clarify-log.example.md`，再依骨架更新本次 clarify session 的問答紀錄。
3. THINK 若仍有高影響缺口且累計題數尚未達 5 題，回到 Phase 1 準備下一輪提問；若資訊已足夠，則輸出已確認決策、使用者補充與剩餘風險，交還呼叫者 skill 繼續後續流程。
