# 提問模版：選 FP（主流程，單選）

依 worklist（`DSL_REFINE_PLAN.yml`）列出「含未完成定義 dsl step」的 FP，
DELEGATE `/clarify-loop` 讓使用者選一個 refine。已全部完成的 FP 不列；一次只選一個。

---

## 候選 FP（來自 worklist `fps[]`，`pending_examples > 0`）

{{FP_OPTIONS}}
<!-- 逐筆一行：`{{slug}}`（待處理 example {{pending_examples}}） -->

## 問題

本輪要 refine 哪一個 FP？（單選）

- reply token：`<NN-slug>`
