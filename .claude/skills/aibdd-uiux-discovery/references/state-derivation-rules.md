# State Derivation Rules — 從 discovery 機械推導 component state matrix + frame composition

> 純 declarative 規則表。SKILL.md Phase 2 LOAD 本檔做兩段推導：
> **§A 元件層**：抽 component → per-component state matrix（component × state）
> **§B 組合層**：frame → 用到哪些 component + 一份 canonical 狀態組合（單一 frame 不展開狀態）
>
> ⚠️ 與舊版（v1 frame-level state matrix）的關鍵差異：
> 狀態爆炸的維度從 `frame × state` 改為 `component × state`；frame 只負責「組合 + canonical state combo」，
> 這對齊下游 `*.stories.tsx` 的 CSF3 Story export（component args 變體 = Story）。
> 不再產出 frame-level state matrix；如果某 component 跨 frame 重用，其狀態定義在 component 層共用，frame 只指向。

---

## §A — Component Inventory + Component State Matrix

### §A1 Component candidate extraction（從 atomic-rules 動詞抽元件）

從 `.feature` Rule 條款抽 imperative verb + object → component candidate。

| Rule 條款範例 | Component candidate | role |
|---|---|---|
| 「使用者送出報名表」 | `SubmitApplicationButton` | button |
| 「房主開始遊戲」 | `StartGameButton` | button |
| 「玩家提交猜測」 | `SubmitGuessButton` | button |
| 「使用者輸入房間名稱」 | `RoomNameInput` | textbox |
| 「顯示玩家列表」 | `PlayerList` | list |
| 「顯示倒數計時」 | `Countdown` | status |

命名規約：
- `PascalCase` + 動詞為主（按鈕 / 動作型）或名詞為主（顯示 / 容器型）
- role 取自 ARIA roles（button / link / heading / textbox / list / listitem / status / dialog / form / region / progressbar / radiogroup / tab / tabpanel）
- 同 role + 同領域語意動詞 → **必須抽成同一 component**（跨 frame 共用）

### §A2 Component state matrix derivation（per-component 狀態清單）

對每個 component candidate，從兩個來源蒐集狀態：

**來源 1：互動本質（隨 role 而異）**

| role | 必有的 base states |
|---|---|
| button | `idle`、`hover`、`focus`、`active`、`disabled` |
| textbox | `empty`、`focus`、`filled`、`disabled`、`invalid` |
| list | `populated`、`empty`、`loading`、`error` |
| dialog | `open`、`closing` |
| form | `pristine`、`dirty`、`submitting`、`success`、`rejected` |
| status | `idle`、`updating`、`stale` |

**來源 2：.activity DECISION × .feature Rule 補狀態**

| Guard / Rule 句型 | 補入 component state |
|---|---|
| `is_valid == true` / `success` | `success`（form / button-cluster） |
| `validation_failed` / 「不可 X」/「需先 Y」 | `rejected` + 訊息槽位 |
| `business_rule_violated` / 「重複」/「上限」 | `rejected.<rule_id>` |
| `not_found` / 「X 不存在」 | `error.not_found` |
| `unauthorized` / 「無權限」 | `error.unauthorized` |
| `network_error` / 「系統錯誤」 | `error.system` |
| `list.length == 0` / 「不可為空」 | `empty` |
| `expired` / 「逾期」 | `rejected.expired` |
| `loading` / 「等待結果」 | `loading` |

兩條輔助規則：
1. 每個 component 至少要列 1 個 success-path state（idle / populated / pristine 視 role 而定）
2. unmatched guard → 標 `unclassified` flag 給 clarify-loop §3 補語意；禁止 silent default

### §A3 State code 命名規約

snake_case，分層：

- `idle` / `hover` / `focus` / `active` / `disabled` — 互動 base state
- `success` — 主路徑成功
- `error.<reason>` — `error.network` / `error.not_found` / `error.unauthorized` / `error.system`
- `empty` 或 `empty.<context>` — `empty.no_rooms` / `empty.no_guesses`
- `rejected.<rule_id>` — `rejected.duplicate_name` / `rejected.over_limit` / `rejected.expired`
- `loading` / `submitting` — 進行中

### §A4 Output schema — `$$component_inventory`

```yaml
component_inventory:
  - id: SubmitApplicationButton
    role: button
    base_states: [idle, hover, focus, active, disabled]
    domain_states:
      - code: submitting
        source: "F-001.R1 (waiting for server)"
      - code: rejected.duplicate_name
        source: "F-001.R2"
      - code: error.system
        source: "activity.SubmitApplication DECISION system_error branch"
    anchor_role: button
    anchor_source_rule_id: F-001.R1
    used_by_frames: ["application-form", "application-review"]
    notes: ""
  - id: PlayerList
    role: list
    base_states: [populated, empty, loading, error]
    domain_states:
      - code: empty.no_players
        source: "F-002.R3"
    anchor_role: list
    anchor_source_rule_id: F-002.R2
    used_by_frames: ["lobby"]
    notes: ""
```

---

## §B — Frame Composition Map

### §B1 Frame extraction（從 .activity action node 抽 frame）

- **frame slug 命名**：`{verb}-{noun}` kebab-case（取自 activity action node 名稱）
- 例：`create-room` / `submit-guess` / `review-result`
- 一個 frame 可橫跨多個 activity action node，但建議 1:1 對齊

### §B2 Frame → component usage

每個 frame 在組合層只記錄：
1. **使用哪些 component**（指向 `$$component_inventory[*].id`）
2. **layout 提示**（stack / grid / sidebar+main / split — clarify §6 補細節）
3. **canonical state combo**：選一組 component state 作為「主畫面」展示（**不**展開全 state matrix；其它 state 透過 component-level 展示）

每個 frame 必須能對應**至少一條** `.feature` Rule（無對應 → 視為 design over-reach，Phase 2 ASSERT 失敗）。

### §B3 Output schema — `$$frame_composition`

```yaml
frame_composition:
  - frame_slug: create-room
    activity_node: ["CreateRoom", "ValidateRoomCode"]
    activity_file: "lobby.activity"
    feature_rules: ["F-001.R1", "F-001.R2"]
    feature_file: "F-001-room-creation.feature"
    layout_hint: "single-column form"
    uses_components:
      - component_id: RoomNameInput
        canonical_state: pristine
      - component_id: SubmitRoomButton
        canonical_state: idle
      - component_id: ErrorBanner
        canonical_state: hidden          # 即「該 frame 預設不顯示」的 component slot
    purpose: "讓房主輸入名稱並建立房間"
```

> `canonical_state` 限制：**只能取自 `$$component_inventory[<id>].base_states ∪ .domain_states[*].code` ∪ `hidden`**；
> 不允許自創新狀態碼。

---

## §C — Reasoning invariants（不變式宣告，非流程）

對 Phase 2 reasoning 結果的不變式（具體執行步驟在 SKILL.md §2 SOP Phase 2）：

- 每個 unmatched guard 或 unclassifiable rule 必須標 `unclassified`；禁止 silent default
- `$$component_inventory` 與 `$$frame_composition` 共享同一個 component id 命名空間；任一 frame 引用的 component id 必須在 inventory 中存在
- 每個 component 至少有 1 個 success-path state
- 每個 frame 對應 ≥ 1 條 .feature Rule
- 任一 frame 的 `uses_components` 為空 → ASSERT 失敗
- 任一 frame 的 `canonical_state` 不在對應 component 的 state set 內 → ASSERT 失敗
- 不再產 frame-level state matrix；舊版 placeholder `$$state_matrix` 已廢除
