---
name: aibdd-feature-file-writing-principle
description: AIBDD feature file writing 原則。規範 `.feature` 必須以 Specification by Example 為 SSOT，Given/When/Then 要資料自足、優先驗證完整結果、覆蓋 negative path 與 idempotency，並優先使用一般化的 fixture-driven、filesystem-oriented、harness CLI 情境來表達規格。
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-feature-file-writing-principle

## 目的

1. 把 AIBDD 中 `.feature` 的寫作標準明文化，避免 feature file 退化成「步驟像測試，但沒有提供可重建規格」的空殼。
2. 強制 `.feature` 以 Specification by Example 為 SSOT，讓後續 script、step definition、worker、reviewer 與下一個 AI 都能從同一份文字重新推導出預期行為。
3. 優先使用一般化、好聯想、低 know-how 依賴的情境示範原則：fixture-driven、會讀寫檔案、由 harness-oriented CLI 觸發的工作流。

## 定義

1. `feature file writing` 指的是撰寫、修改、審查 AIBDD 流程中的 `.feature` 檔，包含 `Rule`、`Example`、`Scenario Outline`、`Background` 與 `Given / When / Then` 內容。
2. `Specification by Example` 指的是：每條規格都要用具體輸入、具體操作、具體輸出表示，而不是只寫抽象宣告或只驗證一個空泛 flag。
3. `資料自足` 指的是：Scenario 所需的 fixture manifest、seed file、模板檔、前置目錄與期望輸出，都必須在 feature 或其明確對應的 Given 中被看見，而不是偷吃 repo 內隱存在的 context。
4. `完整結果驗證` 指的是：優先比對最終檔案全文、完整 JSON projection、完整 report artifact，而不是只驗證某一個欄位、某一行存在、或某個布林值變成 `true`。
5. `harness-oriented CLI 情境` 指的是：像 `load_fixture_manifest.py`、`apply_fixture_bundle.py`、`prepare_workspace.py` 這種由命令列啟動、讀 fixture、處理檔案、輸出 artifact 的一般工作流。
6. `可回到 red` 指的是：當實作被清空或重寫時，feature 仍能穩定地把系統拉回 failing test 狀態，作為下一輪實作的起點。

## 反例

1. 只有口頭 Given，沒有把 manifest 內容寫出來。

```gherkin
Example: CLI 成功載入預設 fixture manifest
  Given the default fixture manifest from repo
  When load_fixture_manifest CLI is run
  Then CLI exit code is 0
```

2. 只驗證單一欄位，不驗證完整 projection。

```gherkin
Then CLI JSON bundle_name is "docs-bundle"
```

3. 對 unknown case 只驗證「有錯誤被記錄」，但不把錯誤內容寫出來。

```gherkin
Then one unknown directive was recorded
```

4. 把規則寫成實作細節或字面 heuristic，而不是可觀察行為。

```gherkin
Rule: TODO 註解改名時仍能正確處理
```

5. 第二次執行會不會重複改檔沒有獨立 example，只靠作者心裡知道它應該 idempotent。

## 原則

1. `.feature` 要被當成行為 SSOT，而不是 smoke shell。
   1. 不要只寫一個看起來會跑過的步驟名稱；要把輸入、操作、輸出都說清楚。
   2. 反例：

```gherkin
Example: CLI 成功載入預設 fixture manifest
  Given the default fixture manifest from repo
  When load_fixture_manifest CLI is run
  Then CLI exit code is 0
```

   3. 正例：

```gherkin
Example: 明確 manifest 輸入應得到對應 JSON projection
  Given a fixture manifest at "fixtures/docs/manifest.yml" with content:
    """
    bundle_name: docs-bundle
    directive_to_template:
      - directive: "insert-title"
        template: title.md
      - directive: "insert-summary"
        template: summary.md
    """
  When load_fixture_manifest CLI is run on the manifest path
  Then CLI exit code is 0
  And CLI JSON projection should equal:
    """
    {
      "bundle_name": "docs-bundle",
      "directive_to_template": [
        { "directive": "insert-title", "template": "title.md" },
        { "directive": "insert-summary", "template": "summary.md" }
      ]
    }
    """
```

2. 每個 Scenario 都要真的是 Specification by Example。
   1. `Given` 要有具體資料，`When` 要有明確操作，`Then` 要有可核對結果。
   2. 反例：

```gherkin
Example: directive 會依優先序排序
  Given the default fixture manifest from repo
  Then directives are sorted correctly
```

   3. 正例：

```gherkin
Example: 輸入未排序 directive 時輸出應為最長者在前
  Given a fixture manifest at "fixtures/docs/manifest.yml" with content:
    """
    bundle_name: docs-bundle
    directive_to_template:
      - directive: "insert"
        template: generic.md
      - directive: "insert-summary-block"
        template: summary.md
      - directive: "insert-summary"
        template: summary-short.md
    """
  When load_fixture_manifest CLI is run on the manifest path
  Then CLI exit code is 0
  And CLI JSON projection should equal:
    """
    {
      "bundle_name": "docs-bundle",
      "directive_to_template": [
        { "directive": "insert-summary-block", "template": "summary.md" },
        { "directive": "insert-summary", "template": "summary-short.md" },
        { "directive": "insert", "template": "generic.md" }
      ]
    }
    """
```

3. `Given` 必須資料自足，不可偷吃 repo 既有 context。
   1. 需要的 manifest、template、seed file 都要在 feature 或明確 Given 中被建立。
   2. 反例：

```gherkin
Given the default fixture manifest from repo
```

   3. 正例：

```gherkin
Background:
  Given a fixture manifest at "fixtures/docs/manifest.yml" with content:
    """
    bundle_name: docs-bundle
    directive_to_template:
      - directive: "insert-title"
        template: title.md
      - directive: "insert-summary"
        template: summary.md
    """
  And a template file at "fixtures/docs/title.md" with content:
    """
    # Release Notes
    """
  And a template file at "fixtures/docs/summary.md" with content:
    """
    本次版本包含 3 項變更。
    """
```

4. 優先驗證完整結果，不要只驗單一欄位或中間 flag。
   1. 能比對完整檔案或完整 report，就不要退化成 `contains` 或單欄位 assert。
   2. 反例：

```gherkin
Then CLI JSON bundle_name is "docs-bundle"
```

   3. 正例：

```gherkin
Then the last file content should equal:
  """
  # Release Notes

  本次版本包含 3 項變更。
  """
```

5. Unknown case 也要做成 Spec by Example，不可只驗「有錯」。
   1. 錯誤本身的內容、定位與分類都要被寫出來。
   2. 反例：

```gherkin
Then one unknown directive was recorded
```

   3. 正例：

```gherkin
Then unknown directives should equal:
  """
  - where: README.md:3
    type: insert-footer
    text: unknown directive `insert-footer`; must match fixture manifest directive_to_template
  """
```

6. Negative path 要同時驗證「不該發生什麼」與「原文保留什麼」。
   1. 對 unknown directive，不只要驗不插入內容，也要驗原本的說明文字與註解沒被誤刪。
   2. 反例：

```gherkin
Example: 未知 directive 不套用
  Given a temporary file at "README.md" with content:
    """
    Project Notes

    <!-- insert-footer -->
    """
  When apply_fixture_bundle CLI is run on the last file
  Then the last file content should equal:
    """
    Project Notes

    <!-- insert-footer -->
    """
```

   3. 正例：

```gherkin
Example: 含說明與註解的未知 directive 仍保留原文
  Given a temporary file at "README.md" with content:
    """
    Project Notes

    說明：這一段是使用者手寫內容
    <!-- insert-footer -->
    """
  When apply_fixture_bundle CLI is run on the last file
  Then unknown directives should equal:
    """
    - where: README.md:4
      type: insert-footer
      text: unknown directive `insert-footer`; must match fixture manifest directive_to_template
    """
  And the last file content should equal:
    """
    Project Notes

    說明：這一段是使用者手寫內容
    <!-- insert-footer -->
    """
```

7. Idempotency 要有獨立 example，不可只靠作者假設。
   1. 同一操作第二次執行不應變更，必須被獨立規格化。
   2. 反例：

```gherkin
Rule: 已套用的檔案重跑不應重複插入
  # 沒有第二次 apply 的獨立 Example
```

   3. 正例：

```gherkin
Example: 第二次 apply 不變更
  Given apply_fixture_bundle CLI is run on the last file
  When apply_fixture_bundle CLI is run again on the last file
  Then the last file content should equal:
    """
    # Release Notes

    本次版本包含 3 項變更。
    """
```

8. 原則應描述可觀察行為，不應描述脆弱的字面 heuristic。
   1. 規則不該綁在 `TODO`、`FIXME` 這類字面值，而應綁在真正行為。
   2. 反例：

```gherkin
Rule: TODO 註解改名時仍能正確處理
```

   3. 正例：

```gherkin
Rule: 檔案中的 directive comment block 在首次 apply 時應由 template 內容取代

  Example: 任意 directive comment 都會被 replace
    Given a temporary file at "README.md" with content:
      """
      Project Notes

      <!-- insert-summary -->
      """
    When apply_fixture_bundle CLI is run on the last file
    Then the last file content should equal:
      """
      Project Notes

      本次版本包含 3 項變更。
      """
```

9. 同一條 policy 的邊界條件要用多個 example 把 shape 講滿。
   1. 不只測單一 marker；也要測多行註解、檔尾、夾帶人工說明、已存在內容等 shape。
   2. 反例：

```gherkin
Example: 任意 directive comment 都會被 replace
  # 只測一種單行 shape
```

   3. 正例：

```gherkin
Example: 連續多行 marker comment 會整段被 replace
  Given a temporary file at "README.md" with content:
    """
    Project Notes

    <!-- insert-summary -->
    <!-- insert-summary -->
    """
  When apply_fixture_bundle CLI is run on the last file
  Then the last file content should equal:
    """
    Project Notes

    本次版本包含 3 項變更。
    """
```

10. feature 必須能支撐重新實作，讓系統可安全回到 failing test。
    1. 當實作被清空時，feature 應直接把紅燈原因講出來，成為下一個 AI 的起跑線。
    2. 反例：

```gherkin
Example: apply works
  When apply_fixture_bundle CLI is run
  Then success
```

    3. 正例：

```gherkin
Example: 標題 block 應插在手寫說明之後
  Given a temporary file at "README.md" with content:
    """
    Project Notes

    說明：以下會由 CLI 補上正式標題
    <!-- insert-title -->
    """
  When apply_fixture_bundle CLI is run on the last file
  Then the last file content should equal:
    """
    Project Notes

    說明：以下會由 CLI 補上正式標題
    # Release Notes
    """
```

## 預防清單

1. 我是否把 `Given` 的輸入資料直接寫出來，而不是偷吃 repo 預設 fixture？
2. 我是否讓 `When` 指向單一、清楚、可重演的 CLI 操作？
3. 我是否優先驗證完整結果，而不是只驗一個欄位或布林值？
4. 我是否為 unknown case 寫出完整的 `where / type / text` 預期？
5. 我是否把 negative path 中「不插入」「保留原文」「記錄錯誤」一起寫出來？
6. 我是否為 idempotency 寫了獨立 example？
7. 我是否把 policy 寫成可觀察行為，而不是脆弱的字面 heuristic？
8. 我是否用多個 example 把同一條 policy 的邊界形狀講滿？
9. 這份 feature 在實作被清空時，是否仍能把系統穩定拉回 failing test？
10. 一個第一次接手這個 harness 的 AI，能否只看這份 feature 就知道要重建什麼行為？
