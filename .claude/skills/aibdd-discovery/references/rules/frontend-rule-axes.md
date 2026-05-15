# Frontend Rule Axes

> 跨 RP 共用的 frontend 軸定義。本檔由 `reasoning/discovery/04b-frontend-axes.md` 引用，作為 UI verb catalog、anchor 命名、state 軸的單一權威。`reasoning/discovery/05-atomic-rules.md` 在 `frontend_lens` 非空時亦消費本檔 §UI Verb Catalog 與 §Anchor Naming Rules 做 ASSERT。
>
> **本檔不負責**：component / frame composition / 視覺 token（皆屬 `aibdd-uiux-design`）；本檔只負責讓 atomic rule 在出生時就帶 UI 詞性與 anchor 鉤子。

---

## §1 啟動條件（Boundary Role Gate）

| Boundary role | 04b 行為 | atomic-rules 消費 |
|---|---|---|
| `frontend` | 啟動完整推導 | 必填 `ui_verb` + `anchor_hint` |
| `backend` / `worker` / `library` / 其他 | short-circuit；`frontend_lens = null` | 跳過 frontend 條款 |
| 未填或非 enum | 進入 Seam C clarify-loop 補 boundary role | 同上 |

> Boundary role 取自 `source_material_bundle.target_boundary.role`。`/aibdd-kickoff` 寫入 `.aibdd/arguments.yml` 後可被 `kickoff_path_resolve.py` 展開。

---

## §2 UI Verb Catalog

每條 atomic rule 的動作動詞在 frontend boundary 下必須能對應到本表 `ui_verb` 欄位之一。catalog 不允許每專案臨時擴充；如需擴充，必須在本檔 PR 上做。

| category | ui_verb | 對應典型 activity 動詞（lemma） | 預設 ARIA role | interactivity |
|---|---|---|---|---|
| input | `click` | 點擊 / 按 / 按下 / tap / press | button | interactive |
| input | `type` | 輸入 / 填 / 填寫 / 打字 / enter text | textbox | interactive |
| input | `select` | 選 / 選擇 / 挑 / 勾選 / 取消勾選 | combobox / listbox / checkbox / radio | interactive |
| input | `focus` | 聚焦 / 移到 / tab 到 | (依底層 role) | interactive |
| input | `submit` | 送出 / 提交 / 確認送出 | button (type=submit) / form | interactive |
| input | `upload` | 上傳 / 附加檔案 | button / input(type=file) | interactive |
| state-change | `enable` | 啟用 / 開啟 | (依底層 role) | interactive |
| state-change | `disable` | 停用 / 鎖定 / 禁用 | (依底層 role) | interactive |
| state-change | `expand` | 展開 / 攤開 | button(aria-expanded) / disclosure | interactive |
| state-change | `collapse` | 收合 / 摺疊 | 同上 | interactive |
| state-change | `toggle` | 切換 / 開關 | switch / button(aria-pressed) | interactive |
| feedback | `announce` | 通知 / 告知 / 唸出（a11y live region）| status / alert | informational |
| feedback | `toast` | 跳訊息 / 顯示提示條 / snackbar | status / alert | informational |
| feedback | `scroll-into-view` | 滾到 / 滑到 / 帶到視野 | (依底層 role) | informational |
| feedback | `focus-trap` | 鎖焦點 / 鎖視線 / 限定 tab 範圍 | dialog | interactive |
| visual | `render` | 顯示 / 出現 / 露出 / 看到 | (依底層 role) | informational |
| visual | `hide` | 隱藏 / 收起 / 不顯示 | (依底層 role) | informational |
| visual | `skeleton` | 顯示骨架 / 顯示載入占位 | status (aria-busy) | informational |
| visual | `spinner` | 顯示載入轉圈 / loading 圖示 | status (aria-busy) | informational |
| visual | `empty-state` | 顯示空狀態 / 顯示尚無資料 | status | informational |
| visual | `error-visual` | 顯示錯誤訊息 / 顯示錯誤橫幅 | alert | informational |
| navigation | `navigate` | 前往 / 切換到 / 跳到（route 變更）| link | interactive |
| navigation | `open-dialog` | 開啟視窗 / 開彈窗 / 開 modal | dialog (opens) | interactive |
| navigation | `close-dialog` | 關閉視窗 / 關 modal / 關抽屜 | button (closes dialog) | interactive |

### §2.1 不允許的動詞（明示黑名單）

下列動詞為 backend / domain command，若在 frontend boundary 的 atomic rule 出現 → Pattern 4 Frontend Lens 命中：

`POST` / `GET` / `PUT` / `DELETE` / `persist` / `save to database` / `query database` / `return 200` / `return 4xx` / `commit transaction` / `lock row` / `publish event` / `enqueue` / `dispatch` / `process job`

> 即使是「驅動 backend command 的 UI 行為」（例如 submit 後送 API），rule 仍須用 UI verb（`submit` / `click`）描述，**不得**寫成「POST /refund」。後端動作屬另一 boundary，由其 atomic rule 各自描述。

---

## §3 UI Verb → ARIA Role Mapping

`AnchorCandidate.role` 取值規則：依 `ui_verb` 與其 activity action object 的搭配對到下列 role。`generic` / `div` / `span` **禁出現**。

| ui_verb | 預設 role | 例外 role（依 object 判定） |
|---|---|---|
| click | button | link（若 object 是「連結 / 連到 / 帶到外部頁」）；tab（若 object 是分頁切換）；menuitem（若 object 在 menu 內） |
| type | textbox | searchbox（object 含「搜尋 / 找 / 查詢」）；spinbutton（object 是數字 stepper）|
| select | combobox | listbox / checkbox / radio（依 UI 形式；activity 若已標記則沿用）|
| submit | button | form（若 rule subject 是 form 整體）|
| navigate | link | — |
| open-dialog | button | — |
| close-dialog | button | — |
| toggle | switch | button(aria-pressed=...)（兩態 toggle 用 switch 較好）|
| expand / collapse | button(aria-expanded) | — |
| announce / toast | status | alert（若是嚴重錯誤或必須打斷使用者）|
| render | (取自 object 自身 role) | heading（標題類）；listitem（清單列）；img（圖像）|
| skeleton / spinner / error-visual / empty-state | status | alert（error 嚴重時）|

---

## §4 Anchor Naming Rules

### §4.1 Accessible Name 取值（核心 invariant）

`AnchorCandidate.accessible_name` 必須是 **activity action 動詞片語的 verbatim quote**，不得同義改寫。

✅ 合法
- activity: 「使用者送出退款」→ accessible_name = `"送出退款"`
- activity: 「點擊取消按鈕」→ accessible_name = `"取消"`（object verbatim）
- activity: 「Submit refund」→ accessible_name = `"Submit refund"`

❌ 不合法（Pattern 4 命中）
- activity: 「送出退款」→ accessible_name = `"提交退款"`（同義改寫；submit 換 commit）
- activity: 「取消」→ accessible_name = `"放棄"`（同義改寫）
- activity: 「填寫 email」→ accessible_name = `"電子郵件輸入框"`（描述化，非動詞片語）

### §4.2 Lemma 一致性檢查

「verbatim」實作上允許以下正規化，**禁**語意改寫：
- 大小寫正規化（`Submit` ↔ `submit`）
- 全形 / 半形標點正規化
- 兩端空白裁切
- 中文「動詞 + 直接受詞」順序保留

不允許：
- 動詞替換（submit ↔ commit、送出 ↔ 提交、取消 ↔ 放棄）
- 名詞替換（退款 ↔ 退費、訂單 ↔ 訂購單）
- 補充修飾語（accessible_name 不得加 activity 沒寫的形容詞）
- 縮寫展開或縮寫化（OK ↔ 確認）

### §4.3 Anchor ID 等於 Action ID（絕對規則）

`anchor_id` **必須**等於對應的 `activity_action.action_id`，**不限**單 frame 或多 frame 情境。

- 單 frame 情境：anchor_id = action_id。此規約讓 `05-atomic-rules.md` §3 step 2 的 `LOOKUP anchor_id == $rule.action_id` 為**確定性 join**，不會因命名漂移靜默失敗。
- 多 frame 情境：同一 activity action 在多個 frame 出現時，anchor_id **仍唯一**（共用同一個 action_id）；不得跨 frame 為同一 anchor 命名多個。

違反此規約 → Pattern 4 §4.2「Anchor 自生」命中，因為 lookup 落空時 05 會誤判為自生 anchor。

### §4.4 黑名單 role

下列 role 不得做為 AnchorCandidate.role：
- `generic`
- `div` / `span`（不是 ARIA role，是 HTML element）
- `presentation` / `none`（純裝飾 element，不應出現在 atomic rule 動作對象上）

如果只是純裝飾 element（與 acceptance 無關），不應在 atomic rule 出現，本檔不為其命名 anchor。

---

## §5 State Axes

> **SSOT note（重要）**：本節 §5.1 / §5.2 推導出的 `state_axes_hint` 為 **hint only**，作用是讓 04b 產出的 atomic rule 攜帶初步 state 線索給 atomic-rules 階段使用。**State matrix 的 SSOT 在 `aibdd-uiux-design/references/state-derivation-rules.md §A2`**；下游 uiux-discovery 不消費本檔的 state_axes_hint，會獨立從 `.feature Rule + .activity DECISION` 重推 component state matrix。
>
> 本檔 §5.1 / §5.2 規則應與 `state-derivation-rules.md §A2` 保持語義一致；若兩者衝突，**以 state-derivation-rules.md 為準**，並開 PR 修正本檔。`state_axes_hint` 與 uiux-discovery 推導結果不一致時不視為失敗——它只是 atomic rule 撰寫時的提示。

### §5.1 Base State（互動本質）

依 ARIA role interactive 預設集：

| role | base states |
|---|---|
| button / link / tab / menuitem | idle, hover, focus, active, disabled |
| textbox / searchbox / spinbutton / combobox | idle, focus, disabled, readonly, invalid |
| checkbox / radio / switch | idle, focus, checked, unchecked, disabled |
| listbox / menu / dialog | idle, open, closed |
| status / alert（informational）| (none — 不互動) |

### §5.2 Domain State（資料 / 流程驅動）

從 activity DECISION 分支 + impact_scope.impacts 抽：
- `loading` — 等待 backend 回應或 long task 進行中
- `empty` — 資料集為空且 acceptance 要求顯示空狀態
- `error` — 錯誤分支命中
- `populated` — 一般成功路徑、有資料
- `pristine` — form 初始未編輯狀態（區別於 idle）

### §5.3 不負責的軸（交給 `aibdd-uiux-design`）

下列軸**不**屬本檔範疇；04b 不為 anchor 推這些屬性：
- viewport（mobile / tablet / desktop）
- visual token（color / typography / spacing）
- motion / animation duration
- component composition（哪個 component 含哪個 anchor）

如果 atomic rule 確實需要 viewport 維度（例如「mobile 下 menu 改為抽屜」），04b 標記為 `FrontendLensCiC{type=BDY}` 並推到 uiux-discovery 處理。

---

## §6 對應 fixture 案例（建議補充）

待 Storybook BDD fixture 落地後在此補；目前先以 catalog + invariant 為準。
