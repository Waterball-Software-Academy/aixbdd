# Activity Variation 拆解規則

本規則定義 `discovery.03-activity-analyze` 何時應對「同一 UAT goal 但具結構性差異」拆出多張 sibling Activity 檔，並建議三類 variation 的覆蓋（happy path + 兩極端），但不強制。

## 核心原則

每張 Activity 必須是 **user 可獨立 demo 的單一具體路徑**。

- 每張 Activity 必須 **self-contained**：從外部 actor 可觀察的 entry trigger 開始，經過必要的狀態轉移、分支、回圈與 handoff，直到可驗證的成功、失敗或終局結果；讀者不得需要跳到 sibling Activity 才知道這條路徑如何走完。
- Activity 不得退化成 **Feature index**：不可只把多個 feature 檔按時間排序串成 checklist，而沒有把 phase handoff、state transition、terminal verification 與 error ending 接進圖上。
- 每條 branch 都必須有明確去處：只能導向下一步、loop back、可觀察 terminal feature，或通往 `[FINAL]` 的 terminal step；不得只用註解表示「流程終止」「不屬本 variation」。
- 結構性差異（routing depth、approval layer、tier table、conditional routing chain）→ 拆為 sibling Activity 檔。
- 不得用單張 Activity 內的 DECISION 把 N 個 variation paths 並列展開（例如 T1 ~ T5 五條鏈塞同一張）。
- 單張內的 DECISION 只用於業務決策分支（例如「核准／駁回」「條件不符／合法」）。

## Self-Contained Definition

一張 Activity 視為 self-contained，必須同時滿足：

1. 有明確 **entry actor** 與 entry trigger。
2. 有完整 **actor-entry → verification / terminal arc**，而不是只截其中一段 phase。
3. 若上游 phase 的 postcondition 是下游 phase 的必要 precondition，且兩段共同構成同一個 UAT lifecycle，必須合併在同一張 Activity。
4. 每個 error / edge / success 分支都能落到明確 terminal，不得以 comment 補洞。
5. 結尾必須是可驗證結果：例如查詢結果、終局摘要、錯誤回應、完成畫面、可觀察狀態。

## Phase-Slice Merge Rule

當 raw idea 描述的是同一個 lifecycle 中前後相依的 phase slices（例如 lobby → prepare → start → battle，或 submit → review → finalize），若：

- phase A 的後置狀態是 phase B 的必要前置，
- phase B 不是獨立的 UAT lifecycle，而是同一次 demo / 驗收的一部分，
- 使用者期待驗收的是整段 journey 而不是單一 phase snapshot，

則 **不得**拆成多張 sibling Activity；必須合成一張 self-contained Activity。

只有在下列情況才允許拆開：

- 結構性 variation 軸不同（entry trigger / tier / routing depth / 顯著 exception path）。
- phase 本身就是獨立可驗收的 journey，且有自己的 actor-entry → verification arc。
- phase 之間不共享同一組關鍵 lifecycle 狀態。

## Variation Trigger

raw idea / impact scope 滿足任一條時，啟動 variation decomposition：

1. 出現 tier table / 金額分層 / 權限分層。
2. 出現 approval layer matrix（不同條件對應不同層數的審核鏈）。
3. 出現 loop / reroute / rejection-rework（被拒絕後修正重送）等需要回頭重跑的子段（任意業務領域：大額訂單審退-補資料、訂單退回-修正、優惠碼核銷失敗-改派 皆屬此類）。
4. 出現 conditional routing chain（不同 condition 觸發不同長度的後續處理）。

無 trigger（單 actor 線性流、無 routing 鏈、無 layer 差異）→ 只產生 1 張 Activity，不啟動 advisory。

## Variation Role

每個 `$uat_flow` 必須帶 `variation_role`，取以下之一：

- `happy_path`：中位／典型 demo 路徑（單一 tier，無駁回，足以走完業務驗收）。
- `extreme_min`：結構最簡（最少審核層／最短 routing 鏈／最少 actor 參與）。
- `extreme_max`：結構最繁（最多審核層／最長 routing 鏈／最多 actor 參與）。
- `additional`：上述三者以外的結構性 variation（例如 reroute loop、不同 operation trigger、不同前置條件）。

## 建議覆蓋（advisory，不強制）

當 trigger 啟動時，建議至少產出：

- 1× `happy_path`
- 1× `extreme_min`
- 1× `extreme_max`
- 0..N× `additional`

User 可在 batch confirm 階段選擇略過任何 variation；本 skill 不在 quality gate 強制 ≥3 張。RP02 在 batch outline 末尾以一行 advisory hint 提示「目前缺 X / Y 極端」。

## 檔名約定

沿用 `bdd-constitution.md` §5.1 `filename.convention = NN-prefix-then-title`，**相鄰整數**，不引入字母後綴：

```text
01-<happy path 名稱>.activity
02-<additional / 第二 UAT goal>.activity
03-<extreme_min 名稱>.activity
04-<extreme_max 名稱>.activity
```

每個檔名 title 應包含 variation 標誌（例如 `T1 店長單層簽核`、`T5 總部多級簽核`），讓 reader 不打開檔就能辨認 variation。

## 不適用情境

- 單 actor 線性流，無 decision / fork。
- 無 routing depth 差異（所有路徑經過相同層數 actors）。
- 無 tier table / 無 layer matrix。
- 業務本身已是「決策內收」型（單張內的 DECISION 即足以表達，不會引發路徑長度差異）。

此時 RP02 只產生 1 張 Activity，`variation_role` 標 `additional`，不啟動 advisory hint。

## 明確反例

- ❌ `開房.activity` / `準備與開局.activity` / `對戰攻防.activity` 各寫一小段，要求讀者自己腦補 phase 之間如何銜接。
- ❌ 單張 Activity 只列：
  - `STEP 1 開房`
  - `STEP 2 準備`
  - `STEP 3 開始`
  - `STEP 4 對戰`
  但沒有 state transition、decision、loop、terminal verification。
- ❌ branch 寫成 `已滿 # 流程終止` 或 `失敗 # 不屬本 variation`。

## 正例判準

- ✅ 同一張 Activity 內完整表達大廳進房、準備、開局、設定、主流程執行與終局讀取。
- ✅ 若房間已滿、訂單被退件、玩家全滅等 edge path 發生，branch 仍會走到明確 terminal step 或 final。
- ✅ variation 只用來切結構差異，不用來逃避把單一路徑寫完整。

## Variation Axis Orthogonality（多軸正交切分規則）

當 raw idea / impact scope 同時出現多個 variation 軸時，**每軸獨立切 sibling Activity，不得多軸組合爆炸**。

### 軸的定義

| 軸 | 描述 | 例 |
|---|---|---|
| **Entry trigger 軸** | 不同的觸發起點 | 首購會員 vs 回購會員 vs 補資料重新提交 |
| **Tier / approval depth 軸** | 同一 entry 後的審核層數差異 | T1 店長單層簽核 vs T5 總部多級簽核 |
| **Exception path 軸** | happy 與 reject 路徑差異 | 一般合在 happy Activity 內以 DECISION 表達；除非 reject 後 routing 顯著不同才另切 |

### 正交規則

設有 N1 個 entry trigger、N2 個 tier — **產出 (N1 + N2) 張 sibling Activity**，**不是** (N1 × N2) 張。

**重要原則**：每張 Activity 都必須是**完整 actor-entry → verification arc**（single-path invariant 的延伸 — Activity 是獨立可 demo 單位，不可半截）。「軸」決定「哪一段詳細展開」，**不是**「省略其他段」。

- **Entry-Activity（共 N1 張）**：聚焦 **entry trigger 軸**（不同前置條件下怎麼進入主流程：新增 / 變更 / 補資料 / 不同身分等）。
  - **entry 段詳細展開**：actor、提交動作、初始狀態變異點寫清楚
  - **routing 段通用化**：以 single STEP（如「送交審核佇列」、「進入出貨處理流程」）帶過，不展開 reviewer 層
  - **verification 段須保留**：完整的 actor-entry → verification arc 不省略
- **Tier-Activity（共 N2 張）**：聚焦 **routing depth 軸**（同一條主流程因條件不同走不同 reviewer 層數 / processing chain 長度）。
  - **entry 段通用化**：使用通用 STEP（在註解中可列出可替代的 entry features，例 `# 或 {02-…feature}`），不重複 N1 個 entry 變體的細節
  - **routing 段詳細展開**：所有層 reviewer 串接、rejection-rework loop、tier-specific 路由全部寫出
  - **verification 段須保留**：完整 arc — entry → 路由 → verification（例如查詢結果、狀態回傳）不省略

**反例**：tier-Activity 只有單一 STEP `[STEP:1] @reviewer 審核` 然後 DECISION → 違反 single-path invariant（不是 actor-entry → verification arc，是 mid-flow 截段）。

### 範例

raw idea：首購／回購會員都會走 1～5 層審核，其中 T1 = 店長單層簽核、T5 = 總部多級簽核至營運長。

- ❌ 錯：4 張 Activity（首購 T1、首購 T5、回購 T1、回購 T5）— 軸組合爆炸
- ❌ 錯：1 張 Activity（同 DECISION 並列 4 條 paths）— 違反 single-path invariant
- ✅ 對：4 張 sibling Activity 但軸正交：
  - `01-首購會員建立訂單作業.activity`（entry 軸）
  - `02-回購會員異動訂單作業.activity`（entry 軸）
  - `03-訂單金額分層審核 T1 店長單層簽核.activity`（tier 軸）
  - `04-訂單金額分層審核 T5 總部多級簽核.activity`（tier 軸）

### Decision tree

1. raw idea 是否含 ≥2 個 entry trigger？→ 是：每個 entry 各 1 張 entry-Activity。
2. raw idea 是否含 tier table / approval matrix？→ 是：取 happy（中位）+ extreme_min（最少層）+ extreme_max（最多層）共 ≤3 張 tier-Activity。
3. raw idea 是否含 reject loop？→ 是：原則上歸入 tier-Activity 的 DECISION（不另切 sibling），除非 reject 後 routing depth 顯著不同。

正交切分後，每張 Activity 只描述**一個軸的一個值**，禁止在同檔同時混 entry × tier 兩軸（檔名與 [ACTIVITY] 標題都應只反映單軸）。
