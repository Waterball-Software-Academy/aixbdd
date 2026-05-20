# User Intent Enum 分類規則

- AI **必須**將 user 本輪訊息收斂至下列 8 個 intent 之一；**不得**留多義並列或自創新 enum。
- 多義訊息 **必須**歸類為 `ambiguous`，由 phase 5 一次性 batch 提問澄清；**禁止**在 phase 2 內 inline 多次反問 user。
- Intent 與 action **必為**一對一映射，逐字對齊下表，不得自造別名：

| intent | action | 典型訊號 |
|---|---|---|
| `new-issue` | `create-issue` | 「來聊另一個」「新議題」「順便討論 X」「再開一個」明顯換主題 |
| `add-fact-to-current` | `append-fact` | 補充細節、補上 fact、追加考量、給範例、貼一段資訊 |
| `confirm-section-done` | `advance-subsection` | 「沒了」「就這樣」「ok 下一步」「繼續」「dive into next」「進入下一個」 |
| `pick-variant` | `commit-variant` | 「我選 S2」「走第二個」「就 X 方向」「I accept」「採用 X」 |
| `revise-prior-decision` | `revise` | 「等等改一下」「剛剛那個其實不對」「重講」「retract」「修正 P1」 |
| `pivot-section` | `defer` | 「先回頭看 Definition」「跳去 implementation」「換回 issue 1」 |
| `meta-question` | `defer` | 「目前 spec 長怎樣」「進度到哪了」「我們聊到哪」 純查詢無更新 |
| `ambiguous` | `ambiguous` | 上列皆不適用、或多 intent 並列、或語意過簡（「嗯」「ok」單獨出現） |

- `defer` 動作於 phase 3 **不寫檔**；phase 4 仍走 consistency 掃描（被動 no-op）；phase 5 emit prompt 推進對話。
- `ambiguous` 動作於 phase 3 / 4 皆 no-op；phase 5 **必須** emit 一次性 batch 提問。

## Good

- User 訊息「我覺得 P3 寫得不夠精準，應該強調 part 一定屬於 contract」→ `$intent = revise-prior-decision`、`$action = revise`（明確要修正 P3 已寫內容）。
- User 訊息「我選 S2，因為它能讓 preset 自帶 spec parser」→ `$intent = pick-variant`、`$action = commit-variant`（明確 commit S2）；S1/S3 之外的方案於 phase 4 強制 archive。
- User 訊息「來看下一個議題：dsl.yml 的檔名怎麼定」→ `$intent = new-issue`、`$action = create-issue`（明確換主題，當前議題隱含完成）；`$target_issue = ${issues_count} + 1`。
- User 訊息「先回 issue 1 補一條 P4」→ `$intent = pivot-section`、`$action = defer`；`$target_issue = 1`、`$target_subsection = problem-space`。
- User 訊息「我選 S2，順便補一條 P4」→ `$intent = ambiguous`、`$action = ambiguous`（多 intent 並列 — 同時要 commit-variant 與 add-fact-to-current）；phase 5 emit batch 提問請 user 確認動作順序。
- User 訊息「嗯」→ `$intent = ambiguous`、`$action = ambiguous`（語意過簡，無法斷定該怎麼推進）。

## Bad

- AI 把「等等，這條 P3 怪怪的，我想想」歸類為 `add-fact-to-current` 並追加新事實 — user 明顯是想 revise 而非 append，誤判導致 spec 內出現新舊矛盾敘述並存。
- AI 把「順便聊聊 dsl.yml 檔名」歸類為 `add-fact-to-current` 並寫進當前 issue — 實為 `new-issue`，誤判導致兩個獨立議題被 conflate 在同一 H1 block。
- AI 把「我選 S2」歸類為 `confirm-section-done` 並直接推進到 Examples — 漏掉 `commit-variant` 必經的「archive brainstorming + 寫 Solution」流程，spec 仍殘留 S1/S3 variants。
- AI 對含糊訊息（譬如 user 只說「嗯」「好喔」）直接 default 為 `add-fact-to-current` — 該歸 `ambiguous` 並 emit 批次提問，不得猜 user 意圖。
- AI 把「我選 S2，順便補一條 P4」拆成兩 intent 連跑兩次 phase 3 / 4 — 違反「一次只推進一個 subsection」原則；應歸 `ambiguous` 由 user 確認順序。
- AI 自創 enum `partial-confirm` 或 `maybe-pick` 描述邊緣 case — 違反封閉 enum，這類訊息應歸 `ambiguous`。
