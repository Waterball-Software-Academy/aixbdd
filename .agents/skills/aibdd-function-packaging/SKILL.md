---
name: aibdd-function-packaging
description: >
  當 reconcile 校準 impact matrix 後、要依本批次需求重新對齊各 function package 範圍時觸發。校正 `function-packaging.md` 把每個受牽動的 function package 標記為 `added` 或 `related`，並為 `added` 的 package 建立目錄。
metadata:
  user-invocable: true
  source: project-level
  skill-type: planner
---

# AIxBDD - Function Packaging

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許調用工具產生或修改的 artifact，只能來自下述 SOP 中明確標注 CREATE、WRITE、UPDATE 的步驟；impact matrix 僅供讀取，本 skill 不寫入。

## PRINCIPLE: slug 命名規則

當本批次需求要開一個全新 function package 時，其落地 filesystem 的 function package 名（`NN-<slug>`）之 `<slug>` 主體，一律以專案規格語系（`arguments.yml` 的 `PROJECT_SPEC_LANGUAGE`）並遵守以下規則書寫。

- 技術名詞（API field、DSL token、operationId、domain acronym 如 CRM／SOP／API／OAuth）可保留英文原文；其餘 slug body 不得整段翻成英文。
- 落地 filesystem 的 slug 須 Windows-safe，不得含 \ / : * ? " < > | 及結尾空白或點號。
- 嚴禁以 romanization（漢語拼音／注音／粵拼）、kana、romaji 等 transliteration 充當「規避該語系字元」的 fallback；slug 必須讀得懂、可直接還原為該語系文字。
- 語系為 zh-hant／zh-hans：以該字形書寫，例 `packages/01-會員登入`；不得寫成 romanization（`packages/01-hui-yuan-deng-ru`）或無此需求的整段英譯（`packages/01-member-login`）。
- 語系為 en-us：slug 以英文 kebab-case 撰寫，例 `packages/01-member-login`。
- 語系為 ja-jp：以日文書寫，禁止以 romaji 取代漢字／假名；語系為 ko-kr：以韓文（Hangul）書寫，禁止以 romaja 取代。
- 禁止無理由中英混拼的 slug（如 `packages/01-會員-login`，除非含上述技術 token 例外）。
- 若專案規格語系缺失或無法判斷，不得自行 fallback 為英文或 romanization，須向使用者釐清。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify-loop` 等待回覆、以及最後一步的結尾報告。

## PRINCIPLE: 限縮推理

- 僅當 step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、CREATE、WRITE、UPDATE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前待辦與進度：目前正在進行 `# SOP` 的哪一個 step。待辦對應本檔 `# SOP` 每一個編號 step，用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具），隨步驟推進更新狀態；嚴禁只在對話列點、不經工具建立的上下文待辦。

範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 解析 arguments。
- [ ] (2) 解析本批次 plan package。
- [ ] (3) 載入校正基準。
- [ ] (4) 識別 impact matrix 標記的既有 package。
- [ ] (5) 判定全新需求的 package 歸屬。
- [ ] (6) 梳理決策與 rationale。
- [ ] (7) 落地新 package 目錄。
- [ ] (8) 校正 function-packaging.md。
- [ ] (9) 回報結果。
```

# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析，`${FEATURE_SPECS_DIR}`、`${TRUTH_FUNCTION_PACKAGE}` 另含 `<<NN-functional-module>>` 借位由各 package 決策的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：reconcile 剛校準完那個 package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續校正 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify-loop）要校正哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清。

3. 載入校正基準

   3.1 若 `${PLAN_REPORTS_DIR}/function-packaging.md` 不存在則參考 `aibdd-function-packaging/assets/templates/function-packaging.template.md` CREATE `${PLAN_REPORTS_DIR}/function-packaging.md` 空骨架，僅含 `# Function Packaging` 標題。

   3.2 READ `${PLAN_REPORTS_DIR}/function-packaging.md` 內容作為 `$CURRENT_PACKAGING`。

   3.3 READ `${PLAN_SPEC}` 需求描述段最新批次作為 `$LATEST_BATCH`。

   3.4 EXECUTE command 以 `read --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 全部 pending impact 作為 `$PENDING_IMPACTS`，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`。

4. 識別 impact matrix 標記的既有 package: 設 `$RELATED_PACKAGES` 為 `$PENDING_IMPACTS` 中 spec path 落在 `packages/NN-<slug>/` 下者所對映的既有 `packages/NN-<slug>` 集合；`${CONTRACTS_DIR}`、`${DATA_DIR}` 等 boundary spec 不對映 function package。

5. 判定全新需求的 package 歸屬: 對 `$PENDING_IMPACTS` 中 specs 為空的每個 impact，參考 `aibdd-function-packaging/rules/function-package-granularity.md` 與 `$CURRENT_PACKAGING`，依其 quotes 與 `$LATEST_BATCH` REASONING 其需求該歸入哪個 function package；落入某既有 package 者把該 `packages/NN-<slug>` 加入 `$RELATED_PACKAGES`，無既有 package 可承載者依 slug 命名規則 PRINCIPLE derive 新 `packages/NN-<slug>` 加入 `$ADDED_PACKAGES`。

6. 梳理決策與 rationale

   6.1 對 `$RELATED_PACKAGES` 每個 package，參考 `aibdd-function-packaging/rules/function-package-granularity.md` READ 該 package 於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下的既有 specs 了解職責，依 `$LATEST_BATCH` REASONING 其 rationale 以說明本批次對它要增修或新增哪些 spec。

   6.2 對 `$ADDED_PACKAGES` 每個 package，參考 `aibdd-function-packaging/rules/function-package-granularity.md` 依 `$LATEST_BATCH` REASONING 其 rationale 以說明為何必須新開。

   6.3 設 `$PACKAGING_DECISIONS` 為 `$RELATED_PACKAGES` 與 `$ADDED_PACKAGES` 各 package 的決策集合，每筆為 `{ package_path, flagged_reason, rationale }`，對應 `${PLAN_REPORTS_DIR}/function-packaging.md` 內容章節，語意參考 `aibdd-function-packaging/assets/templates/function-packaging.template.md`。

7. 落地新 package 目錄: 對 `$PACKAGING_DECISIONS` 每個 `flagged_reason` 為 `added` 的決策，依其 `package_path` 的 `NN-<slug>` 解析 `${TRUTH_FUNCTION_PACKAGE}` 與 `${FEATURE_SPECS_DIR}`，CREATE `${TRUTH_FUNCTION_PACKAGE}` 與 `${FEATURE_SPECS_DIR}` 空骨架。

8. 校正 function-packaging.md: 對 `$PACKAGING_DECISIONS` 每個決策參考 `aibdd-function-packaging/assets/templates/function-packaging.template.md` 在 `${PLAN_REPORTS_DIR}/function-packaging.md` 將該 `package_path` 的章節 UPDATE 為其 `flagged_reason` 與 `rationale`，章節不存在則新增；未列入 `$PACKAGING_DECISIONS` 的既有章節保持不動。

9. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-function-packaging 已依本批次需求校正 `function-packaging.md`：新開的 package 已建立目錄並標記 `added`、其餘受牽動的既有 package 標記 `related`。下面逐一列出本批次 `added`／`related` 的 package：<逐一列出>。接著請執行 /aibdd-flows-specify，在這些 package 內展開 UAT flow 與 feature。」
