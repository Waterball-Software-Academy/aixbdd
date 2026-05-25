---
description: 專案初始化引導；支援 Python E2E、Java E2E 兩個 stack，收集唯一 TLB 名稱，產出 arguments.yml、boundary.yml、component-diagram.class.mmd、specs/shared/dsl.yml 與 boundary skeleton。TRIGGER when 使用者說 kickoff、初始化專案、建 arguments.yml、新專案設定。SKIP when 需要多 TLB、Vue/Svelte 等其他 frontend 框架、Unit Test only、Mobile，或其他尚未支援的 stack。
metadata:
  skill-type: planner
  source: project-level
  user-invocable: true
name: aibdd-kickoff
---

# aibdd-kickoff

Initialize an AIBDD project by deriving stack-aware config and writing one top-level boundary truth skeleton, including boundary shared DSL seed at `${BOUNDARY_SHARED_DSL}`.

嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。

2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-ask-config/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**Tier 0 範例**：

```markdown
- [ ] (1) 展開並執行至完成：`01-ask-config/SOP.md`（細項見下）。
- [ ] (2) 展開並執行至完成：`02-execute-layout/SOP.md`。
```

**進入 (1) 後**才把 (1) 拆成 Tier 1；其餘 phase 在 Tier 0 維持單列：

```markdown
- [ ] (1) 展開並執行至完成：`01-ask-config/SOP.md`。
    - [ ] (1-1) DERIVE：判定 `$action`（resume / restart / cancel / new）。
    - [ ] (1-2) WRITE：`${PLAN_PATH}`（File First — 出題前先存檔）。
    - [ ] (1-3) DELEGATE：`/clarify-loop` 取得答案。
    - [ ] (1-4) UPDATE：`${PLAN_PATH}` writeback 答案。
- [ ] (2) 展開並執行至完成：`02-execute-layout/SOP.md`。
```

**(1)** 的子項全部完成後，將 Tier 0 之 **(1)** 標為完成，再對 **(2)** 重複「展開 → 跑完」。**未完成當前 phase** 前，**不要**為後續 phase 預開檔案層級的細項。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: File First

- Interactive 路徑下，所有對 user 的提問**必須**走 **write → ask → write back** 三段式：問題的 SSOT 是 `KICKOFF_PLAN.md`，**禁止**在 file 之外另起一份問題集。
- **Write Questions**：`01-ask-config/SOP.md` 必須先把整批 Q1–Q4 含 prompt / options / context 完整寫進 `${PLAN_PATH}`，檔案落地後才允許出題。
- **Ask via Clarify-Loop**：從**已寫入的檔案**讀回題目組 batch payload，透過 `DELEGATE /clarify-loop` 詢問；**禁止** executor 自己在 chat 直接列題或自己 ASK。
- **Write Back Answers**：user 答完**必須**把答案 writeback 進**同一份** `${PLAN_PATH}`，每題狀態變 `answered` 後才允許進 `02-execute-layout/`。
- Non-interactive 路徑（`${NON_INTERACTIVE}=true`）跳過 `${PLAN_PATH}`；`$decisions` 直接由 default 推得，不走 File First。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. DERIVE caller payload bindings：
   - `${PROJECT_ROOT}` ← caller payload 或 current workspace 推算；若無法解析則向 user 告知並 STOP。
   - `${NON_INTERACTIVE}` ← caller payload 帶 `non_interactive: true` 或 `defaults_profile: happy-path` 或 headless sandbox（如 `.tests/<scenario>/before` 運行）任一成立則 true，否則 false。**此 flag 由 caller 注入；executor 禁止對 user 詢問「要走 interactive 還是 happy-path」**。
   - `${PLAN_PATH}` = `${PROJECT_ROOT}/KICKOFF_PLAN.md`。

1. EXECUTE the sub-sop: `01-ask-config/SOP.md`

2. EXECUTE the sub-sop: `02-execute-layout/SOP.md`
