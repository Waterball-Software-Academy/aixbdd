# SOP — 01 scan and classify

掃描目前 function package 下所有 `.feature` 檔，抽出每條 atomic Rule 並依 4-pattern 分類，產出 `$rules_to_expand` 清單供下一 phase 消費。

0. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。禁止以 workspace grep／Glob 取代 resolver。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

   0.1 IF SKILL.md Step 0.1 已 override `$TRUTH_FUNCTION_PACKAGE`／`$FEATURE_SPECS_DIR`：沿用該 binding。ELSE IF caller 以 `@` 或路徑指定單一 target `.feature`：DERIVE slug 並 override（同 SKILL.md Step 0.1）。ELSE IF resolver 輸出之 `TRUTH_FUNCTION_PACKAGE` 仍含 `<<`：DELEGATE `/clarify-loop` 後重跑本步驟 0。

1. SEARCH `${FEATURE_SPECS_DIR}/*.feature`：列出本 function package 範圍內的所有 Feature 檔，得到 `$feature_files`。若 caller 僅指定單一 target `.feature`，`$feature_files` 僅含該檔。本步只產出清單，不寫檔。

2. READ 每一個 `$feature_files` 內容到記憶體：解析其 `Feature:` 標題、`Rule:` 標題列、Rule 標題開頭的「類型前綴」（`前置（參數）`／`前置（狀態）`／`後置（狀態）`／`後置（回應）`，以 ` - ` 與業務標題分隔）、與 Rule body（body 可能為空）。本步僅讀取，不寫檔。

3. FOR EACH Rule in `$feature_files`：DERIVE `$pattern_label` — 依 Rule 標題開頭的「類型前綴」對應到 4 種 pattern 之一：
    - `前置（參數）` → `PATTERN_A_PRECONDITION_INPUT`
    - `前置（狀態）` → `PATTERN_B_PRECONDITION_STATE`
    - `後置（狀態）` → `PATTERN_C_POSTCONDITION_STATE`
    - `後置（回應）` → `PATTERN_D_POSTCONDITION_RESPONSE`
    - 詳細分類規則見 `rules/rule-pattern-taxonomy.md`。本步只產出 in-memory 分類，不寫檔。

4. ASSERT 每條 Rule 標題都帶合法的封閉 4-類型前綴之一（`前置（參數）`／`前置（狀態）`／`後置（狀態）`／`後置（回應）`），且成功對應到 step 3 的某個 pattern：若有 Rule 缺類型前綴、或前綴不在上述封閉 4 類，DELEGATE 詢問用戶補上對應類型前綴後再重跑本 phase；禁止擅自推測 pattern。

5. FOR EACH Rule：ASSERT Rule body 為空（無既有 Example）。若已有 Example，標記 `$rule.skip = true`，本 phase 不再處理它；下一 phase 也跳過。

6. DERIVE `$rules_to_expand`：把通過 step 4 且 `skip != true` 的 Rule 收集成清單，每筆含 `{feature_file, feature_title, rule_title, pattern_label, rule_index_within_file}`。本步只產出 in-memory 結構，不寫檔。

7. ASSERT `$rules_to_expand.length > 0`：若清單為空（所有 Rule 都已補完或都被 skip），DELEGATE 告知用戶「本 package 無待補 Rule」並終止本 skill 全流程；禁止繼續進入 phase 2/3。

8. 將 `$rules_to_expand` 傳遞給 phase 2 消費。本 phase 全程不寫檔（含 `.feature`），僅允許 in-memory 傳遞，禁止建立任何中介檔。
