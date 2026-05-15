# AIxBDD - Discovery

嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之專案／規格樹內（相對路徑自 **`CWD`** 解析；本檔所列 `${SPECS_ROOT_DIR}`、`${CURRENT_PLAN_PACKAGE}`、`${PLAN_REPORTS_DIR}`、`${TRUTH_*}` 等皆以 **`CWD`** 為錨。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: 澄清只委派 clarify-loop

- 凡須向使用者做**結構化澄清**，Phase **02／03** 僅用 **一行 `DELEGATE /clarify-loop`**，並帶 **`delegated_intake`**（形狀與展開規則見 sibling [`clarify-loop/references/intake-expanders/aibdd-discovery.md`](../clarify-loop/references/intake-expanders/aibdd-discovery.md)）。**禁止**在子 SOP 內重複敘述 payload 組裝或 **unsupported** 落盤步驟；**禁止**以聊天逐題代替。
- 若 `/clarify-loop` 回傳 **`completed`**：執行者依回傳合流 **`${PLAN_SPEC}`**／相關 **`${ACTIVITIES_DIR}`**／**`${FEATURE_SPECS_DIR}`**／**`${PLAN_REPORTS_DIR}/discovery-sourcing.md`**（一句話義務即可，細節看回傳）。

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。

2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-sourcing-and-packaging/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**Tier 0 範例**（語意範本；實務請用 **`TODOCREATE`／`TASKCREATE`（或等效）** 建立對應任務，結構對齊即可。`<NN-subsop>` 為占位符，以本檔 `# SOP` 實際路徑取代）：

```markdown
- [ ] (1) 展開並執行至完成：`01-<NN-subsop>/SOP.md`（細項見下）。
- [ ] (2) 展開並執行至完成：`02-<NN-subsop>/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-<NN-subsop>/SOP.md`。
```

**進入 (1) 後**才把 (1) 拆成 Tier 1；其餘 phase 在 Tier 0 維持單列：

```markdown
- [ ] (1) 展開並執行至完成：`01-<NN-subsop>/SOP.md`。
    - [ ] (1-1) READ：`01-<NN-subsop>/SOP.md` 步驟 0 …
    - [ ] (1-2) WRITE：`<該步授權產出路徑>`
    - [ ] (1-3) 依該 `SOP.md` 其餘編號步驟續跑 …
- [ ] (2) 展開並執行至完成：`02-<NN-subsop>/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-<NN-subsop>/SOP.md`。
```

**(1)** 的子項全部完成後，以 **`TODOCREATE`／`TASKCREATE`（或等效）** 將 Tier 0 之 **(1)** 標為完成，再對 **(2)** 重複「展開 → 跑完」，依序往後。**未完成當前 phase** 前，**不要**為後續 phase 預開檔案層級的細項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. 在 CWD 底下 grep 搜尋 `**/arguments.yml` 檔案，做 parameters binding for all following phases，這些參數後續每一 phase 都會用到。此檔案一定存在，如不存在請直接停止執行，向使用者回報：「我在 ${CWD} 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」

1. EXECUTE the sub-sop: `01-sourcing-and-packaging/SOP.md`

2. EXECUTE the sub-sop: `02-activity-analyze/SOP.md`

3. EXECUTE the sub-sop: `03-atomic-rules-analyze/SOP.md`

4. 和用戶說道（可使用不同詞彙但維持語意）：「OK 基本上 /aibdd-discovery 所有分析步驟都完成了，如沒問題，可以執行 /aibdd-plan，來正式進入內外部邊界介面的規劃以及 DSL 的設計。」

