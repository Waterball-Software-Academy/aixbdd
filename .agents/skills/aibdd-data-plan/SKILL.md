---
name: aibdd-data-plan
description: "AIBDD Data Plan SOP。聚焦以 Discovery 真相（spec.md／feature truth）派生並落地 persistent data schema（state）。先 bind-and-load 本 skill 所需上游真相，DERIVE state target_path 集合，DELEGATE boundary profile 宣告之 state_specifier.skill 寫入 ${DATA_DIR}，回寫 impact matrix，再跑 findings 分析。TRIGGER when 使用者下 /aibdd-data-plan、或只想單獨重做本輪 data schema。SKIP when CWD 下找不到 arguments.yml（請先 /aibdd-kickoff）、Discovery 真相未 accepted（請先 /aibdd-flows-specify、/aibdd-rules-specify），或本輪只需處理 operation contract（改用 /aibdd-api-plan）。"
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Data Plan

聚焦：把本輪 Discovery 真相中須穩定保存／驗證／追蹤的部分，從資料流動拆成 Domain Aggregate／Entity／Value-Object，並委派 boundary profile 宣告之 `state_specifier` 落地，獨立成可單跑的小 skill。嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: CWD 為產出錨點

- 本 skill **所有經授權產生或修改的 artifact**，**一律**落在當次執行的工作目錄 **`CWD`** 所涵蓋之專案／規格樹內（相對路徑自 **`CWD`** 解析；本檔所列 `${DATA_DIR}`、`${TRUTH_BOUNDARY_ROOT}`、`${IMPACT_MATRIX_YML}`、`${CURRENT_PLAN_PACKAGE}` 等皆以 **`CWD`** 為錨）。
- 【嚴禁】把應屬本流程的產物寫到 **`CWD` 外**的任意絕對路徑，或以「方便」為由落到未載明於本 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP **唯一允許產生或修改**的 artifact，**只能**來自下述 SOP 中透過 DELEGATE（specifier 寫 `${DATA_DIR}`）與 impact matrix `upsert`／`validate` 明確標注的產出物。
- 【嚴禁】除上述 target 外，**其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。**

## PRINCIPLE: 不重畫 Discovery 真相

- Discovery 已 accepted 的 rule-only `${FEATURE_SPECS_DIR}/**`、`${ACTIVITIES_DIR}/**`、`${IMPACT_MATRIX_YML}`、`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}` 之需求全文 **為唯讀輸入**；本 skill **不得**改寫任何 feature／activity 內容、不得改 atomic rule 文字、不得新增 Scenario／Background／Examples。
- `${IMPACT_MATRIX_YML}` 僅能經 `manage_impact_matrix.py` 的 `upsert`／`validate` 追加本 skill 派生出的 data impact；不得手改 YAML 本體。
- 若發現上游真相不足以推導 data schema，必須**回頭委派** `/clarify-loop`，由 Discovery owner 修正後再續跑；**禁止**就地補洞。

## PRINCIPLE: 真相格式委派 specifier skill

- Boundary profile 宣告之 `state_specifier.skill`，是寫入 `${DATA_DIR}/**` 之**唯一合法管道**。
- 本 skill **不得**手寫任何 DBML／其他 state 格式；只負責 DERIVE caller payload 並以 **`DELEGATE`** 把 payload 交給 specifier skill。一個 entity／schema 為一次 DELEGATE。
- 違者視為 ownership 違規，**立即 STOP**。

## PRINCIPLE: 澄清只委派 clarify-loop

- 凡須向使用者做**結構化澄清**（locale 選擇、scope 模糊、上游真相缺洞、specifier 不支援等），本 SOP 僅用 **一行 `DELEGATE /clarify-loop`**。
- **禁止**在 SOP 內 inline classify／branch user reply；**禁止**聊天逐題代替。

## PRINCIPLE: STRICT SOP

1. **依序不漏步**：自底下 SOP 逐一執行；每做一步，在訊息中**明示該步編號**。
2. **限縮延長推理**：僅當當步**明文**標示須 **`THINK / REASONING`** 時，才拉長內省與推演；否則以**最直接**可做之工具呼叫達成該步。

## PRINCIPLE: 待辦工具化

- 本 SOP 雖為單檔扁平流程，仍可能跨多輪對話；在 **conversation compact** 之後，執行者要靠**同一套待辦**還原目前卡在哪一步。
- **必須工具化**：以執行環境提供的任務／待辦建立與更新能力（**`TODOCREATE`**、**`TASKCREATE`** 或等效）把底下 SOP 第一層編號步驟實體化成清單，在跑 SOP 當下就建好並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點。

# SOP

請執行到哪讀到哪，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. 在 CWD 底下 grep 搜尋 `**/arguments.yml` 檔案，做 parameters binding for all following steps，這些參數後續每一步都會用到。此檔案一定存在，如不存在請直接停止執行，向使用者回報：「我在 ${CWD} 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」

1. RESOLVE arguments——將本 SOP 引用的 `${VAR}`（**僅本 skill 用到者**）透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   BOUNDARY_YML=${BOUNDARY_YML}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. ASSERT arguments 必備鍵齊全
   - 對上層已 PARSE 之 `${AIBDD_ARGUMENTS_PATH}` 逐項檢查下列鍵存在：`DATA_DIR`、`PLAN_SPEC`、`PLAN_REPORTS_DIR`、`IMPACT_MATRIX_YML`、`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`CURRENT_PLAN_PACKAGE`、`BOUNDARY_YML`、`ACTIVITIES_DIR`、`FEATURE_SPECS_DIR`。
   - 任一缺鍵 → 列出缺鍵，提示使用者回 `/aibdd-kickoff` 或 `/aibdd-flows-specify` 補綁後再執行本 skill，STOP。本步禁止順手補建 arguments.yml 任何欄位。

3. ASSERT Discovery 真相已 accepted（READ-ONLY）
   - `${PLAN_SPEC}` 存在且含需求敘事全文與 discovery sourcing pointer（章節對齊 `/aibdd-flows-specify`）。
   - `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 存在。
   - `${IMPACT_MATRIX_YML}` 存在。
   - `${FEATURE_SPECS_DIR}` 下至少一份 rule-only `.feature` 檔。
   - `${ACTIVITIES_DIR}` 下若有 `.activity` 則納入 `activity_truth`；若無則視為空集合（不得因此 STOP）。
   - 任一條件失敗 → 提示使用者回 `/aibdd-flows-specify`（spec.md／feature 骨架）或 `/aibdd-rules-specify`（atomic rules）補完，STOP。本步禁止補建或改寫 discovery markdown／feature／activity artifact。

4. READ：boundary type profile 與 state specifier
   - PARSE `${BOUNDARY_YML}` 之 `type` 欄位為 `$boundary_type`；若不存在則 STOP & 報錯。
   - 自該 boundary profile 取出 `state_specifier.{skill,format}`；產出目錄對齊 `${DATA_DIR}`。

5. BIND `$PLAN_SCOPE`（本輪 plan package + function package charters）
   1. READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 `## Function package charters` 與 `## Packaging decision`。
   2. DERIVE `$plan_package_slug` 自 `${CURRENT_PLAN_PACKAGE}` basename。
   3. DERIVE `$function_package_slugs[]`：`Packaging decision` 所列本輪涉及的 `packages/NN-<slug>`；每一 slug 須在 `Function package charters` 有對應小卡。
   4. DERIVE `$PLAN_SCOPE = { plan_package_slug, function_package_slugs[], charter_cards[] }`。
   5. 若 `Packaging decision` 與 `Function package charters` 不一致、或無法解析任一 function package slug，STOP 並回報 discovery sourcing 不完整。

6. TRIGGER impact matrix query，BIND `$PLAN_MUTABLE_IMPACT_ENTRIES`
   1. 讀取本輪 mutable workset（含 `conditional_update`）：
      ```bash
      python3 .claude/skills/aibdd-flows-specify/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} query \
        --change-type update \
        --change-type add \
        --change-type conditional_update
      ```
   2. PARSE stdout JSON 之 `entries` 為 `$PLAN_MUTABLE_IMPACT_ENTRIES`。
   3. FILTER：只保留 path 落在 `$PLAN_SCOPE.function_package_slugs[]` 所屬 `${TRUTH_BOUNDARY_PACKAGES_DIR}/<slug>/**`、或 `${DATA_DIR}/**` 的 entry；其餘 entry 不納入本 skill 推導 scope。
   4. 若 matrix 缺失或 `ok` 為 false，STOP 並回報 impact matrix 不完整。

7. READ-ONLY 載入既有 data 真相骨架（不寫入）
   - READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`、`${DATA_DIR}/**`（缺則視為空骨架）。
   - READ code skeleton index（排除 ignored directories 與非主 worktree）。
   - 只 READ，不得 CREATE 任何空檔或目錄骨架。

8. DERIVE state `target_path` 集合：以 `${PLAN_SPEC}`、`$PLAN_SCOPE` 所涵蓋之 `${FEATURE_SPECS_DIR}/**` 為 SSOT，從資料流動建立資料狀態聚合分析，把資料拆分成 Domain Aggregate／Entity／Value-Object——客觀、不腦補（可加讀 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${ACTIVITIES_DIR}/**`）；依切檔策略決定每份 state schema 的 `target_path`（相對 `${DATA_DIR}` 的檔案路徑）。`target_path` **不得**含 `<<NN-functional-module>>` 借位子層 — `${DATA_DIR}` 在 SSOT 已是 flat directory（見 `aibdd-core::spec-package-paths.md`）。

9. DELEGATE `/${state_specifier.skill}`：請直接透過 Load SKILL 執行該 skill，並遵循其自身的禁令與輸入／輸出形狀，DELEGATE payload 內帶入步驟 8 之 `target_path`；specifier 依其認定之 `format` 寫入 `${DATA_DIR} ⊕ target_path`。

10. TRIGGER impact matrix writeback（本 skill 派生出的 data target paths）：EXECUTE `steps/impact-matrix-writeback.md`。

11. （此步驟必須嚴格遵守，至少要有一條澄清項目）`$NEED_TO_CLARIFY`, `$NEED_TO_FIX` = DO FAITHFUL REASONING 針對本 skill 已導出之 state schemas 與 impact writeback 整體結果，依照 `steps/derive-findings.md` 中的分析切角去進行深度分析，並找到所有需要修正、澄清的地方。

12. 若 `$NEED_TO_FIX` 非空：依 `$NEED_TO_FIX` 修正本 skill 之 state target paths、specifier delegation input 與 impact matrix writeback，必要時重跑步驟 `8` 到 `10`。

13. 若 `$NEED_TO_CLARIFY` 非空：DELEGATE `/clarify-loop` 一次進行提問。

14. 和使用者說道（詞可變、語意不變）：「我已經以 Discovery 真相把本輪須穩定保存的系統狀態推導成 data schema，並委派 specifier 落到 ${DATA_DIR}。你看一下我產的 DBML／資料規格確認設計沒問題。」
    - **禁止建議下一步**：結尾**不得**建議、推薦、引導或暗示任何下一個要執行的 skill／slash command／後續流程（例如 `/aibdd-api-plan`、`/aibdd-implement`、`/aibdd-tasks` 等一律不得出現）。本 skill 到此為止，只回報本輪產出並請使用者檢視，後續由使用者自行決定。
