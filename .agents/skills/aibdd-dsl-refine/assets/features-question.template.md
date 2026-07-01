# 提問模版：選 Features（主流程，多選）

依 worklist（`DSL_REFINE_PLAN.yml`）列出**選定 FP** 下「含未完成定義 dsl step」的 feature，
DELEGATE `/clarify-loop` 讓使用者複選。已全部完成的 feature 不列；一次可選多個。

---

## 選定 FP

`{{FP_SLUG}}`

## 候選 Features（來自 worklist 該 FP 的 `features[]`，含 `status: pending` 的 example）

{{FEATURE_OPTIONS}}
<!-- 逐筆一行：`{{name}}`（待處理 example {{pending_count}}） -->

## 問題

本輪要 refine 哪些 feature？（可多選）

- reply token：`<feature>[, <feature> …]` 或 `全部`
