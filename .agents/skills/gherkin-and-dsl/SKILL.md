---
name: gherkin-and-dsl
description: Evaluate and refactor Gherkin feature files and DSL vocabularies so they can be implemented as test code with minimal inference. Use when converting test plans into Gherkin, reviewing or tightening Given/When/Then sentences, deciding Rule/Background/Scenario Outline/DataTable structure, or checking whether Gherkin and DSL fully cover the intended test cases.
disable-model-invocation: true
---

# Gherkin And DSL

把 Gherkin 與 DSL 收斂成兩件事同時成立：

- PM / 需求方讀得懂 Gherkin
- AI / 測試作者可以直接把 Gherkin + DSL 落地成 step definitions 與測試程式碼

## Quick Start

1. 先讀目標 feature files、同模組 `dsl.md`、相關介面根共用 `dsl.md`、上游 testplan / spec。
2. 先判斷本輪是「建立」、「檢查」還是「重構」。
3. 結構與詞彙一起改，**不要只改 Gherkin 不改 DSL**。
4. 任一 Gherkin 句型若找不到 DSL 對應，先補 DSL，再回填 feature。
5. 最終結果必須同時滿足「業務可讀」與「可直接寫測試」。

## SOP

## Phase 1 -- 收斂輸入與輸出範圍

1. READ 讀取使用者需求、目標 feature files、同模組 `dsl.md`、與目標句型相關的介面根共用 `dsl.md`、上游 testplan / spec，確認本輪介面與處理範圍。
2. THINK 判斷本輪是新建、覆蓋驗證、句型收斂、結構重組或嚴格度補強，並盤點要修改的 feature 與 DSL 檔案。
3. WRITE 回報修改範圍與會影響切檔或句型邊界的高影響歧義；若有歧義，先停下確認。

## Phase 2 -- 盤點測試案例與覆蓋缺口

1. READ 讀取 [STANDARDS.md](STANDARDS.md) 中的「覆蓋與嚴格度標準」與「Gherkin 句型標準」。
2. THINK 逐一比對每個 test case 的 Arrange / Act / 預期輸出 / 必須維持不變 / 本案例不驗證，判斷目前的 Gherkin 與 DSL 是否已完整覆蓋；若只是有步驟但語意被稀釋，也算缺口。
3. WRITE 列出缺口：缺少句型、句型過胖、DataTable / Background / Rule 邊界錯置、Then 嚴格度不足、或 Gherkin 有技術語句外露。

## Phase 3 -- 收斂 Gherkin 句型

1. READ 讀取 [STANDARDS.md](STANDARDS.md) 中的「Gherkin 語言邊界與句型收斂」與「參數 / DataTable 格式」。
2. THINK 收斂 `Given` / `When` / `Then` 的共用句型：語意相同必須共用；句子過胖就拆成更核心、可重用的步驟；只有多列資料或多欄位摘要時才優先用 DataTable。
3. WRITE 修改 Gherkin：補 Given / When / Then、補業務相關預設值註解、調整 DataTable、移除不再需要的搬運期註解與技術細節。

## Phase 4 -- 收斂 DSL 詞彙表

1. READ 讀取 [STANDARDS.md](STANDARDS.md) 中的「DSL 必備欄位」、「後端實作語意」與「前端實作語意」。
2. READ 若需要建立、移動 DSL row，或判斷句型應由模組或介面根承接，按需讀取 `rules/介面功能模組與DSL唯一歸屬判準.md`，確認完整契約與唯一歸屬判準。
3. THINK 對每個 Gherkin 句型判斷既有 row、DataTable 欄位、預設參數與實作語意是否足夠，並依已載入判準決定唯一權威位置。
4. WRITE 在唯一權威 DSL 檔建立或更新 row，確保句型、參數、DataTable 欄位、預設值與實作語意可直接支援 step definition。

## Phase 5 -- 做結構優化

1. READ 讀取 [STANDARDS.md](STANDARDS.md) 中的「Feature / Rule / Example」與「Background / Scenario Outline / DataTable 決策」。
2. THINK 依功能面向切分 feature files，判斷是否要抽 `Rule`、`Background`、`Scenario Outline`；`Rule` 必須原子化，`Example` 應描述資料情境而不是重複規則句。
3. WRITE 重構 feature files：拆檔、抽 Rule、抽 Background、必要時引入 Scenario Outline，並移除被淘汰的單一總表檔。

## Phase 6 -- 檢查可落地性

1. READ 重新讀取修改後的 feature files、同模組 DSL 與相關介面根共用 DSL。
2. DELEGATE 執行 `uv run .agents/skills/gherkin-and-dsl/scripts/audit_feature_dsl_topology.py --root <features-root>`，機械檢查拓樸、DSL row 重複與每個 step 的唯一匹配，並保留輸出供後續判讀。
3. THINK 結合稽核結果與已載入標準，判斷共用契約是否真的語意一致、每個 test case 是否完整覆蓋、Gherkin 是否維持業務語言、DSL 是否足以直接實作，以及 Then 是否超越表面輸出。
4. WRITE 回報機械稽核結果、語意與結構決策、仍需收斂的句型，以及可直接交給 step definition / 測試實作的範圍。

## Additional Resources

- 詳細標準與決策判準： [STANDARDS.md](STANDARDS.md)
- 完整電商示範： [examples.md](examples.md)
