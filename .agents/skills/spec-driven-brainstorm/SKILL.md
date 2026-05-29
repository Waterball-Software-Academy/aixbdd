---
name: spec-driven-brainstorm
description: "Spec-driven brainstorm SOP。"
metadata:
  user-invocable: true
  source: project-level
---

# Spec-Driven Brainstorm

引導 user 把對話式 ideation 逐步沉澱成 issue-organized `spec.md`；每輪自動推斷下一個應深入的 subsection；`spec.md` 永遠維持 absolute design — 無 hedging、無歷史脈絡、無 brainstorming variants 殘留。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之路徑（`${SPEC_FILE}`、`${ARCHIVE_DIR}/**` 皆以 **`CWD`** 為錨；本檔所列其他 `${VAR}` 同此原則）。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物（限於 `${SPEC_FILE}` 與 `${ARCHIVE_DIR}/**`）。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: spec.md 即 absolute design

- `${SPEC_FILE}` 內容**必為**當前所有 decision 與 fact 的單一真實；**禁止**保留猶豫脈絡（例：「之前考慮過 A 後來選 B」「先試試看 X 再決定」「PR #123 之後再補」「等下再聊」）、**禁止**保留已被覆寫的舊決議、**禁止**未經 archive 的 brainstorming variants。
- 任一輪 user 更新後，**必須**主動掃描並刪除被新決議蓋過、與新 fact 矛盾、已 archive 的內容；保留下來的每個句子都是 truth。
- User 即使以「問題形式」提出（例：「這樣可以嗎？」「你覺得呢？」），AI **必須**先把推導出的答案以「肯定式 fact」寫進 `${SPEC_FILE}` 對應 subsection；**禁止**在 `${SPEC_FILE}` 內留下 Q&A 形態、待釐清標記、TODO 註解。

## PRINCIPLE: Brainstorming 是拋棄式

- `## Brainstorming` subsection **僅在**「Problem Space 完成 → Solution 未拍板」之間於 `${SPEC_FILE}` 內存在；user 一旦選定方案，**必須**立刻將該 subsection 整段 archive 至 `${ARCHIVE_DIR}/<issue-slug>-brainstorm-<UTC-yyyymmddThhmmssZ>.md`，並從 `${SPEC_FILE}` 刪除該 subsection。
- **禁止**把多個候選方案的對照表保留在 `${SPEC_FILE}`；**禁止**在 `## Solution` 內回顧「為什麼選 X 而不是 Y」之類的決策脈絡（該脈絡屬已 archive 之 brainstorming）。

## PRINCIPLE: 一次只推進一個 subsection

- 每一輪 user 對話，本 skill **只更新**「目前 active 的 issue × subsection」一格；**禁止**在同一輪預先把後續 subsection（例：尚未進到 Examples 就先補 Examples）展開。
- subsection 遞進順序（progressive disclosure）固定為：`definition` → `problem-space` → `brainstorming` → `solution` → `examples` → `implementation` → `implementation-package-structure`；**僅當** user 明確或推得確認當前 subsection 完成時，才能推進下一個。
- 候選 subsection 並非每個都得寫進每個 issue；缺席合法，但**禁止**逆序新增（譬如先寫 Implementation 再回頭補 Definition）。

## PRINCIPLE: 澄清走批次提問，禁止逐題往返

- 凡須向 user 做結構化澄清，**統一以單一一次性批次提問彙整**（一次給多題、附選項；使用 host 提供之 `AskUserQuestion` 或等效互動工具）；**禁止**在同一輪以多次逐題往返聊天的方式詢問。
- 若同輪同時須提問且須更新 spec，先完成 spec 更新（phase 3 / 4），再於 phase 5 emit 該批次問題；**不得**為了「先問清楚」而跳過 phase 3 的 spec 寫入。

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下列 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。
2. **限縮延長推理**：僅當 sub-SOP 當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-spec-bind/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**Tier 0 範例**：

```markdown
- [ ] (1) 展開並執行至完成：`01-spec-bind/SOP.md`（細項見下）。
- [ ] (2) 展開並執行至完成：`02-input-classify/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-section-apply/SOP.md`。
- [ ] (4) 展開並執行至完成：`04-consistency-sweep/SOP.md`。
- [ ] (5) 展開並執行至完成：`05-next-prompt-elicit/SOP.md`。
```

**(1)** 的子項全部完成後，將 Tier 0 之 **(1)** 標為完成，再對 **(2)** 重複「展開 → 跑完」，依序往後。**未完成當前 phase** 前，**不要**為後續 phase 預開檔案層級的細項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. RESOLVE arguments —— 綁定 `${SPEC_DIR}`、`${SPEC_FILE}`、`${ARCHIVE_DIR}`：
   - `${SPEC_DIR}` 預設 = `CWD`；若 user 本輪訊息明指其他目錄，以 user 指定為準。
   - `${SPEC_FILE}` 預設 = `${SPEC_DIR}/spec.md`。
   - `${ARCHIVE_DIR}` 預設 = `${SPEC_DIR}/archive/`。

1. EXECUTE the sub-sop: `01-spec-bind/SOP.md`

2. EXECUTE the sub-sop: `02-input-classify/SOP.md`

3. EXECUTE the sub-sop: `03-section-apply/SOP.md`

4. EXECUTE the sub-sop: `04-consistency-sweep/SOP.md`

5. EXECUTE the sub-sop: `05-next-prompt-elicit/SOP.md`
