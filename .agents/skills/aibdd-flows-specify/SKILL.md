---
name: aibdd-flows-specify
description: >
  紀錄本輪 plan 需求敘述至 spec.md、掃描 boundary truth、維護 impact matrix、拆分 function package charters，先依 API 級顆粒度把每段需求流程萃取成業務 Action、編織成可獨立驗收的 UAT flow 並交 /aibdd-form-activity 產出 .activity 活動圖，再把每個 Action 落成 business-action .feature 清單（rule-less 骨架）。
  當使用者輸入 /aibdd-flows-specify、要開始需求探索／盤點本輪要做哪些 feature 與其範圍切分觸發本 skill。當 CWD 下找不到 arguments.yml 須先執行 /aibdd-kickoff。當只是要為既有 .feature 列舉 atomic rule 則應使用 /aibdd-rules-specify。"
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Flows Specify

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP`  下每一個編號項目為有序 sub-SOP（phase），phase 中每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOPs 所有經授權產生或修改的 artifact，一律落在本次執行的 CWD 子路徑（相對路徑自 CWD 解析；本檔所列 ${SPECS_ROOT_DIR}、${CURRENT_PLAN_PACKAGE}、${PLAN_REPORTS_DIR}、${ACTIVITIES_DIR}、${TRUTH_*} 等皆以 CWD 為錨）。
- 嚴禁把應屬本流程的產物寫到 CWD 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

- 本 SOP 唯一允許產生、修改或刪除的 artifact，只能來自於下述 SOP 中透過 CREATE / WRITE / UPDATE / DELETE 明確標注的步驟。
- 嚴禁除上述 target 外，其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新、刪除或補骨架。

## PRINCIPLE: Strict SOP

- 依序執行 `# SOP` 下的編號項目；每做一步，在訊息中明示該步編號。

- 每一個 sub-SOP（phase）、sub-SOP step 或 DELEGATE 的 skill 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問「是否繼續」；本 skill 唯三合法的暫停點只有：明文 STOP、澄清提問等待回覆、以及最後一步的結尾報告。

- 僅當 sub-SOP step 明文標示須 THINK / REASONING 時，才拉長內省與推演；否則以最直接可做之 READ／PARSE／DERIVE／WRITE／UPDATE／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前所有待辦與進度：目前卡在哪個 sub-SOP（phase），細項又到哪一個 sub-SOP step。底下為代辦兩層結構規則：外層只列 sub-SOP（phase）進入該 phase 再把該 sub-SOP 第一層編號步驟拆成子項，尚未開始的 phase 不必預先展開。

- Tier 0：sub-SOP（phase），對應本檔 `# SOP` 變好項目最外層每一項；勾選這一層代表「該 phase 的細項已全部展開並且依該 phase SOP.md 跑完」。
- Tier 1：phase 內細項，對應該 phase SOP.md 裡第一層編號步驟拆解出的動作（READ／WRITE／DERIVE 等），進入該 phase 時才補齊子項。編號建議：(phase 序)、(phase 序-step 序)（例：1、1-1）。
- 必須工具化：Tier 0／Tier 1 對應的勾選項，要以執行環境提供的任務／待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP 1 時建立代辦清單並隨步驟推進更新狀態。禁止只靠對話列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。

Tier 0 範例（語意範本；實務請用 TODOCREATE／TASKCREATE（或等效工具）建立對應任務，結構對齊即可）：

```markdown
- [ ] (1) 展開並執行至完成：`aibdd-flows-specify/01-sourcing-and-packaging/SOP.md`（NEW）或 `aibdd-flows-specify/01-amending-and-repackaging/SOP.md`（RECONCILE）。
- [ ] (2) 展開並執行至完成：`aibdd-flows-specify/02-activity-analyze/SOP.md`。
- [ ] (3) 展開並執行至完成：`aibdd-flows-specify/03-feature-file-list-analyze/SOP.md`。
```

進入 (1) 後才把 (1) 拆成 Tier 1，其餘 phase 在 Tier 0 維持單列。

Tier 1 NEW 路徑範例：

```markdown
- [ ] (1) 展開並執行至完成：`aibdd-flows-specify/01-sourcing-and-packaging/SOP.md`。
    - [ ] (1-1) 步驟 0：RESOLVE arguments、READ `aibdd-flows-specify/rules/specs-root-layout.md`、DERIVE `$package_naming_language`。
    - [ ] (1-2) 步驟 1：ANCHOR + SEARCH——WRITE 需求敘事全文至 `${PLAN_SPEC}`、SEARCH boundary truth。
    - [ ] (1-3) 步驟 2：CREATE DIR `${PLAN_PACKAGES_DIR}/$plan_package_slug/`。
    - [ ] (1-4) 步驟 3：EXECUTE `aibdd-flows-specify/01-sourcing-and-packaging/steps/maintain-impact-matrix.md`。
    - [ ] (1-5) 步驟 4：WRITE `${PLAN_REPORTS_DIR}/discovery-sourcing.md`、UPDATE `${PLAN_SPEC}`。
    - [ ] (1-6) 步驟 5–6：THINK function package 拆分、CREATE DIRS ONLY `${FEATURE_SPECS_DIR}` 骨架。
    - [ ] (1-7) 步驟 7：UPDATE `discovery-sourcing.md` 與 `${PLAN_SPEC}` 收尾。
- [ ] (2) 展開並執行至完成：`aibdd-flows-specify/02-activity-analyze/SOP.md`。
- [ ] (3) 展開並執行至完成：`aibdd-flows-specify/03-feature-file-list-analyze/SOP.md`。
```

Tier 1 RECONCILE 路徑範例：

```markdown
- [ ] (1) 展開並執行至完成：`aibdd-flows-specify/01-amending-and-repackaging/SOP.md`。
    - [ ] (1-1) 步驟 0：RESOLVE arguments 並驗證 plan package 已鎖定、READ `aibdd-flows-specify/rules/specs-root-layout.md`、DERIVE `$package_naming_language`。
    - [ ] (1-2) 步驟 1：ANCHOR + SEARCH——CHECK baseline 補缺、AMEND `${PLAN_SPEC}` 追加遞增批次、SEARCH boundary truth。
    - [ ] (1-3) 步驟 2：ASSERT DIR `${PLAN_PACKAGES_DIR}/<NNN-plan-slug>/`。
    - [ ] (1-4) 步驟 3：EXECUTE `aibdd-flows-specify/01-amending-and-repackaging/steps/maintain-impact-matrix.md` amend 模式。
    - [ ] (1-5) 步驟 4：UPDATE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 就地更新既有章節反映當前真相、UPDATE `${PLAN_SPEC}`。
    - [ ] (1-6) 步驟 5–6：THINK charter 影響、CREATE DIRS ONLY 僅新開的 function package。
    - [ ] (1-7) 步驟 7：UPDATE `discovery-sourcing.md` 與 `${PLAN_SPEC}` 收尾。
- [ ] (2) 展開並執行至完成：`aibdd-flows-specify/02-activity-analyze/SOP.md`。
- [ ] (3) 展開並執行至完成：`aibdd-flows-specify/03-feature-file-list-analyze/SOP.md`。
```

(1) 的子項全部完成後，以 TODOCREATE／TASKCREATE（或等效工具） 將 Tier 0 之 (1) 標為完成，再對 (2) 重複「展開 → 跑完」，依序往後。未完成當前 phase 前，不要為後續 phase 預展開 Tier 1 細項。

# SOP

執行到哪裡讀到哪裡，嚴禁提早閱讀後續文件，這會讓起始體驗延遲很久，SOP 寫什麼就做什麼，沒有明文 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. EXECUTE the sub-sop aibdd-flows-specify/00-binding-and-routing/SOP.md 以解析 $MODE（RECONCILE 時含鎖定之 plan slug）；完成後不停步，依據 $MODE 路由：NEW → 步驟 1a；RECONCILE → 步驟 1b，以 TASKCREATE（或等效工具）建立 Tier 0 待辦。

1a. 當 $MODE 為 NEW，EXECUTE the sub-sop aibdd-flows-specify/01-sourcing-and-packaging/SOP.md；完成後不停步，直接進入步驟 2。

1b. 當 $MODE 為 RECONCILE EXECUTE the sub-sop aibdd-flows-specify/01-amending-and-repackaging/SOP.md；完成後不停步，直接進入步驟 2。

2. EXECUTE the sub-sop aibdd-flows-specify/02-activity-analyze/SOP.md；完成後不停步，直接進入步驟 3。

3. EXECUTE the sub-sop aibdd-flows-specify/03-feature-file-list-analyze/SOP.md；完成後不停步，直接進入步驟 4。

4. 和用戶說道（可使用不同詞彙但維持語意）：
   - NEW 路徑：「OK，/aibdd-flows-specify 已完成需求收斂、影響矩陣、function package 拆分、UAT flow 活動圖（.activity）與 feature file 清單（rule-less 骨架）。如沒問題，接著執行 /aibdd-rules-specify，為每個 .feature 列舉其驗收用的 atomic rules。」
   - RECONCILE 路徑：「OK，/aibdd-flows-specify 已把本輪需求變更套用到既有 plan package（更新 spec.md、影響矩陣前後對照、受影響的 UAT flow 活動圖與 feature file 清單）。如沒問題，接著執行 /aibdd-rules-specify，為受影響的 .feature 補列 atomic rules。」
