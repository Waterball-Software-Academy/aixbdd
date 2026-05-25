---
name: aibdd-red-execute
description: Create legal AIBDD red for target feature files by loading project config, mapping every Scenario step to DSL and core preset assets, rendering runtime-visible step definitions, and emitting a Red handoff. TRIGGER when Red execute is requested or delegated by implementation/debug flow. SKIP when the feature package or BDD stack config is absent.
metadata:
  user-invocable: true
---

# aibdd-red-execute

根據上游指定的範疇內，針對每一個 `.feature` 檔，都去實作 Failing Test (StepDefinitions) 並確認此 Failing Test 是「合法的紅燈」：測試環境是健康的、唯一還在失敗的原因，是產品行為還沒做出來。最後把這次紅燈的整理結果（red handoff）交回給呼叫者。

## 這支 skill 在做什麼

1. 接住呼叫者指定要處理的 `.feature` 檔，載入專案設定與各種規格來源。
2. 把每一條 Scenario 的每一個步驟 (DSL Step)，從 dsl corpus 中尋找該 DSL step 撰寫成 Step Definition 的方法（參考 active boundary preset 的 handlers x variants）。
3. 依對應結果產生「執行器看得到」的 step definitions。
4. 真的去跑一次測試，確認它紅得合法（而不是因為程式壞掉而紅）。
5. 把這次紅燈的證據與對應關係整理成 red handoff，交給下游的 green。

## 執行原則

1. 依序執行、不要跳步；每做一步，在訊息中講出你正在做哪一步，方便對話被壓縮後還能接回來。
2. 除非遇到底下明確寫出的 STOP 條件，否則一路做到產出 handoff 為止；中途不要停下來問「要不要繼續」。真的遇到 STOP 條件時，就停下來、把停止原因（`stop_reason`）與該去找誰回報清楚。
3. 這支 skill 唯一要交出去的東西是最後的 red handoff。中途寫出的 step definition 是達成目的的必要副作用，不是另外的交付物。

## SOP

1. RESOLVE arguments：把後續會用到的 `${VAR}` 一次綁定，resolver 的 stdout 原樣 EMIT 給用戶；非 0 退出就停下來並透傳 stderr（缺 `.aibdd/arguments.yml` 是 exit 1，缺鍵是 exit 2 並列出缺哪些鍵）。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   SPECS_ROOT_DIR=${SPECS_ROOT_DIR}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
   PRESET_KIND=${PRESET_KIND}
   STARTER_VARIANT=${STARTER_VARIANT}
   ACCEPTANCE_RUNNER_RUNTIME_REF=${ACCEPTANCE_RUNNER_RUNTIME_REF}
   STEP_DEFINITIONS_RUNTIME_REF=${STEP_DEFINITIONS_RUNTIME_REF}
   FIXTURES_RUNTIME_REF=${FIXTURES_RUNTIME_REF}
   FEATURE_ARCHIVE_RUNTIME_REF=${FEATURE_ARCHIVE_RUNTIME_REF}
   RED_PREHANDLING_HOOK_REF=${RED_PREHANDLING_HOOK_REF}
   EOF
   ```

2. 接著，我們將上游指定的 Feature files 以 `$SCOPE_FEATURE_FILES` 變數稱之。請簡單在對話中復述一次 `$SCOPE_FEATURE_FILES` 復述完之後，不停，就直接緊接著執行下一步。

3. BIND active boundary：以已 RESOLVE 的 `${PRESET_KIND}` 作為本專案 active boundary；值為空就停下來，回報 `stop_reason: missing_active_boundary`。BIND 並確認此路徑存在：`.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/`

4. 針對 EXECUTE `${FEATURE_ARCHIVE_RUNTIME_REF}`：我們要遵守此專案的「Feature Files」歸檔 SOP，來將 Feature Files 用特定方式歸檔，會有這步驟的原因是：Feature File 必須配合專案所用的 BDD 測試框架，有些測試框架會嚴格要求 Feature file 所在位置約束（好比 Java cucumber 下 Feature file 必須放在 resources 底下，而 python behave 下 feature file 必須和測試程式碼放一塊）。此 SOP 檔案被放置在 `${FEATURE_ARCHIVE_RUNTIME_REF}` 所指定的路徑中。

5. EXECUTE `${RED_PREHANDLING_HOOK_REF}`：在我們實際要撰寫測試程式碼 (紅燈階段) 之前，必須先遵守此專案配置的「紅燈前置處理 SOP (RED_PREHANDLING_HOOK)」來進行測試前置處理。為何需要設置 prehandling hook？好比說一個例子：若是後端專案可能會先需要定義 Database 環境，才能跑 testcontainer 測試；但上述只是例子，你在此步驟唯一該做的事情只有嚴格遵照 `${RED_PREHANDLING_HOOK_REF}` 所指路徑檔案中的每一步。

6. READ `${ACCEPTANCE_RUNNER_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}`，在開始撰寫測試之前先充分閱讀這些文件來理解如何在本專案中執行或撰寫、管理 BDD 之測試程式。

最後，我們開始撰寫測試程式碼。

7. [LOOP] 針對每一個 target feature file in `$SCOPE_FEATURE_FILES`，請嚴格 EXECUTE `steps/implement-all-dsl-steps-in-feature-file.md`。

8. EXECUTE `steps/red-basic-double-check.md` 來檢查測試品質。

9. READ `references/handoff-schemas.md` and REPORT - 遵照其格式定義來 report `behavior_test_report` 給呼叫者或是遵照上游所指定的 report 方式。
