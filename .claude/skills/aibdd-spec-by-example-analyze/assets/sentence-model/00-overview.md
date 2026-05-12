# 句型模型 — 總覽（lazy-load 入口）

本模板承接 `reasoning/aibdd-spec-by-example-analyze/02–05` 的 reducer 產物：**internal rule metadata**、**測試資料組**、**Outline 合併決策**、**CoverageRow**、**DSL binding trace**。這些資料只供 reasoning / coverage / handoff 使用；填寫時禁止把推理步驟回寫到 `.feature` 或 `references/rules/*` runtime flow，也禁止修改 `/aibdd-plan` 擁有的 `dsl.yml` / OpenAPI / DBML truth。

本 skill 的句型模型採 **分檔 lazy-load**：依工作階段只讀需要的片段，避免把整包模板一次塞進上下文。

## 載入順序（建議）

1. [`01-domain-shell.md`](01-domain-shell.md) — 實體概述、操作清單、句型清單（plan DSL `L1` truth）
2. [`02-rule-reducer-block.md`](02-rule-reducer-block.md) — reducer metadata block（RP-02/03/04 internal 產物格式；**不進 `.feature`**）
3. [`03-test-analysis-per-operation.md`](03-test-analysis-per-operation.md) — 每 operation 測試分析與 Examples 規劃表
4. [`04-coverage-matrix.md`](04-coverage-matrix.md) — 覆蓋矩陣（對齊 RP-05）

## 契約

- **Given / When / Then 模板句**只能來自 matching DSL entry 的 `L1`（以及必要時 shared registry 中宣告之支援 entry）。不存在可機械對齊的 `L1` 模板 → CiC(GAP)。
- **Examples 欄位**必須可追溯到 matching DSL entry 的 `param_bindings` / `datatable_bindings` / `default_bindings` / `assertion_bindings`，或 OpenAPI/DBML truth；不可自行發明 physical binding。
- 填寫時禁止把推理步驟回寫到 `references/rules/*` runtime flow；runtime SOP 以 `reasoning/aibdd-spec-by-example-analyze/*.md` 為準。
