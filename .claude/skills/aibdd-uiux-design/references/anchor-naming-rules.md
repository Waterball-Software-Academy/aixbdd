# Anchor Naming Rules — accessible name 命名規則（component-keyed）

> 純 declarative 規則表。SKILL.md Phase 2（component inventory derive）與 Phase 3（clarify）LOAD 本檔。
>
> 目的：讓 Pencil 文字節點的 accessible name 與 atomic-rules 動詞、Story `args`、step locator 同源；
> 設計、合約、測試三層合一。
>
> ⚠️ 與舊版（v1 frame-keyed）的差異：
> anchor 從 `(frame_slug, role)` 改為 `(component_id, role)`。
> 同 component 跨 frame 重用時共用同一個 anchor name（不再每 frame 列一次）。

---

## §1 候選來源（從 atomic-rules 抽動詞 → 對應到 component）

從 `.feature` Rule 條款抽動詞短語（imperative verb + object），對應到 [`state-derivation-rules.md`](state-derivation-rules.md) §A1 抽出的 `component_inventory` 條目，產生 anchor name 候選。

| Rule 條款範例 | Component id | role | anchor candidates |
|---|---|---|---|
| 「使用者送出報名表」 | `SubmitApplicationButton` | button | `送出報名`、`送出報名表` |
| 「房主開始遊戲」 | `StartGameButton` | button | `開始遊戲` |
| 「玩家提交猜測」 | `SubmitGuessButton` | button | `提交猜測`、`送出猜測` |
| 「使用者建立房間」 | `CreateRoomButton` | button | `建立房間`、`開房` |
| 「使用者取消預約」 | `CancelReservationButton` | button | `取消預約` |

每個候選 anchor 必含：

```yaml
anchor:
  component_id: CreateRoomButton
  role: button                  # 與 component.role 一致
  name_candidates: ["建立房間", "開房", "新增房間"]
  source_rule_id: F-001.R1
  notes: ""                     # 額外說明（消岐 / variant 提示）
```

---

## §2 命名強制條款（clarify-loop §5 user 鎖定後仍要遵守）

1. **動詞鎖定**：accessible name 必須包含 atomic-rules 的關鍵動詞**之一**，禁同義改寫
   - 例：Rule 寫「送出」，name 不可改成「提交」；要嘛擇一鎖定，要嘛 source rule 改寫
2. **唯一性（component 層）**：同一 `component_id` 只能對應一個鎖定後的 name
3. **跨 component 衝突**：兩個不同 `component_id` 不可同 `role` + 同 `name`
   - 若領域語意確需，用括號消岐：`送出 (報名表)` / `送出 (請假單)`
   - 或考慮合併為同一 component（透過 clarify-loop §3 確認）
4. **長度**：≤ 20 chars（i18n 友善；CJK 6-10 字、英文 ≤ 20 chars）
5. **大小寫**：英文 anchor 用 Title Case（`Submit Application`），中文不加空格

---

## §3 Forbidden anchor

以下類型**禁止**成為 accessible name；必須附 visually-hidden text / `aria-label`：

- 純圖示無文字（icon-only button）
- 純色塊狀按鈕（無 label）
- 純情境通用詞：「按這裡」/「點我」/「More」/「Click」/「OK」/「Cancel」（除非情境完全無歧義且 Rule 確實如此寫）
- 純 emoji（如 `🚀`）

---

## §4 Output schema（Phase 2 step 5 產出）

```yaml
anchor_candidates:
  - component_id: CreateRoomButton
    role: button
    name_candidates: ["建立房間", "開房", "新增房間"]
    source_rule_id: F-001.R1
    notes: ""
  - component_id: SetPasswordInput
    role: textbox
    name_candidates: ["設定密碼"]
    source_rule_id: F-002.R1
    notes: "label 必須出現在 input 旁"
  - component_id: SubmitGuessButton
    role: button
    name_candidates: ["送出猜測", "提交猜測"]
    source_rule_id: F-003.R1
    notes: "與 SubmitApplicationButton 'submit' 同字根，需消岐"
```

Phase 3 clarify-loop §5 Copy Decisions 會讓 user 從每個 anchor 的 `name_candidates` 擇一鎖定，產出 `$$clarify_resolved.copy_decisions`：

```yaml
copy_decisions:
  - component_id: CreateRoomButton
    role: button
    name: "建立房間"
    source_rule_id: F-001.R1
```

---

## §5 與下游合約的對應

最終鎖定的 anchor name 會：

1. **進 Pencil 文字節點**：設計師畫 component scene 時的 button label 必須一字不差（**且該 component 跨 frame 重用時不可改寫**）
2. **進 Storybook `args`**：`/aibdd-form-story-spec` 翻譯 `<ComponentId>.stories.tsx` 時 `args.children` 或 `args.label` 直接取 name
3. **進 step locator**：`getByRole(role, { name: <accessible name> })`

任一環節改寫 → 測試合約斷裂；本 skill 在 Phase 5 ACCEPTANCE CRITERIA 強制 prompt 內 ANCHOR NAME TABLE 必非空，下游 form-story 再做一次驗證。

---

## §6 跨 frame 重用的處理（component-keyed 帶來的核心好處）

當 component 出現在多個 frame：

- ✅ anchor name **共用**一條 ANCHOR NAME TABLE 列；不在每個 frame 重複列
- ✅ component state matrix **共用**；frame 只在 composition table 指定 canonical_state
- ✅ Storybook 對應**單一** `<ComponentId>.stories.tsx`，每個 state 一個 Story export
- ❌ 不允許跨 frame 改文案（例如同一個「送出」按鈕在 A frame 叫「送出」B frame 叫「提交」）— 這代表它們其實是兩個不同 component，應分裂

frame composition table（[`state-derivation-rules.md`](state-derivation-rules.md) §B3）內每筆 `uses_components` 都帶 `component_id`，與本檔 `$$anchor_candidates[*].component_id` 直接 join。
