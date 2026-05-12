# aibdd-principle-starter-stableness

AI x BDD Starter 穩定性原則。

## 目的

定義 starter 在 kickoff 後就**必須預先具備**的基礎建設，使
`/aibdd-red-execute -> /aibdd-green-execute -> /aibdd-refactor-execute`
能以**最小成本**、**最高穩定性**持續推進。

> **如果某個 phase 第一次執行時，才發現某項本可預先提供的基礎建設缺失，
> 需要臨場補建才能繼續，那就是 starter 穩定性違反。**

## 定義

對同一個 feature package：

- **Red** 的成本應集中在建立合法紅燈，而不是修補執行器 wiring、模組載入、
  產物映射、觀測探針、或測試隔離機制。
- **Green** 的成本應集中在 product behavior 實作，而不是回頭補測試執行環境、
  依賴注入接縫、持久化可見性、或識別值重置機制。
- **Refactor** 的成本應集中在依 `${DEV_CONSTITUTION_PATH}` 做結構整理與回歸，
  而不是先補分層骨架、模組邊界、或其它會阻礙拆解的 starter 缺口。

「穩定」還包含 deterministic isolation：同一組 acceptance scenarios 連跑多次，
結果不得依賴前一個 scenario 殘留的狀態、識別值、或載入副作用。

## 反例

以下都算 starter 不穩：

- Red 第一次跑才發現 step definitions 根本不會被 runner 掃到。
- Green 第一次跑才發現測試前置狀態寫進去後，產品入口讀不到。
- Green 第一次需要產生持久化變更腳本時，才發現 starter 缺模板或缺生成骨架。
- Then step 第一次斷言成功/失敗時，才發現 starter 沒有提供通用的 transport/result probe。
- Refactor 想依憲法把 entry layer 變薄時，才發現 starter 根本沒有對應分層骨架可落位。

## 原則

1. **Phase 所需基礎建設必須前置。**
   Starter 應提供每個 phase 的最低可運行基礎建設，不能把「第一次真的需要時再補」
   視為正常流程。
2. **缺口若可預測，就不准延後到 phase 內修。**
   凡是可由 starter 模板、runtime ref、constitution、fixture、common helper
   預先得知的需求，都應在 kickoff 後即到位。
3. **Worker 成本應集中在 feature，不應耗在環境補洞。**
   Worker 的主要成本應落在 red 的合法紅燈、green 的 product code、refactor 的
   結構整理，不應落在共通執行環境補洞。
4. **Starter 必須保證 deterministic test isolation。**
   同一 feature package 連跑多次 acceptance，結果必須穩定。
5. **Starter 必須保證 constitution-friendly refactorability。**
   若 `${DEV_CONSTITUTION_PATH}` 明示分層與邊界，starter 至少要提供不阻礙該分層
   落地的骨架與接縫。
6. **缺口若存在，必須明確歸類為 feature-specific product gap。**
   不應讓 starter 遺漏偽裝成 worker 的正常成本。

## 預防清單

### Cross-phase

- runner 設定、runtime refs、discoverability 規則必須一致
- 啟動測試執行環境後，產品模組必須可被穩定載入
- 持久化結構的宣告、註冊、與變更生成骨架必須完整
- 通用成功/失敗/錯誤斷言所需的 result probe 必須先存在
- 測試前置狀態與產品入口必須共享可對齊的可見性接縫
- scenario teardown 必須同時清除資料狀態與識別值漂移
- constitution 要求的分層骨架必須先存在或有明示保留機制

### Red 前

- runner / dry-run command 與 discoverability 規則一致
- generated steps / runtime artifacts 可被穩定發現
- feature archive contract 與實際 runtime layout 一致
- common assertion helpers 與 shared DSL / shared truth 對齊

### Green 前

- 可覆寫的依賴注入接縫已存在
- 持久化變更生成所需模板與骨架完整
- 結構宣告載入後可被完整看見
- reset 機制已包含 identity / sequence / equivalent identifier reset

### Refactor 前

- dev constitution 已落地為可遵守的分層骨架
- 結構整理不需要先補資料夾或模組邊界才能開始
- runtime 不會因 product-code 拆解而突然踩到 starter 缺口