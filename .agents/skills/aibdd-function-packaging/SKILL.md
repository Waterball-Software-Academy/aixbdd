---
name: aibdd-function-packaging
description: >
  當 reconcile 校準 impact matrix 後、要依本批次需求重新對齊各 function package 範圍時觸發。校正 `function-packaging.md` 把每個受牽動的 function package 標記為 `added` 或 `related`，並為 `added` 的 package 建立目錄。
metadata:
  user-invocable: true
  source: project-level
  skill-type: planner
---

# AIxBDD - Function Packaging

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 sub-SOP（phase），phase 中每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許調用工具產生或修改的 artifact，只能來自下述 SOP 中明確標注 CREATE、WRITE、UPDATE 的步驟；impact matrix 僅供讀取，本 skill 不寫入。

## PRINCIPLE: slug 命名規則

當本批次需求要開一個全新 function package 時，其落地 filesystem 的 function package 名（`NN-<slug>`）之 `<slug>` 主體，一律以專案規格語系（`arguments.yml` 的 `PROJECT_SPEC_LANGUAGE`）並遵守以下規則書寫。

- 技術名詞（API field、DSL token、operationId、domain acronym 如 CRM／SOP／API／OAuth）可保留英文原文；其餘 slug body 不得整段翻成英文。
- 落地 filesystem 的 slug 須 Windows-safe，不得含 \ / : * ? " < > | 及結尾空白或點號。
- 嚴禁以 romanization（漢語拼音／注音／粵拼）、kana、romaji 等 transliteration 充當「規避該語系字元」的 fallback；slug 必須讀得懂、可直接還原為該語系文字。
- 語系為 zh-hant／zh-hans：以該字形書寫，例 `packages/01-會員登入`；不得寫成 romanization（`packages/01-hui-yuan-deng-ru`）或無此需求的整段英譯（`packages/01-member-login`）。
- 語系為 en-us：slug 以英文 kebab-case 撰寫，例 `packages/01-member-login`。
- 語系為 ja-jp：以日文書寫，禁止以 romaji 取代漢字／假名；語系為 ko-kr：以韓文（Hangul）書寫，禁止以 romaja 取代。
- 禁止無理由中英混拼的 slug（如 `packages/01-會員-login`，除非含上述技術 token 例外）。
- 若專案規格語系缺失或無法判斷，不得自行 fallback 為英文或 romanization，須向使用者釐清。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號項目；每做一步，在訊息中明示該步編號。
- 每一個 sub-SOP（phase）、sub-SOP step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify-loop` 等待回覆、以及最後一步的結尾報告。

## PRINCIPLE: 限縮推理

- 僅當 sub-SOP step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、CREATE、WRITE、UPDATE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以兩層待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前所有待辦與進度：目前正在進行的 sub-SOP（phase）和細項 sub-SOP step。外層只列 sub-SOP（phase），進入該 phase 再把該 phase 第一層編號步驟拆成子項，尚未開始的 phase 不必預先展開。

- Tier 0：sub-SOP（phase），對應本檔 `# SOP` 最外層每一項；勾選代表該 phase 的細項已全部展開並依該 phase `SOP.md` 跑完。
- Tier 1：phase 內細項，對應該 phase `SOP.md` 裡第一層編號步驟拆解出的動作，進入該 phase 時才補齊子項。編號方式為 (phase 序)、(phase 序-step 序)。
- 呼叫工具維護待辦清單：勾選 Tier 0、Tier 1 要使用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具）；嚴禁只在對話列點、不經工具建立的上下文待辦。

Tier 0 範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 展開並執行至完成：aibdd-function-packaging/01-bind-inputs/SOP.md。
- [ ] (2) 展開並執行至完成：aibdd-function-packaging/02-reason-packaging/SOP.md。
- [ ] (3) 展開並執行至完成：aibdd-function-packaging/03-apply-packaging/SOP.md。
```

進入某 phase 後才把它拆成 Tier 1，其餘 phase 在 Tier 0 維持單列。

Tier 1 範例（以 phase 2 為例）：

```markdown
- [ ] (1) 展開並執行至完成：aibdd-function-packaging/01-bind-inputs/SOP.md。
- [ ] (2) 展開並執行至完成：aibdd-function-packaging/02-reason-packaging/SOP.md。
    - [ ] (2-1) 步驟 1：解析 arguments。
    - [ ] (2-2) 步驟 2：載入校正基準。
    - [ ] (2-3) 步驟 3：識別 impact matrix 標記的既有 package。
    - [ ] (2-4) 步驟 4：判定全新需求的 package 歸屬。
    - [ ] (2-5) 步驟 5：梳理決策與 rationale。
- [ ] (3) 展開並執行至完成：aibdd-function-packaging/03-apply-packaging/SOP.md。
```

某 phase 的子項全部完成後，把 Tier 0 該項標為完成，再對下一個 phase 重複展開與執行，依序往後；未完成當前 phase 前，不為後續 phase 預展開 Tier 1。

# SOP

僅閱讀當前執行 phase 的 SOP.md，嚴禁提早閱讀後續 phase 文件，避免延遲起始體驗。

1. 綁定輸入: EXECUTE phase `aibdd-function-packaging/01-bind-inputs/SOP.md`。

2. 推理 function packages 校正: EXECUTE phase `aibdd-function-packaging/02-reason-packaging/SOP.md`。

3. 落地 function packages 校正: EXECUTE phase `aibdd-function-packaging/03-apply-packaging/SOP.md`。

4. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-function-packaging 已依本批次需求校正 `function-packaging.md`：新開的 package 已建立目錄並標記 `added`、其餘受牽動的既有 package 標記 `related`。下面逐一列出本批次 `added`／`related` 的 package：<逐一列出>。接著請執行 /aibdd-flows-specify，在這些 package 內展開 UAT flow 與 feature。」
