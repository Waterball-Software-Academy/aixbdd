# Progressive Disclosure Order 規則

- subsection 推進**必須**遵守固定順序：`definition` → `problem-space` → `brainstorming` → `solution` → `examples` → `implementation` → `implementation-package-structure`。
- 候選 subsection 並非每個都得寫進每個 issue；**缺席合法**，但**禁止**逆序新增（譬如先寫 Implementation 再回頭補 Definition）。
- 推進**僅當** user 透過 `confirm-section-done` intent 或 AI 推得「當前 subsection 已飽和」時觸發；**禁止**AI 主動為 user 跳階補 subsection。

## §1 跳階規則

- 中間 subsection 可以**跳過**（譬如 issue 純為小型 cleanup，可直接 definition → solution，跳過 problem-space / brainstorming）；跳階只允許「前向跳過」，**禁止**「跳過後又回填」。
- 一旦進入 `solution`，**禁止**回頭新增 `brainstorming`（brainstorming 已是拋棄式）；若 user 想重啟方案討論，須走 `revise-prior-decision` 整段重寫 `## Solution`。

## §2 終態 subsection

- `implementation-package-structure` 為終態；user 對該 subsection 後續訊息**僅能** revise 或 pivot，不再有 `advance-subsection`。
- 終態之後 user 仍可開新 issue（`new-issue` intent）。

## Good

- 序列：`definition` 確認 → `problem-space` 確認 → `brainstorming` AI 提案、user 選 S2 → `solution` 落地 + `brainstorming` archive → `examples` AI 提案 → user 確認 → `implementation` → `implementation-package-structure` 終態。
- 序列（合法跳過）：`definition` 確認 → 跳過 `problem-space` 與 `brainstorming` 與 `solution` → 直接 `implementation`（適用於純 cleanup-type issue，無 design decision 可言）。
- User 在 `solution` 階段表示「不對，重來」→ 走 `revise-prior-decision` 整段替換 `## Solution`；**不開新 `## Brainstorming`**。

## Bad

- AI 在 user 還沒 confirm `## Problem Space` 完成時，自行先寫 `## Brainstorming` 預載候選方案 — 違反「一次只推進一個 subsection」。
- User 在 `solution` 落地後說「想再多看幾個方案」，AI 重新插入 `## Brainstorming` heading — 違反「進入 solution 後禁止回頭新增 brainstorming」；應走 revise 整段重寫 `## Solution`。
- AI 跳過 `definition` 直接寫 `## Problem Space`（issue 開頭就直奔問題定義）— 違反「definition 必為起點」，至少要有 1 句 definition 描述 issue 想達成什麼。
- AI 在 `## Examples` 已 commit 後回頭補 `## Brainstorming`（逆序新增）— 違反「禁止逆序」。
- AI 為 user 「先把所有 subsection 都建空 heading 等填」一次 commit — 違反「禁止跳階補 subsection」。
