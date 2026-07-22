---
description: 專案初始化引導；支援 python_e2e / java_e2e / nextjs_playwright 三種 stack，收集 stack / 規格語言 / service 名 / 是否安裝 aibdd-spectrum，產出 arguments.yml、boundary.yml、component-diagram.class.mmd、isa.yml 與 boundary skeleton。TRIGGER when 使用者說 kickoff、初始化專案、建 arguments.yml、新專案設定。SKIP when 需要多 TLB、Unit Test only、Mobile，或其他尚未支援的 stack。
metadata:
  skill-type: planner
  source: project-level
  user-invocable: true
name: aibdd-kickoff
---

# aibdd-kickoff

Initialize an AIBDD project：依 stack 收集配置、產生單一 top-level boundary truth skeleton（含 `${BOUNDARY_ISA}` 的 boundary isa seed）。嚴格遵照 Purpose 的紀律執行 SOP。

# Purpose

把「新專案初始化」收斂成一條 phase-by-phase SOP：取得 caller context → File First 收集配置決策 → 跑純複製 script 鋪出 boundary skeleton → 填 stack-aware 配置 → 驗證清理 → 回報並導向 `/aibdd-auto-starter`。貫穿全程的幾條紀律（方針優先於細節，逐步執行時恆常遵守）：

- **嚴格依序**：按 Phase 順序逐一執行，每步在訊息中講清楚自己在做哪個 Phase 哪一步；只在當步真的需要權衡時才深想，否則直接動手，省掉與當步無關的鋪陳。執行到哪讀到哪，不提早翻後續 Phase 的細節與 reference。
- **長流程待辦**：流程跨多輪、會被 conversation compact，得靠待辦還原進度：用宿主的待辦工具建清單、隨步推進，別只在對話裡口頭記；外層每個 Phase 一項，進到某 Phase 才把它的步驟展開成子項。
- **只動該動的**：只有各步明講要產出／修改的檔才准碰；過程中讀到、查到的其他路徑只作判斷依據，不得順手建立或補骨架。
- **File First（僅互動路徑）**：所有對 user 的提問走 **寫 → 問 → 回寫** 三段式：題目與答案的唯一真相是 `KICKOFF_PLAN.md`，先把題目寫進檔再問、答完回寫進同一份檔；提問一律委派 `/clarify`，executor 不自己在對話裡列題。非互動模式整個跳過 File First，配置直接採 default。

# SOP

### Phase 1 — 取得 caller context

1. **(read)** 取得專案根目錄（從 caller payload，或推算當前 workspace）；取不到就告知 user 並停止。互動模式下，這次 kickoff 的問答都記在根目錄的 `KICKOFF_PLAN.md`。
2. **(think)** 判斷這次是不是非互動模式——這個旗標由 caller 注入，絕不反問 user。
   - 請嚴格遵守 `rules/non-interactive-from-caller.md` 來執行此步驟。

### Phase 2 — 收集配置（File First：寫 → 問 → 回寫）

1. **(think)** 非互動模式：直接採 default 決策（stack=python_e2e、規格語言 zh-hant、service 名 backend、放 repo root；headless 要別的 stack 由 caller payload 帶 `stack:` 覆寫），跳過 File First，直接進 Phase 3。
2. **(delegate)** 互動模式且 `KICKOFF_PLAN.md` 已存在：問 user 要接續、重做、還是取消，經 /clarify 出題；取消就停。
   - delegate to SKILL /clarify
3. **(write)** 要新建問卷時：依 `assets/questions/` 第一輪三題與外殼 `assets/kickoff-plan.template.md`，渲染出 `KICKOFF_PLAN.md`（三題、答案欄留空；Q4／Q5 為條件式第二輪，於下方對應步驟才渲染）。
   - 請嚴格遵守 `assets/kickoff-plan.template.md` 來執行此步驟。
   - 請嚴格遵守 `assets/questions/q1-tech-stack.template.md` 來執行此步驟。
   - 請嚴格遵守 `assets/questions/q2-project-spec-language.template.md` 來執行此步驟。
   - 請嚴格遵守 `assets/questions/q3-backend-service-name.template.md` 來執行此步驟。
4. **(delegate)** 一次問完第一輪三題（stack／規格語言／service 名），經 /clarify；回答格式見各 question template 的 reply token 與外殼的 Batch Reply Format。
   - 請嚴格遵守 `assets/kickoff-plan.template.md` 來執行此步驟。
   - delegate to SKILL /clarify
5. **(write)** 把答案回寫 `KICKOFF_PLAN.md`、每題標 answered。任何一題模糊、重複或缺漏，就標 unresolved、告知 user 並停止——不要猜值硬填。
   - 請嚴格遵守 `rules/answer-resolution-gate.md` 來執行此步驟。
6. **(delegate)** 第二輪條件式提問——依答案**逐一檢查兩個檢查點**，把適用的題以一次 `/clarify` 問完回寫：
   - 檢查點 1（先檢查 `type`）：`type: web-service` → 納入 Q4 data schema 格式，渲染 `{{Q4_RECORD}}`；否則跳過 Q4。
     - 請嚴格遵守 `assets/questions/q4-data-schema-format.template.md` 來執行此步驟。
   - 檢查點 2（再檢查 `stack`）：`stack: java_e2e` → 納入 Q5 是否安裝 aibdd-spectrum，渲染 `{{Q5_RECORD}}`；否則跳過 Q5。
     - 請嚴格遵守 `assets/questions/q5-install-spectrum.template.md` 來執行此步驟。
   - 兩檢查點皆不符 → 整步跳過。
   - 請嚴格遵守 `rules/answer-resolution-gate.md` 來執行此步驟。
   - delegate to SKILL /clarify

### Phase 3 — 產生 boundary skeleton

1. **(run)** 把這批決策交給 `assets/scripts/kickoff_layout.py` 跑出 boundary skeleton（用決策檔傳入，跑完清掉暫存）；失敗就轉述錯誤並停。從它的輸出取得 boundary codebase 根目錄與 isa 路徑，供後續步驟使用。
   - 請嚴格遵守 `assets/scripts/kickoff_layout.py` 來執行此步驟。

### Phase 4 — 填 stack-aware 配置

1. **(write)** 依下方 stack 查表，把對應的 per-stack tail 接到 `arguments.yml` 末尾，並填掉 `arguments.yml` 與 `boundary.yml` 裡的通用 placeholder（service id、boundary role／type／description）；若 codebase 指定了子目錄，一併設進 `arguments.yml`。

| stack | tail 模板 | role | type | description（接在 service 名後） |
|---|---|---|---|---|
| `python_e2e` | `python-e2e` | `backend` | `web-service` | Python FastAPI backend service |
| `java_e2e` | `java-e2e` | `backend` | `web-service` | Java Spring Boot backend service |
| `nextjs_playwright` | `nextjs-playwright` | `frontend` | `web-app` | Next.js + Playwright frontend application |
2. **(write)** 把 boundary type 填進 component diagram 的 annotation。
   - 請嚴格遵守 `rules/mermaid-annotation-charset.md` 來執行此步驟。
3. **(write)** java_e2e：填好 Java base package。
   - 請嚴格遵守 `rules/java-base-package.md` 來執行此步驟。
4. **(write)** java_e2e：依 Q5 `install_spectrum` 決策，把 `arguments.yml` 的 `INSTALL_SPECTRUM`（佔位 `${KICKOFF_INSTALL_SPECTRUM}`）回填為 `true`（要裝）或 `false`（不裝）；不可留下未替換的佔位。其他 stack 的 tail 無此鍵，略過——即使 Q5 答 yes 也保持乾淨 pom。
   - 下游 `/aibdd-auto-starter` 僅在此值為 `true` 且 variant 為 `java-e2e` 時，於 pom.xml 疊加 specformula 依賴與 specformula-dsl plugin。
5. **(write)** 規格語言不是 zh-hant 時：切換語系設定。
   - 請嚴格遵守 `rules/language-single-source.md` 來執行此步驟。
6. **(write)** `data_schema_format ∈ { postgresql, mysql, mssql }` 時（僅 `type: web-service` 會有此值）：把 `profile_overrides.state_specifier` 寫進 `boundary.yml`；`dbml` 不寫。
   - 請嚴格遵守 `rules/ddl-state-specifier-override.md` 來執行此步驟。

### Phase 5 — 驗證 + 清理

1. **(write)** 收尾：確認 `arguments.yml`／`boundary.yml`／component diagram 三檔都沒有殘留的 `${KICKOFF_` placeholder（有就指出位置並停）、isa.yml 檔存在；都過了就刪掉 `KICKOFF_PLAN.md` 暫存檔。

### Phase 6 — 回報

1. **(write)** 向 user 回報：「Kickoff 已完成。已建立：<列出產出的 artifact，含 isa.yml>。下一步，來建立專案骨架吧，請直接使用 /aibdd-auto-starter，或是告訴我『繼續』。」
