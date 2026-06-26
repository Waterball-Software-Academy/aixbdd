# 提問模版：變更 Example（Loop step b，合規性未過）

> clarify-loop 的 `context`/`question` 是**單句**；把變更前/後 Example 塞進去會被攤平成一坨。
> 拆兩段：① 先把可讀預覽 **EMIT 到對話**（markdown 渲染），② 再用**精簡單句** DELEGATE `/clarify-loop`。
> 顆粒度＝example／feature 層（改句子／結構，不改驗收意圖）。

## ① EMIT 預覽到對話（markdown，會渲染）

原樣輸出給使用者看：

---
### 變更建議：{{EXAMPLE_TITLE}}

完整 Example（變更前）：
```gherkin
Feature: {{FEATURE_NAME}}
  {{RULE_LINE}}
    Example: {{EXAMPLE_TITLE}}
{{EXAMPLE_GWT_FULLTEXT}}
```

- 未過判準：{{FAILED_CRITERIA}}    （A 合理性／B 前置／C VAR鏈／D Rule一致／E 斷言）
- 變更類型：{{CHANGE_KIND}}        （重寫／拆／併／補前置 Given／對齊 Rule）
- 變更原因：{{CHANGE_REASON}}

變更後 Example：
```gherkin
{{PROPOSED_EXAMPLE}}
```
---

## ② DELEGATE /clarify-loop（精簡，單句；不重貼 Example）

- `context`：`example「{{EXAMPLE_TITLE}}」合規性未過（{{FAILED_CRITERIA}}），變更前/後已列於上方對話。`
- `question`：`同意此變更嗎？（只動步驟結構/句子，不改驗收意圖）`
- `options`：
  - `同意` — 改 `.feature` 後回 a 重驗
  - `不同意` — 說明原因／預期變更方向
