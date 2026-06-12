---
name: aibdd-spec-by-example-analyze
description: "AIBDD Spec by Example Analyze SOP。"
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Spec by Example Analyze

嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之專案／規格樹內（相對路徑自 **`CWD`** 解析；本檔所列 `${SPECS_ROOT_DIR}`、`${CURRENT_PLAN_PACKAGE}`、`${FEATURE_SPECS_DIR}`、`${TRUTH_FUNCTION_PACKAGE}`、`${PLAN_REPORTS_DIR}` 等皆以 **`CWD`** 為錨。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE / DELEGATE / TRIGGER 明確標注的產出物。
- 各 sub-SOP 可在其**明確擁有的 `.feature` 區塊**內做 idempotent inline update（例如 `01` 的 Example skeleton、`02` 的 `# candidates:`）；不得改寫其他 phase 已落地決策或 upstream accepted truth。
- 【嚴禁】**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。
2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／`DELEGATE`／`TRIGGER` 工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: Clarify gate is blocking

1. 任何 sub-SOP 只要回傳 `$questions` 或 `$NEED_TO_CLARIFY`，外層 orchestrator **必須**先 DELEGATE `/clarify-loop` 完成澄清，再只重跑受影響的 worker。
2. 在對應的 clarify gate 尚未清空前，該 phase 不算完成；頂層 SOP 也不得往後推進，更不得對用戶宣告 `/aibdd-spec-by-example-analyze` 完成。
3. worker 只負責分析與寫檔；使用者互動一律由外層 phase 負責。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-bind-and-load/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE`／`DELEGATE`／`TRIGGER` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`）；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**(1)** 的子項全部完成後，以 **`TODOCREATE`／`TASKCREATE`（或等效）** 將 Tier 0 之 **(1)** 標為完成，再對 **(2)** 重複「展開 → 跑完」，依序往後。**未完成當前 phase** 前，**不要**為後續 phase 預開檔案層級的細項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. 在 CWD 底下 grep 搜尋 `**/arguments.yml` 檔案，做 parameters binding for all following phases，這些參數後續每一 phase 都會用到。此檔案一定存在，如不存在請直接停止執行，向使用者回報：「我在 ${CWD} 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff、/aibdd-flows-specify、/aibdd-rules-specify、/aibdd-plan 了？」

1. BIND feature files——TRIGGER impact matrix query（只取本輪確定要改寫的 `.feature`：`update`／`add`），將 stdout JSON 之 `entries` 物化成 `${SCOPED_FEATURE_PATHS}`；後續所有 sub-SOP 一律沿用 `${SCOPED_FEATURE_PATHS}`。
   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
     --matrix ${IMPACT_MATRIX_YML} query \
     --suffix .feature \
     --change-type update \
     --change-type add
   ```
   物化規則：對每一筆 `entries[].path`，若未以 `${SPECS_ROOT_DIR}/` 開頭，則 prefix `${SPECS_ROOT_DIR}/`；去重後排序。
   若 matrix 缺失、`ok` 為 false、或物化後 `${SCOPED_FEATURE_PATHS}` 為空，STOP 並回報本輪無 mutable feature scope。

2. EXECUTE `01-example-form-lock/SOP.md`

3. EXECUTE `02-handler-retrieval/SOP.md`

4. EXECUTE `03-dsl-arrangement/SOP.md`

5. EXECUTE `04-parameter-instantiation/SOP.md`

6. 當且僅當 clarify gate 都已清空，和用戶說道（可使用不同詞彙但維持語意）：「OK /aibdd-spec-by-example-analyze 完成。本輪 `${SCOPED_FEATURE_PATHS}` 內 atomic rules 已展成 Scenario／Scenario Outline + Examples，並完成 Given／When／Then 的 DSL arrangement 與 canonical exemplar instantiation（唯一產物為原地改寫之 `.feature`）。

嗯，本步完成後即可直接執行 /aibdd-tasks！」
