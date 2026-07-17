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
2. 找出需要手寫的步驟並對應其撰寫方法。**custom isa 一律手寫（不分框架）**——來源取自 isa.yml ＋ 測試碼、不看 `.isa.feature`；builtin instruction 則：已安裝框架時由框架 BuiltinIsaPlugin 提供（不手寫），未安裝框架時另以固定 codegen 模版依 `instruction_type` 生成（見 SOP 7）。
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
   PRESET_KIND=${PRESET_KIND}
   STARTER_VARIANT=${STARTER_VARIANT}
   ACCEPTANCE_RUNNER_RUNTIME_REF=${ACCEPTANCE_RUNNER_RUNTIME_REF}
   STEP_DEFINITIONS_RUNTIME_REF=${STEP_DEFINITIONS_RUNTIME_REF}
   FIXTURES_RUNTIME_REF=${FIXTURES_RUNTIME_REF}
   FEATURE_ARCHIVE_RUNTIME_REF=${FEATURE_ARCHIVE_RUNTIME_REF}
   RED_PREHANDLING_HOOK_REF=${RED_PREHANDLING_HOOK_REF}
   INSTALL_SPECTRUM=${INSTALL_SPECTRUM}
   BOUNDARY_ISA=${BOUNDARY_ISA}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   EOF
   ```

2. 接著，我們將上游指定的 Feature files 以 `$SCOPE_FEATURE_FILES` 變數稱之。請簡單在對話中復述一次 `$SCOPE_FEATURE_FILES` 復述完之後，不停，就直接緊接著執行下一步。

3. BIND active boundary：以已 RESOLVE 的 `${PRESET_KIND}` 作為本專案 active boundary；值為空就停下來，回報 `stop_reason: missing_active_boundary`。BIND 並確認此路徑存在：`.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/`

4. Feature 歸檔：把 spec 產物放到測試框架要求的位置（Java cucumber 須在 resources 下；python behave 要與測試碼放一塊）。

   **歸檔開關（feature flag，選填）**：先讀 `${AIBDD_ARGUMENTS_PATH}` 的 `RED_ARCHIVE_SPECS`（未宣告視為 `true`；僅 `false` 才關閉）。若為 `false` → **SKIP 本步整個 Feature 歸檔**——不執行 specs 同步腳本（`archive_specs.py`）、也不跑 `${FEATURE_ARCHIVE_RUNTIME_REF}`；specs 落點改由使用者自訂方式管理（如 pom.xml 的 build/resources 配置、Maven plugin，或自備同步腳本），red-execute 不介入。於 red handoff 註記 `specs_archive: skipped`，直接進 step 5。否則（`true`）依 `${INSTALL_SPECTRUM}` 分流：

   - **`${INSTALL_SPECTRUM}` 為 true（框架 / preprocess）** → RUN 歸檔腳本（**mirror；嚴禁手動複製、禁手改 target**）。它把 specs 的 feature+dsl+isa+api+data mirror 到 test resources（4 target，clean-then-copy；來源刪檔下游一併移除；還沒完成 dsl-refine〔無同名 `.dsl.yml`〕的 feature 不搬）：
     ```bash
     python3 .claude/skills/aibdd-red-execute/scripts/cli/archive_specs.py --specs-dir ${SPECS_ROOT_DIR} --resources-dir src/test/resources
     ```
     產物為 specs 的衍生物；下次歸檔重跑本腳本即可。
   - **否則（未安裝框架）** → EXECUTE `${FEATURE_ARCHIVE_RUNTIME_REF}`（把可跑 `.feature` 依 per-project 歸檔 SOP 放進 runner 樹）。

5. EXECUTE `${RED_PREHANDLING_HOOK_REF}`：在我們實際要撰寫測試程式碼 (紅燈階段) 之前，必須先遵守此專案配置的「紅燈前置處理 SOP (RED_PREHANDLING_HOOK)」來進行測試前置處理。為何需要設置 prehandling hook？好比說一個例子：若是後端專案可能會先需要定義 Database 環境，才能跑 testcontainer 測試；但上述只是例子，你在此步驟唯一該做的事情只有嚴格遵照 `${RED_PREHANDLING_HOOK_REF}` 所指路徑檔案中的每一步。

6. READ `${ACCEPTANCE_RUNNER_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}`，在開始撰寫測試之前先充分閱讀這些文件來理解如何在本專案中執行或撰寫、管理 BDD 之測試程式。

最後，我們開始撰寫測試程式碼。

7. 實作 StepDefinition：

   7a. **恆執行（不分框架）**：嚴格 EXECUTE `steps/implement-custom-isa-stepdefs.md` —— 補齊 custom isa 的 StepDefinition。custom isa 一律手寫；來源掃 isa.yml ＋ 測試碼，**不**逐 `.isa.feature`。

   7b. **僅當 `${INSTALL_SPECTRUM}` 為 false（未安裝框架）才額外執行**：builtin instruction 的 step def 不會由框架提供，須**額外**依 `instruction_type` 走固定 codegen 模版生成。`${INSTALL_SPECTRUM}` 為 true 時 builtin 由框架 BuiltinIsaPlugin 提供，本子步驟 SKIP。
   （此 builtin codegen 步驟尚未改造、暫缺；現行 `steps/implement-all-dsl-steps-in-feature-file.md` 為舊 handler 模型，待後續重做為固定 codegen 模版。）

8. un-ignore 本輪 RED 範疇（**生成 StepDefinition 後、跑 cucumber 前；交使用者決定**）：歸檔後的 feature 預設帶 `@ignore`（cucumber 會濾掉、不跑），用來控制範疇。以 `$SCOPE_FEATURE_FILES` 為選項 DELEGATE `/clarify-loop`（多選）讓使用者挑「這輪要轉紅、下一階段 green 優先實作」的 feature file——**此選擇即本輪 RED 範疇，直接決定 green 先做哪部分**。對選中者 RUN 拿掉 `@ignore`（未選中者維持 @ignore、不進本輪 RED）：

   ```bash
   python3 .claude/skills/aibdd-red-execute/scripts/cli/unignore.py --features <選中的 runtime feature 路徑...>
   ```

   runtime feature 路徑：`${INSTALL_SPECTRUM}` 為 true（框架/preprocess）時為 `src/test/resources/dsl-features/<package>/features/<feature>.feature`（拿掉後 step 9 的 `mvn test` 會重新 preprocess 出不帶 @ignore 的展開檔）；未安裝框架時為歸檔後 runner 樹下的 `.feature`。

9. EXECUTE `steps/red-basic-double-check.md` 來檢查測試品質。

10. READ `references/handoff-schemas.md` and REPORT - 遵照其格式定義來 report `behavior_test_report` 給呼叫者或是遵照上游所指定的 report 方式。
