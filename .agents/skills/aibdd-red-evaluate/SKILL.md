---
name: aibdd-red-evaluate
description: Evaluate a completed AIBDD Red Worker run using runtime-visible feature files, step definitions, and test report evidence. Veto false red and hollow red before Green may consume the run.
metadata:
  user-invocable: true
---

# aibdd-red-evaluate

檢查一次已完成的 Red 跑出來的紅燈，到底是不是「合法又有意義」的紅燈。只有通過這關（verdict `PASS`），下游的 green 才可以接手。這支 skill 只做判斷、出一份評估報告，不去修任何東西。

## 這支 skill 在做什麼

1. 接住上游交來的 Red 證據：red handoff 或一組明確的檔案指標。
2. 把執行器看得到的 feature 檔、step definition、測試報告讀進來。
3. 跑 Type A 硬性關卡：揪出「假紅燈」（其實是環境壞掉、不是行為缺口造成的紅）。
4. 跑 Type B 判斷：揪出「空心紅燈」（測試紅了，但根本沒在測使用者看得到的行為）。
5. 依兩關結果給出 `PASS` 或 `FAIL`，把評估報告交回呼叫者。

## 執行原則

1. 依序執行、不要跳步；每做一步，在訊息中講出你正在做哪一步。
2. 你是評估者，不是修理工：只判斷、只記 findings、只出報告，不去改 feature／step-def／產品程式碼。
3. 除非遇到底下明確寫出的 STOP 條件（通常是證據檔指標缺失），否則一路做到產出評估報告為止；中途不要停下來問「要不要繼續」。
4. Type A 與 Type B 都是硬性關卡：只要任一關有 findings，verdict 就是 `FAIL`，不能把 finding 降級成「僅供參考」。

## 參考文件

讀到需要時再打開：

1. [references/evaluate-input-contract.md](references/evaluate-input-contract.md)：定義 Red evaluate 的 payload 與各種證據檔指標的要求。
2. [references/evaluate-report-schema.md](references/evaluate-report-schema.md)：定義 Red evaluate 的 PASS／FAIL／Veto 報告欄位。
3. [references/hollow-red-rubric.md](references/hollow-red-rubric.md)：定義「空心紅燈」的語意判斷訊號——也就是測試雖然失敗，卻沒在測使用者看得到的行為。

## SOP

### Phase 1 — 接住 Red 的證據

1. RESOLVE arguments：把本 phase 會引用到的 `${VAR}` 一次綁定，resolver 的 stdout 原樣 EMIT 給用戶；非 0 退出就停下來並透傳 stderr。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   FEATURE_ARCHIVE_RUNTIME_REF=${FEATURE_ARCHIVE_RUNTIME_REF}
   STEP_DEFINITIONS_RUNTIME_REF=${STEP_DEFINITIONS_RUNTIME_REF}
   EOF
   ```
2. 接住呼叫者交來的 `red_handoff`（或等價的一組明確檔案指標）。
3. 解析出這次要評估的 `target_feature_files`（規則見 evaluate-input-contract.md）。
4. 找出最終測試報告的路徑：payload 有給就用，沒有就用 `red_handoff.behavior_test_report.report_path`。
5. 找出歸檔後 feature 的根目錄、以及 step definition 的根目錄：以 `red_handoff` 的 runtime snapshot 為準（那是 Red 實際用的路徑），snapshot 沒有才退用上一步 resolver 綁定的 `${FEATURE_ARCHIVE_RUNTIME_REF}`、`${STEP_DEFINITIONS_RUNTIME_REF}`。
6. 找出這次動過的 step definition 檔清單：payload 有給就用，沒有就用 `red_handoff.step_defs_touched`。
7. 確認上面每一個必要的證據指標都存在；只要缺一個，就停下來，回報 `stop_reason: missing_red_evaluation_artifact`。

### Phase 2 — 把看得到的證據讀進來

1. 讀進測試報告。
2. 讀進歸檔根目錄底下、每一個 target feature 檔。
3. 讀進 step definition 檔清單裡的每一個檔。
4. 確認每一個 step-def 檔都落在 step definition 的根目錄底下。
5. 確認測試報告是「執行器原生的證據」，裡面沒有混進任何 DSL 對應的欄位。

### Phase 3 — 跑 Type A 硬性關卡（揪假紅燈）

1. 先準備一份空的 findings 清單。
2. 看測試報告有沒有把每一個 target feature 與 Scenario 都收集進來。
   1. 沒有，就把 `runner_visibility_failed` 記進 findings。
3. 看測試報告裡，target Scenario 有沒有出現缺步驟、未定義、被略過、xfail、被 deselect、import 錯、語法錯、fixture 錯、或環境錯。
   1. 只要有其中之一，就把 `false_red_runner_error` 記進 findings。
4. 逐一檢查每一個 step definition：
   1. 看它的 matcher 有沒有確實貼著 target Scenario 步驟的句子，沒有自由放寬。對不上，就把 `step_matcher_not_grounded` 記進 findings。
   2. 看它的內容有沒有出現空 body、`pass`、`RED-PENDING`、佔位用的 throw、未實作標記、或直接 import 產品內部。有任一項，就把 `invalid_step_definition_body` 記進 findings。
5. 看報告裡「第一個失敗」與其他 target 失敗，是不是 assertion／值差異或預期例外造成的，而且帶有 feature、Scenario、step、訊息的位置。
   1. 不是，就把 `not_legal_red_failure` 記進 findings。

### Phase 4 — 判斷空心紅燈（Type B）

1. 先準備一份空的 findings 清單。
2. 逐一檢查報告裡每一個 target Scenario 的結果：
   1. 整理出一組證據：失敗的那一步、失敗訊息、feature 文字、以及對應的 step definition 內容。
   2. 拿這組證據對照 hollow-red-rubric.md，判斷它是不是空心紅燈。
   3. 是空心紅燈，就把 `hollow_red` 記進 findings。
3. Type B 是硬性關卡：空心紅燈的 finding 不能被降級成「僅供參考」。

### Phase 5 — 交出 Red 評估結果

1. 決定 verdict：Type A 與 Type B 的 findings 都是空的就 `PASS`，否則 `FAIL`。
2. 依 evaluate-report-schema.md，用 `target_feature_files`、各證據指標、Type A findings、Type B findings、以及 verdict，render 出評估報告。
3. 把評估報告交回給呼叫者。

## 完成後接給誰

1. `/aibdd-red-execute`：產生這裡所評估的 Red 證據的 Worker skill。
2. `/aibdd-green-execute`：只能接收評估 verdict 為 `PASS` 的 Red 跑次。
