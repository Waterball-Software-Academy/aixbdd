# Clause Analysis — atomic rule → Given / When / Then 子句拆解

> **Legacy reference**：部位對應與 ClauseBinding 形狀參考；**clause 拆解與值枚舉順序**以
> `reasoning/aibdd-spec-by-example-analyze/03-enumerate-rule-data-values.md` +
> `05-build-coverage-handoff.md` 為準。

Reason §3.④ 呼叫本檔。目標 = 把每條 atomic rule 拆解為可直接綁定 **plan DSL L1** 句型的子句部位。

---

## §1 三部位映射

Atomic rule 五問自檢的答案（who / whom / does / when / consequence）直接對映到 Gherkin 三部位：

| atomic rule 問題 | Gherkin 部位 | 子句語意 |
|-----------------|-------------|---------|
| when（前置狀態、觸發條件之前的系統狀態） | `Given` | **狀態**：系統 / entity 的初始狀態 |
| does（動作 / 觸發） | `When` | **觸發**：actor 對系統的動作或事件 |
| consequence（結果 / 副作用） | `Then` | **結果**：狀態變化 / 回應 / 對外部的副作用 |

若 rule 內含多個 who × does（複合動作），先拆成多條 atomic rule 再處理；本 skill 不得擅改 rule。

---

## §2 子句拆解程序

對每條 atomic rule，依序做：

### ① 標記句型部位

逐字讀 rule；用 `[Given]` / `[When]` / `[Then]` 在心中標註每個片段：

```
[心中標記]
原 rule：「當使用者點擊付款按鈕時，若購物車為空，則回傳 400 並顯示『購物車為空』」
標註：
- [Given] 購物車為空 ← 前置狀態
- [When] 使用者點擊付款按鈕 ← 觸發
- [Then] 回傳 400 ← 結果（HTTP response）
- [Then] 顯示「購物車為空」 ← 結果（UI feedback / error message）
```

### ② 檢查是否存在隱含前置

若 `Given` 為空（rule 沒寫前置狀態），對照 **matching DSL entry** 的 `L1.given` / shared DSL 與 `test-strategy` 是否已有可執行 setup 模板。

若無任何 plan-owned 來源可補足 → 標 `CiC(BDY)` 於該 rule 處。

### ③ 綁定 plan DSL L1 step pattern

對每個子句，查 matching DSL entry 的 **`L1` given/when/then**（canonical 模板；機械檢查見 `check_preset_compliance.py`）：

- 找得到對應模板 → 綁定（記下 canonical `dsl_l1_pattern` + `dsl_entry_id`）
- 找不到 → 標 `CiC(GAP)`；**不得**自行造新句型（plan DSL L1 truth）

### ④ 輸出 ClauseBinding

對每條 rule 產出一組 ClauseBinding：

```yaml
rule_id: <atomic rule 錨點>
clauses:
  - kind: Given
    text: "購物車為空"
    dsl_l1_pattern: "購物車為空"
  - kind: When
    text: "使用者點擊付款按鈕"
    dsl_l1_pattern: "使用者點擊付款按鈕"
  - kind: Then
    text: "系統回傳 400"
    dsl_l1_pattern: "系統回傳 <status_code>"
  - kind: Then
    text: "系統顯示「購物車為空」"
    dsl_l1_pattern: "系統顯示 <message>"
```

---

## §3 多路徑 rule 處理

當一條 rule 的 consequence 有多條並列路徑（例：`成功則 X；失敗則 Y`），兩種可選策略：

| 策略 | 做法 | 適用 |
|------|------|------|
| A — 一條 Scenario 裝 And / But | Then / And / But 並列多個 step | 路徑都對同一 trigger 且狀態單純 |
| B — 拆成多條 Scenario Outline | 用 Examples 欄位切多條輸入 → 多條路徑 | 觸發輸入有變化（值分類）|

預設用 B；A 僅用於狀態固定 + 結果為「AND 累加」的場景。

---

## §4 反腦補防線

以下情況必標 CiC，不得推斷：

| 情況 | KIND |
|------|------|
| rule 未寫 Given 且 plan DSL / test-strategy 無可引用之 setup 模板 | `CiC(BDY)` |
| 子句無對應 plan DSL `L1` canonical 模板 | `CiC(GAP)` |
| 同一 rule 推出兩個互斥路徑且無法辨別優先順序 | `CiC(CON)` |
| 依業務常識「推論」Given 具體值（如「使用者已登入」） | `CiC(ASM)` |
