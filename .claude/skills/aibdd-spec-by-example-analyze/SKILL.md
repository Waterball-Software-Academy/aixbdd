# AIxBDD - Spec by Example Analyze

嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之專案／規格樹內（相對路徑自 **`CWD`** 解析；本檔所列 `${SPECS_ROOT_DIR}`、`${CURRENT_PLAN_PACKAGE}`、`${FEATURE_SPECS_DIR}`、`${TRUTH_FUNCTION_PACKAGE}`、`${PLAN_REPORTS_DIR}` 等皆以 **`CWD`** 為錨。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE / DELEGATE 明確標注的產出物：feature files 例子填充（**只**經 DELEGATE `/aibdd-form-feature-spec` mode=example-fill）、`${TRUTH_FUNCTION_PACKAGE}/coverage/*.coverage.yml` 之 `coverage_type: example` 列、`${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`、`${PLAN_REPORTS_DIR}/bdd-analyze-quality.md`。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: 不重畫 Plan 真相

- `/aibdd-plan` 已 accepted 的 `${BOUNDARY_PACKAGE_DSL}`、`${BOUNDARY_SHARED_DSL}`、`${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`、`${TEST_STRATEGY_FILE}`、`${FEATURE_SPECS_DIR}/**` 之 atomic rule 本體 **為唯讀輸入**；本 skill **不得**新增或修改任何 DSL entry、不得改寫 contract operation 或 DBML 欄位、不得改 atomic rule 字詞、不得改 feature 路徑／檔名。
- 若發現 plan 真相不足以推導 Example（缺 binding、缺 contract 欄位、缺 DBML 表、缺 stub policy 等）→ 累積 CiC 便條紙寫入 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，**STOP** 並提示回 `/aibdd-plan`；**禁止**就地補洞、**禁止**自生 step pattern 讓下游 bypass。

## PRINCIPLE: 真相格式委派 specifier skills

- `.feature` 之 Scenario／Scenario Outline + Examples 填空之**唯一合法管道**為 **`DELEGATE /aibdd-form-feature-spec`** with `mode=example-fill`。一個 feature path 為一次 DELEGATE；payload 含 `target_path`、`reasoning`（本輪推理 bundle 切片）、`atomic_rule_ids`。
- 本 skill **不得**手寫任何 `.feature` 任一行；只負責 DERIVE caller payload 並 `DELEGATE`。違者視為 ownership 違規，**立即 STOP**。

## PRINCIPLE: 靜默累積 CiC 便條紙，不呼叫 clarify-loop

- 本 skill 為背景推理階段；任何上游真相缺洞、Outline 合併歧義、Example 維度無法填滿等疑處，**一律**累積為 CiC 便條紙寫入 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`（kind ∈ `GAP`／`ASM`／`BDY`／`CON`，每條含 `where`／`text`），由下游 `/speckit.clarify` 下一輪消化。
- **禁止** inline 向使用者提問；**禁止** DELEGATE `/clarify-loop`。本原則與 plan/discovery 不同——上述兩 skill 需互動澄清，本 skill 一律靜默。

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

0. 在 CWD 底下 grep 搜尋 `**/arguments.yml` 檔案，做 parameters binding for all following phases，這些參數後續每一 phase 都會用到。此檔案一定存在，如不存在請直接停止執行，向使用者回報：「我在 ${CWD} 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff、/aibdd-discovery、/aibdd-plan 了？」

1. EXECUTE the sub-sop: `01-bind-and-load/SOP.md`

2. EXECUTE the sub-sop: `02-classify-rule/SOP.md`

3. EXECUTE the sub-sop: `03-enumerate-data/SOP.md`

4. EXECUTE the sub-sop: `04-plan-scenario/SOP.md`

5. EXECUTE the sub-sop: `05-delegate-and-quality-gate/SOP.md`

6. 和用戶說道（可使用不同詞彙但維持語意）：「OK /aibdd-spec-by-example-analyze 完成。本輪 atomic rules 已展成 Scenario／Scenario Outline + Examples，coverage matrix 已寫入 package；語意 verdict 已寫入 `${PLAN_REPORTS_DIR}/bdd-analyze-quality.md`（deterministic check 腳本已自本 skill 移除，不再強制執行）。{若有 CiC 便條紙：『尚有 N 張便條紙待 /speckit.clarify 釐清，路徑：${PLAN_REPORTS_DIR}/bdd-analyze-cic.md。』否則省略}如沒問題，可以執行 /aibdd-tasks，正式進入 task list 拆解。」
