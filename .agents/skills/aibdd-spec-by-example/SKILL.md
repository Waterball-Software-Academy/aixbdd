---
name: aibdd-spec-by-example
description: "AIBDD spec-by-example：對 .feature 內已分類的 atomic Rule 套 4-pattern 模板補完 Example。"
metadata:
  user-invocable: true
  source: project-level
---

# AIBDD - Spec-By-Example（atomic rule expansion）

依本 SKILL.md 進行：以 `.feature` 檔內已有的 atomic Rule（已含 pattern 標籤）為輸入，對每條 Rule 補完一個符合對應 pattern 的 Example。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP 所有經授權產生或修改的 artifact，一律落在當次執行的工作目錄 `CWD` 所涵蓋之專案／規格樹內（相對路徑自 `CWD` 解析；本檔所列 `${SPECS_ROOT_DIR}`、`${FEATURE_SPECS_DIR}`、`${TRUTH_FUNCTION_PACKAGE}` 等皆以 `CWD` 為錨）。
- 【嚴禁】把應屬本流程的產物寫到 `CWD` 外的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP 唯一允許產生或修改的 artifact，只能來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物。
- 【嚴禁】除上述 target 外，其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。

## PRINCIPLE: STRICT SOP

1. 依序不漏步：自底下列 SOP 逐一執行；每做一步，在訊息中明示該步編號。

2. 限縮延長推理：僅當 sub-SOP 當步明文標示須 `THINK / REASONING` 時，才拉長內省與推演；否則以最直接可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 conversation compact（對話摘要壓縮）之後，執行者仍要靠同一套待辦還原：目前卡在哪個 phase，該 phase 內細項又到哪一格。底下為兩層約定：外層只列 phase，進入該 phase 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- 必須工具化：Tier 0／Tier 1 對應的勾選項，要以執行環境提供的任務／待辦建立與更新能力實體化（例如 `TODOCREATE`、`TASKCREATE` 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP 當下就建好清單並隨步驟推進更新狀態。禁止只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- Tier 0（phase）：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-scan-and-classify/`）。這一層的勾選語意是「該 phase 的細項已全部展開且依 `SOP.md` 跑完」。
- Tier 1（phase 內細項）：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡第一層編號步驟拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；進入該 phase 時以 `TODOCREATE`／`TASKCREATE`（或等效） 補齊子項。

Tier 0 範例（語意範本；實務請用 `TODOCREATE`／`TASKCREATE`（或等效） 建立對應任務，結構對齊即可）：

```markdown
- [ ] (1) 展開並執行至完成：`01-scan-and-classify/SOP.md`（細項見下）。
- [ ] (2) 展開並執行至完成：`02-expand-each-rule/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-validate-and-finalize/SOP.md`。
```

進入 (1) 後才把 (1) 拆成 Tier 1；其餘 phase 在 Tier 0 維持單列：

```markdown
- [ ] (1) 展開並執行至完成：`01-scan-and-classify/SOP.md`。
    - [ ] (1-1) RESOLVE arguments：`01-scan-and-classify/SOP.md` 步驟 0 …
    - [ ] (1-2) WRITE：`<該步授權產出路徑>`
    - [ ] (1-3) 依該 `SOP.md` 其餘編號步驟續跑 …
- [ ] (2) 展開並執行至完成：`02-expand-each-rule/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-validate-and-finalize/SOP.md`。
```

(1) 的子項全部完成後，以 `TODOCREATE`／`TASKCREATE`（或等效） 將 Tier 0 之 (1) 標為完成，再對 (2) 重複「展開 → 跑完」，依序往後。未完成當前 phase 前，不要為後續 phase 預開檔案層級的細項。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. RESOLVE arguments（與 `/aibdd-discovery` sub-SOP 同款）——在 `${CWD}`（shell working directory）執行 sibling resolver，固定讀取 `${AIBDD_ARGUMENTS_PATH}`（即 `.aibdd/arguments.yml`）。將 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 skill 並把 stderr 透傳給用戶；若訊息為 arguments.yml not found，改以語意回報：「我在 ${CWD} 底下找不到 `.aibdd/arguments.yml`，你是否已經執行過 /aibdd-kickoff 了？」禁止以 workspace grep／Glob 取代本步的 READ 或 resolver。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

   0.1 IF caller 以 `@` 或明確路徑指定 target `.feature` 檔：DERIVE `$function_package_slug`（該檔位於 `${TRUTH_BOUNDARY_PACKAGES_DIR}/NN-<slug>/features/` 下）→ 在記憶體 override `$TRUTH_FUNCTION_PACKAGE` 與 `$FEATURE_SPECS_DIR`；禁止改寫 `arguments.yml`。若未指定 target，且 resolver 輸出之 `TRUTH_FUNCTION_PACKAGE` 仍含 `<<` 借位：DELEGATE `/clarify-loop` 詢問本次 function package 或 feature 路徑後再續跑。

1. EXECUTE the sub-sop: `01-scan-and-classify/SOP.md`

2. EXECUTE the sub-sop: `02-expand-each-rule/SOP.md`

3. EXECUTE the sub-sop: `03-validate-and-finalize/SOP.md`

4. 和用戶說道（可使用不同詞彙但維持語意）：「OK 本 package 的 atomic Rule 都已補完 Example。若無問題，可以執行 `/aibdd-plan` 來產出 API Plan 或 Data Plan。」
