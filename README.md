# AIBDD

> PM 用 Gherkin 定義驗收標準，RD 把它落地成自動化測試，一氣呵成開發出正確的系統。

大多數 AI 開發 workflow 都沒有切清楚 PM 與 RD 的職責。

需求不清楚時，RD 只好反覆跑 `grill-me`，但是 RD 的職責根本不是通靈需求。RD 的專業不該用在這裡。

AIBDD 是第一款將 PM / RD 職責切分清楚的 workflow：

- PM 用 Gherkin 定義驗收標準，並完成 Prototyping。
- RD 專注在系統分析，把 Gherkin 落地到前後端系統，做到高可靠度全自動開發。

PM 負責定義什麼結果才算通過驗收。
RD 直接把需求標準落地成可運作的系統。

## Workflow 與合作方式

每一個步驟都只需要回答兩件事：

1. 現在要執行哪一支 skill？
2. 執行完要 review 哪個產出物（artifact），review 的重點是什麼？

### PM 定義需求與驗收標準

#### `/specify`

由 PM 執行，將這次需求整理成 `spec.md` 與需求 checklist。

快速開始：

```text
/specify

我想從零建立一個 CRM 系統：

- 業務可以建立與管理客戶及公司資料。
- 業務可以記錄每次聯絡內容與下一步行動。
- 業務可以建立銷售機會，並設定階段、預估金額與預計成交日。
- 業務主管可以查看銷售管線，以及每筆銷售機會的負責人與目前階段。
- 只有具備權限的成員可以查看或修改客戶與銷售資料。
- 系統需要包含可操作的網頁介面與後端 API。
```

完成後，PM review：

- `spec.md` 的 User Stories 是否完整表達這次要解決的需求；
- 每條驗收標準是否具體、可判定通過或不通過；
- 正常流程、拒絕情況與重要邊界是否都有被寫出來。

#### `/clarify-over-specs`（選用）

當 PM 希望在寫 Gherkin 前，再完整請 AI 檢查自己的需求邏輯是否完備時執行。

此步驟，PM 僅需要清楚且認真回答 AI 提出的每個問題。

完成後，PM review：

- 更新後的 `spec.md` 是否已納入所有確認過的答案。

#### `/spec-by-example`

由 PM 執行，將驗收標準寫成可直接 review 的 Gherkin Acceptance Criteria。

完成後，PM review：

- 每個 User Story 是否都有對應的驗收 Feature File；
- `Given / When / Then` 組成的流程是否清楚表達前提、行為與預期結果；
- 正常結果與拒絕結果是否都符合產品預期。

以 CRM 的「推進銷售機會」流程為例，`/spec-by-example` 可能產出：

```gherkin
Feature: 推進銷售機會

  Background:
    Given CRM 有以下銷售階段：
      | 順序 | 階段   |
      | 1    | 潛在   |
      | 2    | 已聯繫 |
      | 3    | 提案中 |
      | 4    | 已成交 |
      | 5    | 已失敗 |

  Rule: 只有銷售機會負責人或業務主管可以推進階段

    Example: 負責人完成需求訪談後將銷售機會推進到提案中
      Given "Alice" 負責 "水球軟體" 的銷售機會
      And 該銷售機會目前階段為 "已聯繫"
      And 該銷售機會預估金額為 300000 元
      When "Alice" 記錄聯絡內容為 "需求訪談完成"
      And "Alice" 將銷售機會推進到 "提案中"
      And "Alice" 將下一步行動設定為 "9 月 5 日提供正式提案"
      Then CRM 保留本次聯絡紀錄
      And 銷售機會目前階段為 "提案中"
      And 下一步行動為 "9 月 5 日提供正式提案"

    Example: 非負責人且非業務主管不可推進銷售機會
      Given "Alice" 負責 "水球軟體" 的銷售機會
      And "Bob" 不是該銷售機會負責人
      And "Bob" 不是業務主管
      When "Bob" 將銷售機會推進到 "提案中"
      Then CRM 拒絕這次操作
      And 銷售機會維持原本階段
```

#### `/ui-plan`

由 PM 在 `/spec-by-example` 後執行，根據已確認的驗收 Gherkin 完成 Prototyping。

完成後，PM review `ui-plan.md` 與靜態雛形。此雛形由 1..* 個 HTML 組成，為中保真度雛形，會覆蓋先前所定義的驗收流程。

- PM 此時需花時間確保雛形的 UI/UX 滿足所需。
- PM 確認驗收標準 Gherkin 與雛形後，需求正式交接給 RD 下去系統整合開發。

`spec.md` 完成後，RD 可以在 PM 執行 `/spec-by-example` 與 `/ui-plan` 的同時，平行執行 `/technical-research`。

### RD 進行系統規劃

#### `/technical-research`

由 RD 執行，分析這次需求需要做出的技術決策與技術選型。

完成後，RD 先 review `research.md`：

- AI 做出的每一項技術決策是否合理；
- 採用與不採用各方案的理由是否正確；
- 技術選型是否符合需求、既有系統與已知限制；
- 是否有仍需實驗、效能量測或實作驗證的風險。

確認 `research.md` 沒有問題後，RD 再 review `techstack.md`，確認目前專案的完整技術選型仍符合預期，而不是只確認這次新增的部分。

#### `/system-analysis`

在 `/technical-research` 執行完之後，RD 可執行。

`/system-analysis` 依本次需求是否涉及後端，委派 `/api-plan`（後端 API 設計）與 `/data-plan`（後端資料設計）。

它不會重做 `/ui-plan`。雛形已由 PM 完成；若本次涉及前端，前端 RD 再 review 一次既有的 `ui-plan.md` 與靜態雛形，確認目前技術邊界下可以落地。其他 RD 不需要重做或重看 UI。

完成後，RD 需要 review：

- API Spec 是否符合預期；
- 資料庫設計是否符合公司規範，或是否有資料整合上可改進之處。

RD 須在此階段確認系統設計是正確且高效率的。

### RD 針對前後端，一次性撰寫 BDD 測試計劃（Gherkin - 可執行規格）

#### `/dsl-refine`

由 RD 執行，將 PM 確認的驗收標準作為權威，將其拆成前端與後端的測試計劃（Gherkin - 可執行規格）。

完成後，RD review：

- 前端和後端的 Gherkin 是否有滿足 PM 定義的驗收標準。

此階段通常可以跳過 Review，因為 AI 會謹慎地將驗收標準拆成前後端的 Gherkin，可斟酌信任 AI 的產出。

### RD 拆解並執行實作

#### `/tasks`

由 RD 執行，將本次開發的系統規劃，拆解成 BDD 開發任務清單 -- `tasks.md`。

此任務清單會把開發拆解成 BDD 的 RED -> GREEN -> REFACTOR 等開發步驟，來高速且依序開發每一個 Gherkin Feature Files。

此階段不需要 Review，可信任 AI 的產出。

#### `/implement`

由 RD 執行，讓 AI 針對上一步的任務清單，One-Shot 開發到位且通過所有測試。

完成後，便代表 AI 完成了本次開發。
RD 此時需要 Review 的就是程式的產出，直接操作系統看看是否符合預期。

建議可以先直接跑前端的 Playwright BDD test，直接看網頁的執行流程，便可看見一定的系統運作，而無需全部都依手動測試。

## 快速開始

```text
1. /constitution           必要時建立或調整 artifact 規則。
2. /specify                建立新的 plan package。
3. /clarify-over-specs     選用；進一步確認產出的 spec。
4. 平行執行：
   PM: /spec-by-example    產出可供 review 的驗收 Journey。
       /ui-plan            根據驗收 Gherkin 完成 Prototyping。
   RD: /technical-research 研究技術決策並更新 techstack。
5. PM 確認 Gherkin 與 Prototyping 後 handoff 給 RD。
6. /system-analysis        建立 plan.md，並依 Wave 委派 API / data planners。
7. /dsl-refine             產出可執行的前後端 Gherkin 與 DSL。
8. /tasks                  產出 BDD 開發任務清單。
9. /implement              依任務清單開發到位並通過測試。
```

需求涉及對應 interface 時，`/system-analysis` 會委派 `/api-plan` 與 `/data-plan`。若涉及前端，前端 RD 另外 review PM 已完成的 UI plan 與靜態雛形。

`/truth-delta` 由 truth owner skills 呼叫，通常不需要由使用者手動執行。

當 feature files 與 DSL 需要獨立 review 或重構時，可以使用 `/gherkin-and-dsl`。

## 內含 Skills

主要 workflow：

```text
constitution
specify
clarify-over-specs
spec-by-example
technical-research
system-analysis
api-plan
data-plan
ui-plan
dsl-refine
truth-delta
tasks
implement
bdd
```

共用 Gherkin 與 DSL 標準：

```text
gherkin-and-dsl
```

目前這 15 支 skills 預期環境中另有可相容的 `/clarify` skill。`/clarify` 未包含在本 repo。

## Skill 目錄

skill 的主要目錄是 `.agents/skills/`。

`.claude/skills` 指向同一份檔案：

```text
.claude/skills -> ../.agents/skills
```

Windows 使用者 clone 時應啟用 Git symlink 支援：

```bash
git clone -c core.symlinks=true git@github.com:Waterball-Software-Academy/aixbdd.git
```

## 結論

PM 定義並確認預期的使用者體驗。

RD 把驗收標準轉成系統設計、可執行的測試、任務與產品程式碼。

驗收標準清楚。職責清楚。專業用在系統落地。

## 授權與出處標註

本 repo 使用 [Apache License 2.0](LICENSE)。

`specify`、`clarify-over-specs`、`tasks`、`implement` 與 `technical-research` skills 包含參考並改寫自 [GitHub Spec Kit](https://github.com/github/spec-kit) 的內容。GitHub Spec Kit 使用 MIT License；適用的著作權與授權聲明已保留在各 skill 目錄。

repo 出處標註請見 [`NOTICE`](NOTICE)。
