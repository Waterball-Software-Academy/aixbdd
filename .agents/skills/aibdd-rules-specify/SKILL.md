---
name: aibdd-rules-specify
description: "AIBDD Rules Specify SOP。為 /aibdd-flows-specify 產出的每個 rule-less `.feature` 骨架列舉 atomic rules（4 種類型前綴、單一主詞／單一條件、可指回需求原文），再跑 findings 分析（NEED_TO_FIX 就地修正、NEED_TO_CLARIFY 交 /clarify-loop）。TRIGGER when 使用者下 /aibdd-rules-specify、flows 完成後要為每個 feature 補驗收規則、或被 /aibdd-reconcile cascade 委派。SKIP when 尚無 `.feature` 骨架（請先 /aibdd-flows-specify）、或只是要為 atomic rule 補可跑 Example（那是 /aibdd-spec-by-example）。"
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Rules Specify

嚴格遵照底下 Principles 來執行 SOP。本 skill 接在 `/aibdd-flows-specify` 之後：為每個已萃取出的 rule-less `.feature` 骨架列舉 atomic rules，並對全部範疇內 feature 做疑慮分析（就地修正 or 交澄清）。完成後交棒 `/aibdd-spec-by-example` 為每條 atomic rule 補可跑 Example。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之專案／規格樹內（相對路徑自 **`CWD`** 解析；本檔所列 `${SPECS_ROOT_DIR}`、`${CURRENT_PLAN_PACKAGE}`、`${PLAN_REPORTS_DIR}`、`${TRUTH_*}` 等皆以 **`CWD`** 為錨。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物（本 skill 僅在既有 `.feature` 骨架內補 `Rule:` 與其補充說明，不新建 `.feature`、不建 dsl／contracts／data）。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。

2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-atomic-rules-analyze/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**Tier 0 範例**（語意範本；實務請用 **`TODOCREATE`／`TASKCREATE`（或等效）** 建立對應任務，結構對齊即可）：

```markdown
- [ ] (1) 展開並執行至完成：`01-atomic-rules-analyze/SOP.md`（細項見下）。
```

**進入 (1) 後**才把 (1) 拆成 Tier 1（本 skill 僅此一個 phase）：

```markdown
- [ ] (1) 展開並執行至完成：`01-atomic-rules-analyze/SOP.md`。
    - [ ] (1-1) READ：`01-atomic-rules-analyze/SOP.md` 步驟 0 …
    - [ ] (1-2) WRITE：`<該步授權產出路徑>`
    - [ ] (1-3) 依該 `SOP.md` 其餘編號步驟續跑 …
```

**(1)** 的子項全部完成即整份 `# SOP` 完成。**未完成當前 phase** 前，**不要**為當步授權範圍以外的動作預開細項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. 在 CWD 底下 grep 搜尋 `**/arguments.yml` 檔案，做 parameters binding for all following phases，這些參數後續每一 phase 都會用到。此檔案一定存在，如不存在請直接停止執行，向使用者回報：「我在 ${CWD} 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」

  0.1 解析 plan package 作為 $PLAN_PACKAGE_SLUG。arguments.yml 的 CURRENT_PLAN_PACKAGE 永遠保持 <<NNN-plan-slug>> 借位形態，並且 CURRENT_PLAN_PACKAGE 借位時一律以 $PLAN_PACKAGE_SLUG 為準，plan package 解析順位為：
    - 對話歷史已指名具體 NNN-<slug>（例：稍早曾經解析過 plan package、使用者點名 ${PLAN_PACKAGES_DIR}/NNN-<slug>、或「繼續／重跑 NNN 那包」這類指涉），並且 ASSERT ${PLAN_PACKAGES_DIR}/NNN-<slug>/ 存在於 CWD；路徑不存在則改走下方釐清。
    - 其餘情況不得自行判定，列出 ${PLAN_PACKAGES_DIR}/*/ 全部候選向使用者釐清，直接詢問是延續哪個既有 plan packages；取得回覆前 STOP，候選僅一個、甚至為空，也必須釐清；若使用者指名新建或是不存在的 plan packages，則 STOP 並提示使用者本 skill 必須基於既有 plan package 執行。

1. ASSERT 上游 `/aibdd-flows-specify` 產物存在（READ-ONLY；本步不補建、不改寫）：
   - `${PLAN_SPEC}`（`${CURRENT_PLAN_PACKAGE}/spec.md`）存在且含本輪需求敘事全文（atomic rule 須能指回此原文）。
   - `${FEATURE_SPECS_DIR}` 下**至少一份** `.feature` 骨架（含 `Feature:` 標題）。
   - 任一條件不成立 → STOP，向使用者回報：「尚未偵測到 flows 產物（spec.md／.feature 骨架），請先執行 /aibdd-flows-specify 再回來跑 /aibdd-rules-specify。」**不得**在本步順手建立 spec.md 或任何 `.feature`。

2. EXECUTE the sub-sop: `01-atomic-rules-analyze/SOP.md`

3. 和用戶說道（可使用不同詞彙但維持語意）：「OK，每個 Feature File 對應的 atomic rules 都列舉並收斂完了，你本次需求的所有規則已定義在各 `.feature` 上，系統複雜度與後續實作將由這些規則的驗收測試所驅動。如沒問題，可以執行 /aibdd-spec-by-example，為每條 atomic rule 補上可跑的 Example。」