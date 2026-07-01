# 提問模版：確認 ISA 展開（Loop step d，逐 dsl_step 一提）

> clarify-loop 的 `context`/`question` 是**單句**；把展開（表格／code block）塞進去會被攤平成一坨。
> 拆兩段：① 先把可讀預覽 **EMIT 到對話**（markdown 正常渲染表格與 code block），② 再用**精簡單句** DELEGATE `/clarify-loop`。
> 顆粒度＝dsl_step 層（一次一個，N 個 dsl_step → N 題）。

## ① EMIT 預覽到對話（markdown，會渲染）

逐一原樣輸出給使用者看：

---
### dsl_step {{INDEX}}/{{TOTAL}}：{{DSL_STEP_NAME}}

完整 Example：
```gherkin
Feature: {{FEATURE_NAME}}
  {{RULE_LINE}}
    Example: {{EXAMPLE_TITLE}}
{{EXAMPLE_GWT_FULLTEXT}}
```

本 dsl_step 對應句：`{{SOURCE_GWT_LINE}}`

預期展開後的 ISA（**僅此 dsl_step**；`scripts/cli/expand_isa.py` 產出）：
```gherkin
{{EXPANDED_ISA_FOR_THIS_STEP}}
```
---

## ② DELEGATE /clarify-loop（精簡，單句；不重貼展開）

- `context`：`dsl_step「{{DSL_STEP_NAME}}」（{{INDEX}}/{{TOTAL}}）的 ISA 展開已列於上方對話。`
- `question`：`這個 dsl_step 的 ISA 展開無誤？`
- `options`：
  - `同意` — 標 `# done`，續下一個 dsl_step
  - `不同意` — 說明原因／預期調整方向
