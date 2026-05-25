---
name: aibdd-refactor-evaluate
description: Evaluate a completed AIBDD Refactor Worker run by checking strict dev constitution conformance and final full acceptance suite all pass.
metadata:
  user-invocable: true
---

# aibdd-refactor-evaluate

檢查一次已完成的 Refactor 跑次，是不是既守住開發憲章、又維持行為安全。兩件事要同時成立：嚴格符合開發憲章、以及最終整套 acceptance 測試全過。這支 skill 只做判斷、出一份評估報告，不去修任何東西。

## 這支 skill 在做什麼

1. 接住上游交來的 Refactor 證據：refactor handoff 或一組明確的檔案指標。
2. 把最終全套測試報告、開發憲章、以及這次整理涉及的程式碼讀進來。
3. 嚴格比對程式碼有沒有違反開發憲章的硬性條款。
4. 檢查最終全套測試是不是真的全過。
5. 依兩項結果給出 `PASS` 或 `FAIL`，把評估報告交回呼叫者。

## 執行原則

1. 依序執行、不要跳步；每做一步，在訊息中講出你正在做哪一步。
2. 你是評估者，不是修理工：只判斷、只記 findings、只出報告。
3. 只認那一份最終的全套測試報告當證據；不要拿 target-only 的子集報告頂替。
4. 憲章判斷要嚴格：任何被違反的 MUST 或 MUST NOT 都不能被降級成「僅供參考」。
5. 除非遇到底下明確寫出的 STOP 條件（證據檔指標缺失），否則一路做到產出評估報告為止；中途不要停下來問「要不要繼續」。

## 參考文件

讀到需要時再打開：

1. [references/evaluate-input-contract.md](references/evaluate-input-contract.md)：定義 Refactor evaluate 的 payload 與各種證據檔指標的要求。
2. [references/evaluate-report-schema.md](references/evaluate-report-schema.md)：定義 Refactor evaluate 的 PASS／FAIL／Veto 報告欄位。
3. [references/dev-constitution-check.md](references/dev-constitution-check.md)：定義嚴格的開發憲章符合性證據與 Veto 標準。

## SOP

### Phase 1 — 接住 Refactor 的證據

1. RESOLVE arguments：把本 phase 會引用到的 `${VAR}` 一次綁定，resolver 的 stdout 原樣 EMIT 給用戶；非 0 退出就停下來並透傳 stderr。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   DEV_CONSTITUTION_PATH=${DEV_CONSTITUTION_PATH}
   EOF
   ```
2. 接住呼叫者交來的 `refactor_handoff`（或等價的一組明確檔案指標）。
3. 解析出「最終全套 acceptance 測試報告」的路徑（規則見 evaluate-input-contract.md）。
4. 取開發憲章路徑：payload 有給就用，沒有就用上一步 resolver 綁定的 `${DEV_CONSTITUTION_PATH}`。
5. 解析出這次要做憲章檢查的範圍：產品程式碼的根目錄與「改了哪些檔」的範圍。
6. 確認報告路徑存在；找不到就停下來，回報 `stop_reason: missing_refactor_full_suite_report`。
7. 確認開發憲章路徑存在；找不到就停下來，回報 `stop_reason: missing_dev_constitution_path`。
8. 確認檢查範圍有給；沒有就停下來，回報 `stop_reason: missing_constitution_check_scope`。

### Phase 2 — 把證據讀進來

1. 讀進那份測試報告。
2. 讀進開發憲章。
3. 讀進檢查範圍裡的那些產品程式碼檔。
4. 確認報告本身標示這次跑的是「全套 acceptance 測試」，不是只跑 target 的子集。
5. 確認報告是執行器原生的證據，裡面沒有混進任何 DSL 對應的欄位。

### Phase 3 — 嚴格檢查開發憲章

1. 先準備一份空的憲章 findings 清單。
2. 依 dev-constitution-check.md，從開發憲章解析出強制條款（MUST）與禁止條款（MUST NOT）。
3. 逐一檢查每一條條款：
   1. 拿範圍內的程式碼去判斷有沒有違反這一條。
   2. 違反了，就把這一條記進憲章 findings。
4. 憲章判斷要嚴格：任何被違反的 MUST 或 MUST NOT 都不能被降級成「僅供參考」。

### Phase 4 — 檢查全套測試是不是全過

1. 先準備一份空的測試 findings 清單。
2. 看報告是不是 `0 failed`。
   1. 不是，就把 `full_suite_failed` 記進測試 findings。
3. 看報告是不是 `0 errors`。
   1. 不是，就把 `full_suite_error` 記進測試 findings。
4. 看報告裡有沒有場景被不當的 skip、xfail、deselect 或收集遺漏給藏起來。
   1. 有，就把 `not_assertion_passed` 記進測試 findings。

### Phase 5 — 交出 Refactor 評估結果

1. 決定 verdict：憲章 findings 與測試 findings 都是空的就 `PASS`，否則 `FAIL`。
2. 依 evaluate-report-schema.md，用報告路徑、開發憲章路徑、檢查範圍、憲章 findings、測試 findings、以及 verdict，render 出評估報告。
3. 把評估報告交回給呼叫者。

## 完成後接給誰

1. `/aibdd-refactor-execute`：產生這裡所評估的 Refactor 證據的 Worker skill。
2. `/speckit-constitution`：`${DEV_CONSTITUTION_PATH}` 的變更歸它管，不在評估者範圍內。
