---
name: aibdd-reconcile
description: Reconcile one AIBDD plan package from the earliest affected planner by archiving current package artifacts, classifying trigger impact against planner relevance, cascading the reconcilable planners, and recording one session narrative. TRIGGER when user, evaluator, or worker reports an upstream artifact defect or requirement change against an existing plan package. SKIP when the request is to rewind filesystem state, regenerate tasks/implement directly, or modify non-AIBDD product code.
metadata:
  user-invocable: true
  source: project-level dogfooding
  skill-type: planner
---

# aibdd-reconcile

把一個既有的 plan package 重新對齊：找出最上游被影響到的 planner，把目前 package 內的產物整批歸檔保存，從那個 planner 開始往下游重跑，最後留下一份「這次為什麼要重對齊」的紀錄。

嚴格遵照底下 PRINCIPLE 來執行 SOP。

## PRINCIPLE: 只對齊這四個 planner

- 本 skill 只會分類與重跑這四個 planner，固定上下游順序為 `aibdd-flows-specify` → `aibdd-rules-specify` → `aibdd-plan` → `aibdd-spec-by-example-analyze`。
- 不分類、不重跑 `/aibdd-tasks` 與 `/aibdd-implement`；它們在本流程結束後一律視為過期，須由使用者另外重跑。
- 不回捲整個 workspace 到舊 checkpoint，那是 `/aibdd-rewind` 的職責。
- 不自行改動任何非 AIBDD 的產品程式碼，也不越過各 planner 的 ownership 邊界。

## PRINCIPLE: 歸檔語意

- 開一個新的 reconcile session 時，把目標 plan package 根目錄下「除了 `archive/` 以外」的每一個 entry，整批搬進 `archive/<session_id>/`。
- `archive/` 永遠不會被歸檔進它自己；不挑檔、不做例外保留；新一輪一律從乾淨的 package 根目錄開始。
- 不刪除任何既有 `archive/` 歷史，也不清理舊 session。

## PRINCIPLE: 同一輪只開一個 session

- 若目標 package 已有一個進行中的 session（`archive/.reconcile-active.json` 存在），不開新歸檔，改成把這次的新 trigger 併進同一個 session。
- 併入後重新分類最上游 planner：若新的最上游比目前進度更上游，就從新的最上游重跑；否則沿目前進度繼續。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 所有產出（歸檔搬移、`RECONCILE_RECORD.md`、active session 狀態檔）一律落在目標 plan package 樹內，相對路徑自 `CWD` 與 `.aibdd/arguments.yml` 解析。
- 嚴禁把產物寫到目標 plan package 之外的任意絕對路徑。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。

2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-bind-target-and-session/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. BIND 本次 reconcile 的三個輸入，並把綁定結果 EMIT 給用戶：
   1. arguments 路徑：若 caller payload 帶有 `arguments_path` 就用它，否則用 `CWD` 下的 `.aibdd/arguments.yml`。
   2. 目標 plan package：若 caller payload 帶有 `plan_package_path` 就用它，否則取 skill ARGUMENTS 的第一個位置參數。
   3. trigger 描述：若 caller payload 帶有 `trigger_description` 就用它，否則取 skill ARGUMENTS 去掉 package 路徑後、被引號包住的其餘文字（即本次「為什麼要重對齊」的缺陷或需求說明）。

1. EXECUTE the sub-sop: `01-bind-target-and-session/SOP.md`

2. EXECUTE the sub-sop: `02-classify-and-open-session/SOP.md`

3. EXECUTE the sub-sop: `03-archive-snapshot/SOP.md`

4. EXECUTE the sub-sop: `04-cascade-planners/SOP.md`

5. EXECUTE the sub-sop: `05-finalize-and-report/SOP.md`
