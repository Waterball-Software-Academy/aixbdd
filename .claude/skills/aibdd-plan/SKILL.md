# AIxBDD - Plan

嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之專案／規格樹內（相對路徑自 **`CWD`** 解析；本檔所列 `${SPECS_ROOT_DIR}`、`${CURRENT_PLAN_PACKAGE}`、`${TRUTH_BOUNDARY_ROOT}`、`${TRUTH_FUNCTION_PACKAGE}`、`${BOUNDARY_PACKAGE_DSL}`、`${BOUNDARY_SHARED_DSL}`、`${TEST_STRATEGY_FILE}` 等皆以 **`CWD`** 為錨。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE / DELEGATE 明確標注的產出物。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: 不重畫 Discovery 真相

- Discovery 已 accepted 的 `${ACTIVITIES_DIR}/**`、rule-only `${FEATURE_SPECS_DIR}/**`、actor 目錄、`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}` 之需求全文 **為唯讀輸入**；本 skill **不得**改寫任何 activity／feature 內容、不得改 atomic rule 文字、不得新增 Scenario／Background／Examples。
- 若發現上游真相不足以推導技術計畫，必須**回頭委派** `/clarify-loop`（profile=`aibdd-plan`），由 Discovery owner 修正後再續跑；**禁止**就地補洞、**禁止**寫弱 placeholder DSL 讓下游 bypass。

## PRINCIPLE: 真相格式委派 specifier skills

- Boundary profile 宣告之 `operation_contract_specifier.skill`／`state_specifier.skill`／`component_contract_specifier.skill`，是寫入 `${TRUTH_BOUNDARY_ROOT}/contracts/**`／`${TRUTH_BOUNDARY_ROOT}/data/**`／Story export 之**唯一合法管道**。
- 本 skill **不得**手寫任何 OpenAPI／DBML／`.stories.tsx`／`.tsx` 檔；只負責 DERIVE caller payload 並以 **`DELEGATE`** 把 payload 交給對應 specifier skill。一個 slice／一個 entity／一個 component 為一次 DELEGATE。
- 違者視為 ownership 違規，**立即 STOP**。

## PRINCIPLE: 澄清只委派 clarify-loop

- 凡須向使用者做**結構化澄清**（locale 選擇、scope 模糊、上游真相缺洞、specifier 不支援等），各 sub-SOP 僅用 **一行 `DELEGATE /clarify-loop`**，並帶 **`delegated_intake`**（`profile=aibdd-plan`，形狀與展開規則見 sibling `clarify-loop/references/intake-expanders/aibdd-plan.md`）。
- **禁止**在 sub-SOP 內 inline classify／branch user reply；**禁止**聊天逐題代替。

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。
2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／`DELEGATE`／`TRIGGER` 工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-bind-and-load/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE`／`DELEGATE`／`TRIGGER` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`）；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**(1)** 的子項全部完成後，以 **`TODOCREATE`／`TASKCREATE`（或等效）** 將 Tier 0 之 **(1)** 標為完成，再對 **(2)** 重複「展開 → 跑完」，依序往後。**未完成當前 phase** 前，**不要**為後續 phase 預開檔案層級的細項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. 在 CWD 底下 grep 搜尋 `**/arguments.yml` 檔案，做 parameters binding for all following phases，這些參數後續每一 phase 都會用到。此檔案一定存在，如不存在請直接停止執行，向使用者回報：「我在 ${CWD} 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」

1. EXECUTE the sub-sop: `01-bind-and-load/SOP.md`

2. EXECUTE the sub-sop: `02-boundary-truth/SOP.md`

3. EXECUTE the sub-sop: `03-implementation-plan/SOP.md`

4. EXECUTE the sub-sop: `04-dsl-synthesis/SOP.md`

5. EXECUTE the sub-sop: `05-plan-doc-and-handoff/SOP.md`

6. 和用戶說道（可使用不同詞彙但維持語意）：「OK 基本上 /aibdd-plan 所有技術計畫都做完了。boundary-map／contracts／data／test-strategy 已落到 boundary 真相，DSL 已物理化、可被 red 端使用，sequence diagrams 與 internal-structure 已寫入 plan package，plan.md 已列出本輪 Impacted Feature Files。如沒問題，可以執行 /aibdd-spec-by-example-analyze，來把 atomic rules 展成 Scenario Outline 與 Examples。」
