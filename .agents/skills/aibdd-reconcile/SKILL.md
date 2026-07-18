---
name: aibdd-reconcile
description: >
  當要把一筆需求對齊進 plan package 時觸發，這筆需求可以是對既有規格的變更或缺陷，也可以是要落到既有或全新 plan package 的全新需求。把這筆需求追加進 spec.md 並校準 impact matrix。
metadata:
  user-invocable: true
  source: project-level
  skill-type: planner
---

# AIxBDD - Reconcile

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許調用工具產生或修改的 artifact，只能來自下述 SOP 中明確標注 CREATE、WRITE、UPDATE 或 impact matrix CLI 的步驟；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。

## PRINCIPLE: slug 命名規則

當本批次需求要開一個全新 plan package 時，其落地 filesystem 的 plan package 名（`NNN-<slug>`）之 `<slug>` 主體，一律以專案規格語系（`arguments.yml` 的 `PROJECT_SPEC_LANGUAGE`）並遵守以下規則書寫。

- 技術名詞（API field、DSL token、operationId、domain acronym 如 CRM／SOP／API／OAuth）可保留英文原文；其餘 slug body 不得整段翻成英文。
- 落地 filesystem 的 slug 須 Windows-safe，不得含 \ / : * ? " < > | 及結尾空白或點號。
- 嚴禁以 romanization（漢語拼音／注音／粵拼）、kana、romaji 等 transliteration 充當「規避該語系字元」的 fallback；slug 必須讀得懂、可直接還原為該語系文字。
- 語系為 zh-hant／zh-hans：以該字形書寫，例 `001-會員登入記錄登入時間`；不得寫成 romanization（`001-hui-yuan-deng-ru`）或無此需求的整段英譯（`001-member-login-last-login-at`）。
- 語系為 en-us：slug 以英文 kebab-case 撰寫，例 `001-member-login-last-login-at`。
- 語系為 ja-jp：以日文書寫，禁止以 romaji 取代漢字／假名；語系為 ko-kr：以韓文（Hangul）書寫，禁止以 romaja 取代。
- 禁止無理由中英混拼的 slug（如 `001-會員-login`，除非含上述技術 token 例外）。
- 若專案規格語系缺失或無法判斷，不得自行 fallback 為英文或 romanization，須向使用者釐清。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify` 等待回覆、以及最後一步的結尾報告。

## PRINCIPLE: 限縮推理

- 僅當 step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、CREATE、WRITE、UPDATE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前待辦與進度：目前正在進行 `# SOP` 的哪一個 step。待辦對應本檔 `# SOP` 每一個編號 step，用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具），隨步驟推進更新狀態；嚴禁只在對話列點、不經工具建立的上下文待辦。

範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 解析 arguments。
- [ ] (2) 解析本輪 plan package。
- [ ] (3) 確認本批次需求。
- [ ] (4) 建立 plan package folder。
- [ ] (5) 載入 CLI 手冊。
- [ ] (6) 補齊 spec.md 與 impact matrix 骨架。
- [ ] (7) 追加本批次需求至 spec.md。
- [ ] (8) 盤點需重建的 impact。
- [ ] (9) 重建為單一 spec 的 impact。
- [ ] (10) 刪除原 impact。
- [ ] (11) 載入校準基準。
- [ ] (12) 探索各階段 impact。
- [ ] (13) 彙整待校準清單。
- [ ] (14) 標記過時 spec。
- [ ] (15) 新增全新 impact。
- [ ] (16) 回報結果。
```

# SOP

沒有明文 THINK、REASONING 就不啟用 extended thinking。

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 解析本輪 plan package

   2.1 對話歷史已指名具體 `NNN-<slug>`（例：稍早曾解析過 plan package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續／重跑 NNN 那包」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`、`$MODE` 為 `RECONCILE`。

   2.2 需求敘事明確指名要開新 plan package（例：「開新的 plan」「建立新 package」「這是新需求，開新包」這類明示字句）則設 `$MODE` 為 `NEW`；僅限明示指名新建，從敘事推測「看起來像新功能」不算。

   2.3 其餘情況不得自行判定: 對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify）是要更新哪一個 plan package（設 `$PLAN_PACKAGE_SLUG` 為該 slug、`$MODE` 為 `RECONCILE`）還是開新 plan package（設 `$MODE` 為 `NEW`），STOP 待使用者回答，候選僅一個甚至為空也必須釐清。

3. 確認本批次需求: ASSERT 使用者已提供需求描述並設為 `$RAW_IDEA`，若無則直接向使用者提問本批次需求（不使用 /clarify），STOP 待使用者回答。

4. 建立 plan package folder: 若 `$MODE` 為 `NEW` 則依 `$RAW_IDEA` 與 slug 命名規則 PRINCIPLE 命名 `$PLAN_PACKAGE_SLUG`（`NNN-<slug>`）並 CREATE `${PLAN_PACKAGES_DIR}/$PLAN_PACKAGE_SLUG/`。

5. 載入 CLI 手冊: READ `aibdd-core::references/impact-matrix/cli-usage.md` 內容，取得通用規則、資料模型、status 語意與各 verb 應用 command。

6. 補齊 spec.md 與 impact matrix 骨架

   6.1 若 `${PLAN_SPEC}` 不存在 則參考 `aibdd-core::references/ssot/spec.template.md` CREATE `${PLAN_SPEC}` 空骨架，僅含需求描述與澄清紀錄章節標題。

   6.2 若 `${IMPACT_MATRIX_YML}` 不存在 則 EXECUTE command 跑一次 impact matrix `init` 建空檔。

7. 追加本批次需求至 spec.md: 參考 `aibdd-core::references/ssot/spec.template.md` 的需求批次填寫規則，在 `${PLAN_SPEC}` WRITE `$RAW_IDEA`。

8. 盤點需重建的 impact

   8.1 EXECUTE command 以 `read`（無 filter）讀出 `${IMPACT_MATRIX_YML}` 全部 impact 作為 `$CURRENT_MATRIX` 並對使用者輸出。

   8.2 依據 `$CURRENT_MATRIX` REASONING `$SPEC_ENTRIES`：把每個 impact 的每個 spec 攤平為一筆 `{ owner, spec_path, impact_id, spec_status }`。

   8.3 依據 `$SPEC_ENTRIES` REASONING `$DUP_KEYS`：以 `(owner, spec_path)` group by 統計各自出現於幾個 impact，取數量大於 1 者，數量為 1 者忽略。

   8.4 依據 `$DUP_KEYS`、`$SPEC_ENTRIES` 與 `$CURRENT_MATRIX` REASONING `$REBUILD_IMPACT_IDS`：取「含任一 `$DUP_KEYS` 之 impact」與「`specs` 多於一個之 impact」兩者的 impact id 聯集。

   8.5 依據 `$REBUILD_IMPACT_IDS` 與 `$SPEC_ENTRIES` REASONING `$REBUILD_KEYS`：取 `$REBUILD_IMPACT_IDS` 所有 impact 內出現過的所有 `(owner, spec_path)` 聯集。

9. 重建為單一 spec 的 impact: 對 `$REBUILD_KEYS` 每個 `(owner, spec_path)` 執行下列 CLI command，任一回 ok 為 false 即 STOP 並對使用者輸出其 violations。

   9.1 EXECUTE command `write --owner <owner> --quote <quotes> --rationale <rationale> --spec <spec_path>` 新建一個只含該 spec 的 impact，其產生的 id 作為 `$NEW_ID`；由 `quote` 傳入該 `(owner, spec_path)` 在 `$REBUILD_IMPACT_IDS` 所有 impact 的 quotes 聯集設為 `$MERGED_QUOTES`；`rationale` 依據 `$MERGED_QUOTES` 以一句話說明此 impact 在該 owner 下為何要產生該 spec。

   9.2 若該 `(owner, spec_path)` 在 `$CURRENT_MATRIX` 原各 impact 的 spec status 皆為 consistent 則 EXECUTE command `transit-status --id <$NEW_ID> --spec <spec_path> --status consistent`。

10. 刪除原 impact: 對 `$REBUILD_IMPACT_IDS` 每個 id EXECUTE command `remove --id <id>`，command 回 ok 為 false 即 STOP 並對使用者輸出其 violations。

11. 載入校準基準

    11.1 EXECUTE command 以 `read`（無 filter）重新讀出 `${IMPACT_MATRIX_YML}` 全部 impact 作為 `$CURRENT_MATRIX` 並對使用者輸出。

    11.2 確立 finding 構成原則作為 `$FINDING_RULE`：以 `$RAW_IDEA` 的完整敘述段落為捕捉單位（一段為一個或多個語意連續的自然段，含段內的表格／分級／允許值／回應欄位等列舉清單整塊），一個 impact 把某幾個段落交給某 owner 職責下 formulate 成 spec；本步以段落為單位對照既有 spec 判斷該段是改動既有 spec、還是須由 owner 新建 spec。每個 finding 為 `{ owner, quotes, spec_path }`：`owner` 為所屬階段；`quotes` 為交給該 owner 的 `$RAW_IDEA` 段落，一律逐字整段照抄；同一段落若同時觸及多個 owner 的職責，則該段落同時歸屬每個被觸及 owner 的 finding，`quotes` 可跨 owner 重疊不必互斥；`spec_path` 僅在影響既有 spec 時填其相對 `${TRUTH_BOUNDARY_ROOT}` 的路徑，否則留空，確定或有懷疑被牽動者皆視為受影響。派工從寬，各 owner 之後只以掛名自己的 pending impact 為 worklist，不會自行檢查本批次是否需要出手，漏派會讓該階段整批靜默缺工，多派至多是該 owner 領工後確認無事；因此判斷段落是否牽動某 owner 時一律從寬——確定牽動、懷疑牽動、無法明確排除者，皆須為該 owner 構成 finding。

12. 探索各階段 impact

    12.1 `aibdd-flows-specify` 階段: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${FEATURE_SPECS_DIR}` 下 `.feature` 骨架與 `${ACTIVITIES_DIR}` 下 `.activity` 與 `${PLAN_REPORTS_DIR}/function-packaging.md` REASONING 本階段被牽動的 finding，包含但不限於 UAT flow、function package 範圍劃分、feature 範圍劃分，加入 `$STAGE_FINDINGS`。

    12.2 `aibdd-rules-specify` 階段: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${FEATURE_SPECS_DIR}` 下既有 `.feature` 的 atomic rules REASONING 本階段被牽動的 finding，包含但不限於 feature 範圍不變下各條 atomic rule 的對錯與增刪，加入 `$STAGE_FINDINGS`。

    12.3 `aibdd-spec-by-example` 階段: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${FEATURE_SPECS_DIR}` 下既有 `.feature` 的 Scenario／Examples REASONING 本階段被牽動的 finding，包含但不限於 example 具體值、邊界值、step 寫法，加入 `$STAGE_FINDINGS`。

    12.4 `aibdd-api-plan` 階段: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${CONTRACTS_DIR}` 下契約檔 REASONING 本階段被牽動的 finding，包含但不限於 operation contract、對外 operation／路由／欄位，加入 `$STAGE_FINDINGS`；段落分不清是對外互動承諾還是須穩定保存的系統狀態（operation／state 兩屬不明）者，一律先歸本階段收進 finding、不歸 `aibdd-data-plan`。

    12.5 `aibdd-data-plan` 階段: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${DATA_DIR}` 下 schema 檔 REASONING 本階段被牽動的 finding，包含但不限於 persistent data schema、entity／table／欄位，加入 `$STAGE_FINDINGS`。

13. 彙整待校準清單

    13.1 自 `$STAGE_FINDINGS` 取有 `spec_path` 者 REASONING `$STALE_SPECS`：不論該 spec 在 `$CURRENT_MATRIX` 現為 `consistent` 或 `inconsistent`，被 finding 命中即表示有新 quote 要加入該 impact。每筆含 `{ impact_id, spec_path, owner, quote, rationale }`：`impact_id`／`owner` 取自該 spec 所屬 impact；`quote` 為該 impact 既有 quotes 加上該 finding 之 quotes；`rationale` 整合該 impact 更新後的全部 quote，以一句話說明此 impact 在該 owner 下為何要產生其 spec。

    13.2 自 `$STAGE_FINDINGS` 取無 `spec_path` 者 REASONING `$NEW_IMPACTS`，每筆含 `{ owner, quote, rationale }`：`owner` 取自該 finding；`quote` 取自該 finding 之 quotes；`rationale` 整合其 quote 以一句話說明此 impact 在該 owner 下為何要產生 spec。

    13.3 owner 覆蓋檢查: 依 `$STALE_SPECS` 與 `$NEW_IMPACTS` REASONING 檢查 step 12 的每個 owner（`aibdd-flows-specify`、`aibdd-rules-specify`、`aibdd-spec-by-example`、`aibdd-api-plan`、`aibdd-data-plan`）是否各自至少分得一筆。對一筆都沒有的 owner，回到 step 12 該 owner 的 sub-step 以 `$FINDING_RULE` 的派工從寬原則重新 REASONING 一次：只要 `$RAW_IDEA` 任一段落在該 owner 職責下可能需要增修 spec——含被其他階段的變更間接牽動者（例：權限、角色、狀態、欄位、流程的連動）——即補構成 finding 併入 13.1／13.2。重查後仍無 finding 的 owner 屬例外情況，記入 `$UNDISPATCHED_OWNERS`，每筆含 `{ owner, reason }`：`reason` 為本批次確定不牽動該階段的具體排除理由，嚴禁只寫「需求未提及」帶過；亦嚴禁為湊數捏造與 `$RAW_IDEA` 無關的任務。

14. 標記過時 spec: 對 `$STALE_SPECS` 每一筆 `{ impact_id, spec_path, owner, quote, rationale }` 執行下列 CLI command；任一 command 回 ok 為 false 時依其 `violations` 修正後重試直到 ok。

    14.1 若該筆 `quote` 或 `rationale` 較 `$CURRENT_MATRIX` 現值有更新 則 EXECUTE command `read --id <impact_id>` 取回該 impact 全貌後 EXECUTE command `write --id <impact_id>` 以更新後的 `quotes` 與 `rationale` 取代該 impact，保留其餘既有 spec 與 quotes 不遺漏；無變化則略過。

    14.2 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status inconsistent`。

15. 新增全新 impact: 對 `$NEW_IMPACTS` 每一筆 `{ owner, quote, rationale }` EXECUTE command `write --owner <owner> --quote <quote> --rationale <rationale>` 新建一個 spec-less 的 `pending` impact；任一 command 回 ok 為 false 時依其 `violations` 修正後重試直到 ok。

16. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-reconcile 已把本批次需求追加進 `spec.md`，並把影響矩陣校準完成：受影響而過時的 spec 已標成 `inconsistent`（對應 impact 降級為 `pending`），新發現的影響已新增為 `pending` impact。下面逐一列出本輪被標 `inconsistent` 的 spec 與新增的 impact：<逐一列出>。」若 `$UNDISPATCHED_OWNERS` 非空，接著逐筆輸出「owner <owner> 本輪未獲派任何 impact，排除理由：<reason>」。最後輸出「接著請依序重新執行 planner skills（`aibdd-function-packaging`、`aibdd-flows-specify`、`aibdd-rules-specify`、`aibdd-spec-by-example`、`aibdd-api-plan`、`aibdd-data-plan`）。」
