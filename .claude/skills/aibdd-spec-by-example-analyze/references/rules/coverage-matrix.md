# Coverage Matrix — Spec-by-Example 覆蓋矩陣

> **Legacy reference**：測試維度詞表與矩陣空格語意；**維度選取決策樹**以
> `reasoning/aibdd-spec-by-example-analyze/02-classify-rule-test-strategy.md` +
> `05-build-coverage-handoff.md` 為準。

Reason §3.⑤ 呼叫本檔。目標 = 用二維矩陣（rule × 測試維度）判定 example 的最小必要集合，避免「每條 rule 寫一條 happy path」的脆弱覆蓋。

---

## §1 測試維度清單

對每條 atomic rule 逐條過下列維度；每個維度要有至少一條 example（或明記為 N/A）：

| 維度 | 意涵 | 必要性 |
|------|------|-------|
| `happy_path` | 正常成功路徑 | 必要 |
| `boundary_min` | 輸入 / 狀態的最小邊界（0、空字串、空 list、起始狀態） | 有值域時必要 |
| `boundary_max` | 輸入 / 狀態的最大邊界（上限、最末狀態） | 有值域時必要 |
| `invalid_input` | 輸入違反前置條件 / validation | 有輸入時必要 |
| `concurrent_state` | 狀態 race / 同一 aggregate 被並行改動 | 涉及狀態變更時建議 |
| `authorization` | actor 無權執行 | 有 actor 權限時必要 |
| `idempotency` | 同一指令重放兩次 | 有副作用時建議 |
| `failure_path` | 下游 / 外部服務 / I/O 失敗 | 涉及外部 call 時必要 |

> 「必要 / 建議 / N/A」 由 rule 的結構決定，不由作者喜好決定。例：純 query rule 不必寫 idempotency；純事件訂閱 rule 可能不需 happy_path（概念上所有訊息都是等價的）。

---

## §2 矩陣草擬程序

### ① 建矩陣

以 rule 為列、測試維度為欄，逐格填入：

| rule_id | happy_path | boundary_min | boundary_max | invalid_input | authorization | failure_path |
|---------|-----------|--------------|--------------|---------------|---------------|--------------|
| `rule-checkout-empty-cart` | ✅ | N/A | N/A | ✅ | N/A | — |
| `rule-checkout-insufficient-stock` | ✅ | ✅ | ✅ | ✅ | — | ✅ |

- `✅` = 已有 example 覆蓋 → 填入 example id
- `—` = 尚無 example → 要補
- `N/A` = 此維度對本 rule 不適用 → 需一句理由（例：「純 query，無狀態變更」）

### ② 補空格

對每格 `—`，決定補 example 的策略：

- 若可併入既有 Scenario Outline 的 Examples 列 → 追加一列
- 若需獨立 Scenario（例：`authorization` 需特殊 Given）→ 新增一條
- 若 rule 本身無法推出具體值 → 標 `CiC(BDY)` 或 `CiC(GAP)`

### ③ 輸出 CoverageRow

每個 `(rule, dimension, example_id)` triplet 產出一行 coverage entry：

```yaml
coverage_type: example
rule_id: <atomic rule 錨點>
dimension: happy_path
example_id: <example 錨點 - scenario title + outline row index>
spec_file: features/<boundary-id>/<feature>.feature
```

---

## §3 最小必要 Example 數計算

矩陣建好後，反推最少 Example 數：

```
總 example 數 = sum(每條 rule 的非 N/A 且非共用 row 的格數)
共用 row = 同一 Scenario Outline 的 Examples 表內多列（成本 ≈ 1 條 example）
```

**目標**：總 example 數 ≤ rule 數 × 3（超過要檢討是否真的需要這麼多 outlier case，或被 rule 切分粒度影響）。

---

## §4 反過度覆蓋

下列情境**不**補 example：

| 情境 | 理由 |
|------|------|
| 同一 happy path 改幾個無關欄位名 | 沒新資訊，只是變長度 |
| 已有 Scenario Outline 的 Examples 多到 > 5 列 | 超過記憶負荷；考慮分 Scenario 或用屬性測試外掛 |
| 「為了測而測」的複合 rule（例：A + B + C）但三個獨立 rule 都已覆蓋 | 複合由 DAG 整合層管（`aibdd-atdd-plan`），不在 BDD Analysis 內 |
