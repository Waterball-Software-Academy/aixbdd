---
name: aibdd-dependency-plan
description: >
  當 reconcile 校準 impact matrix 後、本 owner 名下有 pending impact 待落成 dependency registry entry 時觸發。以 `read --owner aibdd-dependency-plan --impact-status pending` 為 worklist，依 Discovery 真相（spec.md／feature truth）盤點測試會經過的外部依賴、判定 kind（值域：api／store／channel／websocket／grpc／identity）、取得或撰寫各依賴的 truth 檔（`${DEPENDENCIES_DIR}/<name>/`），並在全專案唯一的 `${DEPENDENCIES_DIR}/dependencies.yml` registry 登記 entry，最後回寫 impact matrix。
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Dependency Plan

把本輪 Discovery 真相中「業務行為經過外部依賴」的部分盤點成 dependency registry entry（依賴的可測試契約索引）＋truth 檔，供使用者一眼檢視全專案依賴全景、並供下游 dsl-refine／red-execute 依 entry.kind 查 kind-constants 取素材宣告 custom instruction 與實作 step definition。嚴格遵照底下 PRINCIPLEs 來執行 SOP。`# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許產生或修改的 artifact，只能來自下述 SOP 中明確標注的步驟：WRITE `${DEPENDENCIES_DIR}/dependencies.yml`（registry；append 或更新本輪觸及的 entry）、WRITE `${DEPENDENCIES_DIR}/<name>/` 下的 truth 檔、impact matrix CLI 維護 `${IMPACT_MATRIX_YML}`、以及把澄清結論 WRITE 進 `${PLAN_SPEC}` 的澄清區；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。特別地，本 skill 不寫 isa.yml（config 區與 instructions 條目皆不寫——custom instruction 的宣告是 dsl-refine 消費 registry 後的職責）。

## PRINCIPLE: 不重畫 Discovery 真相

Discovery 已 accepted 的 `${FEATURE_SPECS_DIR}/**`、`${ACTIVITIES_DIR}/**`、`${PLAN_REPORTS_DIR}/function-packaging.md`、`${PLAN_SPEC}` 需求描述全文為唯讀輸入；本 skill 不得改寫任何 feature／activity 內容，只能 append `${PLAN_SPEC}` 的澄清區。`${IMPACT_MATRIX_YML}` 僅能經 impact matrix CLI 維護，不得手改 YAML 本體。若發現上游真相不足以判定依賴或其 truth，必須當步 DELEGATE `/clarify` 釐清，禁止補洞。

## PRINCIPLE: kind 值域封閉

值域為 `api`／`store`／`channel`／`websocket`／`grpc`／`identity` 六個 kind，判定依 `aibdd-dependency-plan/rules/scope-discriminant.md`。判定不出 kind（不屬六值域的新型態，如 SMTP 信箱觀測）或範圍內外難辨者，一律收進 `$ASK_BATCH` 向使用者釐清本輪要緩做還是提案新 kind；不得自創 kind、不得硬塞進最相近的 kind。

## PRINCIPLE: truth 不得發明

每個 registry entry 的 truth 必須有出處：使用者自放的 spec 檔（優先採用）、網路官方文件（`origin_url` 必填）、或依 per-kind rule 撰寫的約定檔（標 `evidence: assumed`）。truth 檔只可宣告真相支持的條目；truth 缺位處不得以合理想像補洞，必須 DELEGATE `/clarify`。

## PRINCIPLE: registry 即配置 SSOT

依賴的宣告只住在全專案唯一的 `${DEPENDENCIES_DIR}/dependencies.yml`（每依賴一個 entry），細節 truth 檔住 `${DEPENDENCIES_DIR}/<name>/`；下游讀 registry 取全清單、依 entry.truth.ref 下鑽細節、依 entry.kind 查 aibdd-core references/kind-constants 取 kind 常數。surface 細節（operations／keyspaces／channels）由 truth 檔本身承載，不抄進 registry。registry 與 truth 檔內不得出現任何憑證（credential 不管理）。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step。每一則對使用者的訊息都必須遵守 `aibdd-dependency-plan/rules/step-trace.md` 的訊息面步驟追蹤規定（首行 Step 標記行；回應外部輸入與短過場訊息不豁免；連續 tool 步驟區間補宣告；停點與結尾必含當前步）。輸出任何訊息前，先對照當前待辦清單的步驟狀態組出標記行。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify` 等待回覆、以及最後一步的結尾報告。
- 停點的執行方式恆為「輸出訊息後結束回合、等待下一則輸入」；執行環境一律視為可互動，禁止以任何「偵測不到互動工具」的推論繞過停點。

## PRINCIPLE: 限縮推理

- 僅當 step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、WRITE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前待辦與進度：目前正在進行 `# SOP` 的哪一個 step。待辦對應本檔 `# SOP` 每一個編號 step，用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具），隨步驟推進更新狀態；嚴禁只在對話列點、不經工具建立的上下文待辦。

範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 解析 arguments。
- [ ] (2) 解析本批次 plan package。
- [ ] (3) 查 worklist。
- [ ] (4) 載入 package 範疇。
- [ ] (5) 載入分析基準。
- [ ] (6) 盤點依賴並判定 kind。
- [ ] (7) 逐依賴研究 truth 與 testability。
- [ ] (8) 稽核 entry 草稿。
- [ ] (9) 落地 registry entry 與 truth 檔。
- [ ] (10) 回寫 impact matrix。
- [ ] (11) 回報結果。
```

# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析，`${FEATURE_SPECS_DIR}` 另含 `<<NN-functional-module>>` 借位由各 function package 的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   BOUNDARY_YML=${BOUNDARY_YML}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   DEPENDENCIES_DIR=${DEPENDENCIES_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：稍早解析過 plan package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續做 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify）要做哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清；若使用者指名新建或不存在的 plan package，則 STOP 並提示本 skill 必須基於既有 plan package 執行。STOP 的唯一合法形式＝把詢問訊息輸出後結束本回合，下一則輸入即為使用者回覆；不得以「非互動環境／背景執行／無互動工具」為由跳過詢問自行假定（此類判斷一律錯誤——輸出訊息本身就是發問通道），亦不得改用本 skill 未宣告的訊息指令或通道（如 dp、通知工具）發問；「候選唯一」「候選與 pending impact 對應」皆不構成免問理由，不得視同已確認。

3. 查 worklist: 進入本步前 ASSERT 對話中已存在使用者對 step 2 詢問的回覆訊息（`$PLAN_PACKAGE_SLUG` 必須出自該回覆，不得出自推斷）；ASSERT 不成立即回 step 2 補停點，禁止帶著未經回覆的 slug 繼續。EXECUTE command 以 `read --owner aibdd-dependency-plan --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 屬本 owner 的 pending impact 作為 `$WORKLIST` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`；`$WORKLIST` 各 impact 的 quotes 為本批次本 owner 要落成 dependency registry entry 的需求句，其中 spec 為空的 impact 為待盤點並 add-spec 的全新工作、帶 inconsistent spec 的 impact 為待重新對齊既有 registry entry 或 truth 檔。

4. 載入 package 範疇: READ `${PLAN_REPORTS_DIR}/function-packaging.md` 取各 function package 的 flagged-reason（`added`／`related`）與 rationale 作為 `$PLAN_SCOPE`，作為待讀 feature truth 的範疇。

5. 載入分析基準

   5.1 設 `$WORKLIST_QUOTES` 為 `$WORKLIST` 各 impact 的 quotes 聯集，每句標註其來源 impact id，為本批次本 owner 要落成 dependency registry entry 的需求句。

   5.2 READ `${PLAN_SPEC}` 全文作為本批次盤點依賴的主要真相來源；依據 `$WORKLIST_QUOTES` 在 `${PLAN_SPEC}` 全文 REASONING 每個 quote 跨段落相關的完整需求上下文作為 `$QUOTE_SEGMENTS`。並設 `$BATCH_NO` 為其需求描述段最新批次號。

   5.3 READ `$PLAN_SCOPE` 各 function package 之 `${FEATURE_SPECS_DIR}` feature truth 與 `${ACTIVITIES_DIR}` activity truth 作為 `$DISCOVERY_TRUTH`，為本批次盤點依賴的真相基準。

   5.4 READ `${DEPENDENCIES_DIR}/dependencies.yml`（不存在視為空 registry）讀出既有 entry 清單作為 `$EXISTING_ENTRIES`；既有依賴不重建，只在本批次真相牽動其 truth 時列為待更新。

6. 盤點依賴並判定 kind

   6.1 依 `$QUOTE_SEGMENTS` 參照 `$DISCOVERY_TRUTH` 並嚴格遵照 `aibdd-dependency-plan/rules/scope-discriminant.md` 全部約束 REASONING 依賴盤點清單 `$DEP_INVENTORY`，每筆為 `{ name, kind, 測試互動面, quotes, impact_id, 對照的既有 profile（若有） }`：`name` 為全域唯一 ref（kebab-case）、`kind` 為值域六 kind 之一、測試互動面為該依賴在 feature 中出現的模式（前置／觸發／驗證）。範圍外情境（判別式排除者）明列於盤點附註不入清單；判定不出 kind（不屬六值域的新型態）或範圍內外難辨者蒐集成 `$ASK_BATCH`；本步只推理不落地。

   6.2 若 `$ASK_BATCH` 非空 則一次性 DELEGATE `/clarify` 批次問清，附各項來源 quote 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-dependency-plan` 的澄清區塊，並依結論處置：判定屬第一方 REST endpoint 者改派 owner `aibdd-api-plan`、屬 persistent state 者改派 owner `aibdd-data-plan`（EXECUTE command `read --id <impact_id>` 取回該 impact 後 `write --id <impact_id> --owner <owner>` 重新提供其原 quotes 與 rationale）；判定本輪緩做（含不屬六值域的新型態）者更新該 impact 的 quote／rationale 標記緩做並保留其 pending；再依結論回 6.1 重推，重複至 `$ASK_BATCH` 清空。

7. 逐依賴研究 truth 與 testability: 對 `$DEP_INVENTORY` 每筆依賴，嚴格遵照其 kind 對應的 `aibdd-dependency-plan/rules/kind-<kind>.md` 全部約束 REASONING 出 registry entry 草稿與 truth 檔草稿 `$ENTRY_DRAFTS`（entry 照 `aibdd-dependency-plan/assets/dependencies.template.yml` 對應 kind 條目的骨架填空；surface 細節由 truth 檔承載，不抄進 entry）：

   7.1 truth 取得：先 SEARCH `${DEPENDENCIES_DIR}/<name>/` 有無使用者自放的 spec 檔（有則優先採用並標 `acquisition: user-provided`）；沒有才依該 kind rule 檔的取得分流進行（api kind 得 SEARCH 網路官方文件，取得後標 `acquisition: web-official` 且 `origin_url` 必填；store／channel 依 rule 檔判定 native 或 authored）。truth 缺位且 rule 檔判定不可自產者收進 `$ASK_BATCH`。

   7.2 testability 與 wiring 判定：預設住 `.claude/skills/aibdd-core/references/kind-constants/<kind>.yml`，entry 只在偏離時填 `testability_overrides`；依該 kind rule 檔判定 `sut_property_overrides`。truth 檔內容只可宣告真相支持的條目。

   7.3 若 `$ASK_BATCH` 非空 則比照 6.2 一次性 DELEGATE `/clarify` 批次問清並記澄清區，依結論重推該依賴，重複至清空。

8. 稽核 entry 草稿: 對收斂後的 `$ENTRY_DRAFTS` DELEGATE `/analyze-and-clarify` 稽核，交辦上下文說清楚：稽核對象為 plan package `$PLAN_PACKAGE_SLUG` 需求批次 `$BATCH_NO` 的推論結果；推論目的為依 `$QUOTE_SEGMENTS` 盤點外部依賴並產出 registry entry 與 truth 檔，且每個本 owner pending impact 的依賴面都要有 entry 承接；稽核基準為 `aibdd-dependency-plan/rules/scope-discriminant.md`、各 kind 的 `rules/kind-<kind>.md` 與 `assets/dependencies.template.yml`；待稽核結果為 `$ENTRY_DRAFTS` 完整內容（entry＋truth 檔草稿，附內容本身，非路徑）。依回報的 violations 處置：`fixable` 就地重推對應草稿；`to-clarify` 併入 `$ASK_BATCH` 比照 6.2 批次問清、記澄清區後重推；本輪 violations 尚有 `to-clarify` 未獲使用者回答前不得重新 DELEGATE `/analyze-and-clarify`，待全數處置完畢才重新稽核，重複至 violations 回空。

9. 落地 registry entry 與 truth 檔: 先落 truth——`acquisition: web-official` 取得的 truth 內容 WRITE `${DEPENDENCIES_DIR}/<name>/` 下對應 truth 檔（openapi.yml／asyncapi.yml 等）；authored 約定者依 kind rule 檔的最小欄位 WRITE 約定檔；使用者自放的 truth 檔為唯讀輸入，不得改寫。再對 `$ENTRY_DRAFTS` 每筆依賴 WRITE `${DEPENDENCIES_DIR}/dependencies.yml`——registry 不存在則依 `assets/dependencies.template.yml` 建立，已存在則只 append 或更新本輪觸及的 entry、不得動其他 entry。v1 由本 skill 直接依樣板落地（暫無 specifier skill；樣板即固定規格）。

10. 回寫 impact matrix

    10.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

    10.2 對 `$ENTRY_DRAFTS` 每筆依賴，其 spec 為：registry 檔相對 `${TRUTH_BOUNDARY_ROOT}` 路徑（dependencies/dependencies.yml，必列），以及本 skill 本輪產出的 truth 檔路徑（web-official 或 authored 者必列；user-provided 者不列——非本 skill 產物）；對每個 spec_path，若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

    10.3 結案完成的 impact: EXECUTE command 以 `read --owner aibdd-dependency-plan --impact-status pending` 取回本 owner 仍 pending 的 impact，對其中 specs 非空且全部 spec 皆為 consistent 的每個 impact EXECUTE command `transit-status --id <impact_id> --status resolved`；若 command 失敗則依其 violations 修正後重試直到成功。

11. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-dependency-plan 已以 Discovery 真相把本 owner 的 pending impact 盤點進 `${DEPENDENCIES_DIR}/dependencies.yml` registry，truth 檔落於各依賴資料夾，impact matrix 已同步。下面逐一列出本批次登記或更新的 entry（name／kind／truth 來源與證據等級）與 resolve 的 impact：<逐一列出>。請檢視 registry 與各 truth 檔是否正確——特別是 acquisition 為 web-official 的 truth 來源與 authored 約定檔的內容。」本步不建議下一步，不得引導任何後續 skill 或 slash command，後續由使用者自行決定。
