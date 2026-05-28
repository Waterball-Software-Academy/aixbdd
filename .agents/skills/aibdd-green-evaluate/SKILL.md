---
name: aibdd-green-evaluate
description: Evaluate a completed AIBDD Green Worker run by checking only the final full acceptance suite test report. Pass only when the suite is truly all green.
metadata:
  user-invocable: true
---

# aibdd-green-evaluate

檢查一次已完成的 Green 跑次，是不是真的以「整套 acceptance 測試全綠」收尾。只看那一份最終的全套測試報告；只有真的全綠才給 `PASS`。這支 skill 只做判斷、出一份評估報告，不去修任何東西。

## 這支 skill 在做什麼

1. 接住上游交來的 Green 證據：green handoff 或一組明確的檔案指標。
2. 把那份「最終全套 acceptance 測試報告」讀進來，確認它真的是全套、不是只跑 target 的子集。
3. 檢查報告是不是真的零失敗、零錯誤，而且沒有用不當的 skip／xfail／deselect 把場景藏起來。
4. 依檢查結果給出 `PASS` 或 `FAIL`，把評估報告交回呼叫者。

## 執行原則

1. 依序執行、不要跳步；每做一步，在訊息中講出你正在做哪一步。
2. 你是評估者，不是修理工：只判斷、只記 findings、只出報告。
3. 只認那一份最終的全套測試報告當證據；不要拿 target-only 的子集報告頂替。
4. 除非遇到底下明確寫出的 STOP 條件（報告檔指標缺失），否則一路做到產出評估報告為止；中途不要停下來問「要不要繼續」。

## 參考文件

讀到需要時再打開：

1. [references/evaluate-input-contract.md](references/evaluate-input-contract.md)：定義 Green evaluate 的 payload，以及最終全套報告指標的要求。
2. [references/evaluate-report-schema.md](references/evaluate-report-schema.md)：定義 Green evaluate 的 PASS／FAIL／Veto 報告欄位。

## SOP

### Phase 1 — 接住 Green 的報告

1. RESOLVE arguments：把本 phase 會引用到的 `${VAR}` 一次綁定，resolver 的 stdout 原樣 EMIT 給用戶；非 0 退出就停下來並透傳 stderr。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACCEPTANCE_RUNNER_RUNTIME_REF=${ACCEPTANCE_RUNNER_RUNTIME_REF}
   EOF
   ```
2. 接住呼叫者交來的 `green_handoff`（或等價的一組明確檔案指標）。
3. 解析出「最終全套 acceptance 測試報告」的路徑（規則見 evaluate-input-contract.md）。
4. 確認報告路徑存在；找不到就停下來，回報 `stop_reason: missing_green_full_suite_report`。

### Phase 2 — 把全套報告讀進來

1. 讀進那份測試報告。
2. 確認報告本身標示這次跑的是「全套 acceptance 測試」，不是只跑 target 的子集。
3. 確認報告是執行器原生的證據，裡面沒有混進任何 DSL 對應的欄位。

### Phase 3 — 檢查是不是真的全過

1. 先準備一份空的 findings 清單。
2. 看報告是不是 `0 failed`。
   1. 不是，就把 `full_suite_failed` 記進 findings。
3. 看報告是不是 `0 errors`。
   1. 不是，就把 `full_suite_error` 記進 findings。
4. 看報告裡有沒有場景被不當的 skip、xfail、deselect 或收集遺漏給藏起來。
   1. 有，就把 `not_assertion_passed` 記進 findings。

### Phase 4 — 交出 Green 評估結果

1. 決定 verdict：findings 是空的就 `PASS`，否則 `FAIL`。
2. 依 evaluate-report-schema.md，用報告路徑、runner 設定、findings、以及 verdict，render 出評估報告。
3. 把評估報告交回給呼叫者。

## 完成後接給誰

1. `/aibdd-green-execute`：產生這裡所評估的最終全套 acceptance 報告的 Worker skill。
2. `/aibdd-refactor-execute`：只有在 Green 評估 verdict 為 `PASS` 之後才可以接著做。
