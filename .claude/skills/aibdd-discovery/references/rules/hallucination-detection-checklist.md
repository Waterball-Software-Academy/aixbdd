# Hallucination Detection Checklist

> **共用偵測規則**。本檔由 Seam 0（`02-sourcing-clarify.md`）/ Seam A（`04-activity-clarify.md`）/ Seam B（`06-atomic-clarify.md`）三個 clarify RP 引用，用於決定何時觸發 cic 題目。
>
> **Class 3（raw 明寫但 AI 失讀）不在本檔範疇**；那由 Phase 4 `check_raw_artifact_alignment.py`（CQ2 P5）獨立處理。

---

## Pattern 1 — Lexical Marker（Seam 0 主用）

**目的**：偵測 raw idea 中 PM 主動標示為「示意」的措辭，防止 AI 把 marker 修飾過的數字 / 概念固化成 SSOT。

### 1.1 觸發條件

對 raw idea 全文做關鍵字掃描，命中以下任一即觸發：

| Marker（中文）| Marker（英文）|
|---|---|
| 可能 / 大概 / 像 / 例如 / 譬如 / 比方說 | maybe / probably / about / around / e.g. / for example |
| 左右 / 上下 / 大約 / 差不多 | roughly / approximately |
| 這只是例子 / 只是舉例 / 實際要看 / 視情況 | this is just an example / depends on |

### 1.2 觸發後輸出

每個命中的修飾語 + 其後接的數字／概念 → 列入 `clarify_payload.questions`，options 採 `(A) 升格為 hard claim / (B) 保留為示意 / (OTHER)`，default = B。

### 1.3 Anti-Pattern

- ❌ 對命中 marker 但 PM 隨後在另一段已明示「就是 X」的 hard claim 重複丟題目
- ❌ 對 marker 之外的 hard claim 數字（無修飾的「7 項」「3 個」）丟題目
- ❌ 在 Seam A / Seam B 重複跑此 pattern（Seam 0 已處理）

### 1.4 對應 fixture 案例

電商訂單 fixture（07-order-checkout-hallucination-audit）Class 1：
- 「**像**低單價 3000 元**可能**店長核准就好」→ 命中 `像` + `可能` × 2
- 「**例如** 5000 元只需要店長簽核」→ 命中 `例如`
- 「**大概**會算到風評 58 分**左右**…**這只是例子**」→ 命中 3 個 marker

---

## Pattern 2 — Inference Without Source（Seam A / Seam B 主用）

**目的**：偵測 reasoning 即將生出某條 rule / actor / branch / step，但在 raw idea 中找不到對應原文（substring / synonym / paraphrase 皆無）。

### 2.1 觸發條件

對 reasoning output（`activity_analyses` / `atomic_rule_draft`）的每個語義單位執行 traceback：

| 單位類型 | Traceback 規則 |
|---|---|
| `activity.actors[*]` | actor 名稱必須在 raw normalized_excerpts 中有 substring / synonym 命中 |
| `activity.decisions[*].branches[*]` | branch label 必須在 raw 中有對應描述 |
| `activity.decisions[*].branches[*].loop_back_target` | loop_back target 必須在 raw 中有「再 X」「回到 X」「重新 X」等明確迴圈線索；無線索 → 觸發 |
| `activity.steps[*].action / postcondition` | 動作關鍵詞必須有 raw 對應，且 **raw 中該詞之語境屬 operation_trigger（actor 主動發起、可獨立 demo），而非 hand-off / 後續處置 / 系統 side-effect**；語境不符 → 觸發（判別見 §2.1.a） |
| `activity.steps[*]` granularity | 一個 step 對應的 raw 子句若包含**多個 actor verb**（CRUD vs assign、view vs record）且各自有獨立 postcondition，必須拆 sibling step；未拆 → 觸發 |
| `activity.steps[*]` decision-selector 一致性 | 若 Decision condition 引用某 attribute（例：意向／結果／興趣／狀態），則最近的 record / set action 必須在 `action.name` 顯式提及該 attribute；漏提 → 觸發（見 §2.1.b） |
| `atomic_rule_draft.rules[*]` | rule subject + action + condition 任一無 raw 對應 → 觸發 |

#### 2.1.a Operation_trigger vs hand-off 判別

`operation_trigger`：actor 主動操作 UI 觸發、可由該 actor 獨立完成 demo、postcondition 可由該 actor 觀察到。
`hand-off / 後續處置`：raw 把它放在「→ 交回給 X」「→ 通知 X 處理」「→ X 接手」「→ 然後 X 處理」等被動承接語境；後續實作可能由系統或他人完成，但**不**是當前 actor 的 demo step。

判別啟發：
- 該動詞前後出現「交回」「轉給」「通知」「丟給」「然後 X 處理」 → 高機率 hand-off
- 該動詞出現於 raw 對 actor 行為的明確列舉句（「他可以 X / Y / Z」） → 高機率 operation_trigger
- 不確定 → 列入 ambiguity_findings；題目格式：「raw 中『X』看起來是 hand-off / 後續處置；是否仍要建為獨立 operation step？」options 同 §2.2

#### 2.1.b Decision selector attribute 命名一致性

當 Decision 的 condition 引用某 attribute（例：「意向」「結果」「興趣」「狀態」），則最近的 record / set action 在 `action.name` 上必須**顯式提及該 attribute**；漏提 → 觸發。

理由：record action 與 decision selector 解耦會在後續 feature step pattern projection 失去語意連結；下游 form-feature-spec / form-activity 的 step pattern 也會無法對齊 attribute。

### 2.2 標註與題目

對無 traceback 的元素，先在 in-memory output 標 `<!-- inferred: raw 未明示 -->`，等本 RP 統一聚合成 cic 題目。

題目 options 預設 `(A) 刪除回 raw 範圍 / (B) 保留並補充來源 / (OTHER)`，default = A。

### 2.3 Anti-Pattern

- ❌ 對 raw 明確提及但用詞略不同的元素丟題目（屬 Class 3 失讀範疇）— traceback 應允許 synonym / paraphrase
- ❌ 對 entity 欄位 schema 越界提問（屬 plan 階段，不在 Discovery scope）

### 2.4 對應 fixture 案例

CRM fixture：
- 「需再追蹤」第三類意向 → activity DECISION 多出無 raw 對應的 branch → Seam A 命中
- HTTP method 寫死 / 「等價狀態」hedge / 版本號 → atomic rule 有自生規則 → Seam B 命中

電商 fixture：
- 訂單附件下載權限（出貨後仍可取發票／僅限客服與買家本人）→ Seam A 或 Seam B 命中（規則 vs 流程依其落點分派）
- 簽核鏈 fallback 順序 → Seam B 命中

---

## Pattern 3 — Demo Anchor（Seam 0 / Seam B 主用）

**目的**：偵測「raw 用 marker 標示為示意的數字／範圍切點」被 AI 落成「規格化結構」（tier table / range table / score band）。屬於 Pattern 1 的「規格化矛盾」延伸；觸發後一定要 cic。

### 3.1 觸發條件

當 reasoning 即將輸出規格化結構（如 tier table、range table、score band），對每個切點 / 邊界值執行：

1. 在 raw 中找對應原文。
2. 檢查該原文是否帶 Pattern 1 marker。
3. **帶 marker 卻被升格為 SSOT** → 命中。

額外：若 raw 中該數字／範圍**重複出現 ≥ 2 次**且每次都帶 marker，視為強訊號（高優先級題目）。

### 3.2 觸發後輸出

題目格式：「以下範圍 raw 標示為示意（帶『可能』『例如』），是否升格為規格切點？」options 同 Pattern 1。

### 3.3 Anti-Pattern

- ❌ 對 raw 中以 hard claim 形式提供的具體數字（無 marker）丟題目
- ❌ 把這個 pattern 用在「raw 完全沒提及的範圍」（屬 Pattern 2 範疇）

### 3.4 對應 fixture 案例

電商 fixture：
- 免運／簽核 tier 切點（`像 500 元 / 例如 800 元 / 單筆 5 萬以上`）被落成 `T1 = ≤500 元, T5 = >5 萬 ~ ≤30 萬`（≤30 萬還憑空多生）→ Seam 0 命中（lexical）+ Seam B 命中（atomic 規則層 demo-anchor）
- 首購 demo 風評「**大概**會算到 58 分**左右**…**這只是例子**」 被落成 activity comment 「風評 48 分 → 折價上限 2000 元 → T2」→ Seam 0 命中

---

## 整體流程

```
RP01 sourcing produced
    │
    ▼
Seam 0（02-sourcing-clarify）
    跑 Pattern 1（lexical sweep）+ Pattern 3（demo-anchor，僅 sourcing 即將寫進規格化結構時）
    │
    ▼
RP02 activity-analyze produced
    │
    ▼
Seam A（04-activity-clarify）
    跑 Pattern 2（流程結構 traceback）
    │
    ▼
RP03 atomic-rules produced
    │
    ▼
Seam B（06-atomic-clarify）
    跑 Pattern 2（規則 traceback）+ Pattern 3（規則內 range/tier）
    │
    ▼
formulation → Phase 4 quality gate → P5 sweep（Class 3，獨立工具）
```

---

## 為什麼集中於本檔（CQ3-b 決議）

3 個 clarify RP 各自寫偵測邏輯會造成：
- 重複維護（marker 清單 / traceback 規則隨業務演化）
- 跨 RP 重疊（如 Pattern 3 同時被 Seam 0 與 Seam B 用）
- 難確認覆蓋率（無單一可審計的 SSOT）

集中後：clarify RP 各自只寫「我用哪些 pattern + 怎麼把命中變題目」，偵測規則本身只在這裡演化。

## 不屬本檔範疇

- **Class 3 失讀**（raw 明寫但 AI 沒照做）→ `scripts/check_raw_artifact_alignment.py`（CQ2 P5）
- **Type C 越界**（資料欄位 schema 寫進 Discovery）→ `scripts/check_discovery_phase.py` 黑名單（P3 衍生改善項）
- **Type D 契約**（sourcing 標 gap 但 feature 仍寫具體實作）→ sourcing-report ↔ feature wording 一致性 gate（P4 衍生改善項）
