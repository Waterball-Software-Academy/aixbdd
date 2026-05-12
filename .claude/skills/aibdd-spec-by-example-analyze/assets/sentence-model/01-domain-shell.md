# {Domain} 句型模型 — 領域殼（實體 / 操作 / 句型索引）

## 實體概述

- **性質**: Aggregate / Gateway
- **攜帶狀態**: …
- **Invariant 清單**（若為 Aggregate）: …

## 操作清單

| 操作 | 行為分類 | When Data Table 欄位 | Then Data Table 欄位 | Violation Types |
|------|---------|---------------------|---------------------|-----------------|
| … | … | … | … | … |

## 句型清單（plan DSL L1）

> **Given / When / Then 模板句**必須能在 `dsl.yml` 對應 entry 的 `L1` 找到 canonical 模板（或合併之 shared entry）。不存在模板 → CiC(GAP)。
> 句型中的欄位只能使用該 DSL entry 暴露的 binding key；底層 OpenAPI/DBML target 只留在 trace，不洩漏成裸 contract 欄位。

| # | 類別 | 句型 | DSL Entry | Handler | Binding Keys |
|---|------|------|-----------|---------|--------------|
| G1 | Given | … | … | … | … |
| W1 | When | … | … | … | … |
| T1 | Then | … | … | … | … |
