# 覆蓋矩陣（對齊 RP-05）

每個操作按 Rule 分行；**空格必須是 example id 或 CiC**。`rule_id` 使用 atomic Rule anchor，不使用 operation-level `dsl.source.rule_id` 代替：

| 操作 | Feature File | DSL Entry | Rule Anchor | Scenario 結構 | Examples 行數 | 覆蓋的分析維度 | Binding Trace |
|------|-------------|-----------|-------------|--------------|--------------|---------------|---------------|
| … | … | dsl-... | 前置: … | Outline(N) / Scenario(1) | N / 1 | … | binding keys / targets |

> `Outline(4)` = 4 行共用句型結構+前置狀態的 Scenario Outline；
> `Scenario(1)` = 單行，用普通 Scenario 而非 Outline。
> **成功路徑與失敗路徑的 When+Then 模板不同 → 禁止合成同一 Outline**（RP-04 Step 0）。
