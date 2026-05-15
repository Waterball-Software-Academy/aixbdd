# 參數設定

- **產出錨點** → 見 `research/discovery-拆解/SKILL.md` **PRINCIPLE: CWD 為產出錨點**；下列 `${…}` 均錨定於 **`CWD`**。
- **需求故事錨點** → `${PLAN_SPEC}`（`${CURRENT_PLAN_PACKAGE}/spec.md`）
- **Discovery 報告** → `${PLAN_REPORTS_DIR}/discovery-sourcing.md`（澄清擱置機讀題組：`${PLAN_REPORTS_DIR}/discovery-clarify-pending.payload.yml`）
- **活動規格／`.activity` 根目錄** → `${ACTIVITIES_DIR}`
- **Activity／feature 命名憲法** → `${BDD_CONSTITUTION_PATH}` §5.1

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. THINK: 拆解 `${PLAN_SPEC}` 中需求敘述的每一段話，進行段落流程建模分析。 標註每一段話為 $P，所有話的集合為 all $P
2. FAITHFUL REASONING: FOR EACH $P，萃取此段落句子中的 Actors 或 Actions，請勿捕捉句子中不存在的元素，因此捕捉過程針對每一個捕捉物都要明確指出他對應的證據。
    - $Actors = 嚴格遵照 `rules/activity-actor-granularity.md` 的顆粒度定義來萃取。
    - $Actions = 嚴格遵照 `rules/activity-step-granularity.md` 的顆粒度定義來萃取。
    - $GAPS = 當你發現底下現象時，將此現象記錄起來儲存於內部推理思考的 GAPS 空間中：
        - 找到某個 Action 但不確定其隸屬於哪一個 Actor。
        - 找到某個 Actor 但不確定他具備哪些 Action。
        - 針對某個 Action 不確定他的顆粒度是否正確，是否應該被萃取成 Action。

3. **FAITHFUL REASONING: `UAT flows` 清單**（一條 flow = **一張** Activity；從 actor 可理解的「進場→可驗收」完整旅程）
   - **READ** `rules/activity-diagram-granularity.md`
   - 從 all `$P` 提煉**幾條**獨立 flow、因而**幾張**活動圖；輸出至訊息中 **`$UAT_FLOWS`**（每條 flow **一筆**記錄）。
   - **`$UAT_FLOWS` 每筆必備鍵（缺任一即視為步驟 3 未完成；供步驟 4 機械組路徑）**：`uat_flow_id`（本輪唯一）、`summary_one_line`（一句話 journey：進場→可驗收）、`activity_relpath`（相對 **`${ACTIVITIES_DIR}`** 之**唯一相對路徑**：可為單一檔名如 `foo.activity`，或含子目錄如 `pkg/order-submit.activity`；**須**以 **`.activity`** 結尾、**不得**以 `/` 開頭）。**寬鬆度**：`variation_role`（`happy_path`／`extreme_min`／`extreme_max`／`additional`）選填，未知則 `additional`。

4. **WRITE FILES: 活動圖檔** — 對 **`$UAT_FLOWS` 每一筆**：以 **`${ACTIVITIES_DIR}`** 為根、依 **`activity_relpath`** **新建**對應 `.activity` 檔（步驟 **3** 三必備鍵須已齊）；**本步僅允許**檔頭註解或 Activity DSL **極小骨架**；Action、決策節點、轉移與並行語意留待步驟 **7** 寫入。

5. **WRITE FILES: Feature 檔（initial）** — **READ** `templates/initial-feature-file.template.md`。對 `$Actions` 中尚未存在對應檔者於專案 feature 規格目錄補建 `.feature`：**正文**為模板中 fenced 區塊之逐字複製，僅將 `REPLACE_WITH_TITLE_MATCHING_ACTION` 換成對齊該 Action 之一行標題；路徑／檔名依 **`${BDD_CONSTITUTION_PATH}` §5.1**。

6. **READ：Activity 落地閘道** — **READ** `{SKILL-HOME}/aibdd-dispatchers/write-activity/DISPATCH.md`。依該檔辨識 Activity Aggregate 所需結構定義。

7. **FAITHFUL REASONING** — **FOR EACH** `$UAT_FLOWS` 之一條 flow，將對應步驟 **4** 之 `.activity` 內容設計完整。素材來自 **all `$P`、該筆之 `summary_one_line`、以及僅與此 journey 有證據關聯之 `$Actions` 子集**。**READ** `reasoning/activity-control-flow.md`，依該檔**編號** 逐項執行。

8. **WRITE AGGREGATE FILES**：依步驟 **6** `DISPATCH.md` 所定分支與約束，將上述所有 Activities 寫成與該路徑一致之檔案／聚合。

9. IF **`$GAPS` 非空** → **DELEGATE** `/clarify-loop`，**`delegated_intake`**：**`profile`**＝**`aibdd-discovery`**（其餘 [`../clarify-loop/references/intake-expanders/aibdd-discovery.md`](../clarify-loop/references/intake-expanders/aibdd-discovery.md)）：**`phase`**＝**`activity`**，`raw_items`←`$GAPS` 每筆之 **`text`**，`anchors` 鍵 **`plan_spec`／`plan_reports_dir`／`activities_dir`／`feature_specs_dir`** 分別←本 sub-SOP **`${PLAN_SPEC}`** 等（相對 **`CWD`**）。若 **`completed`**：依回傳合流規格。
10. IF **`$GAPS` 為空**或上步為 **`completed`**：向使用者說道：「OK，很好，活動圖和初步 Feature File 我想我們是分析完了，你晚點還能跟我說你想改什麼。現在我要繼續下一步驟：**分析每一個 Feature File 裡面有哪些規則**。」IF 上步 **`unsupported_tooling`**：唯轉述 **`/clarify-loop`**（**`artefacts.wrote`**），**禁止**聊天重造題組。**END** Sub-SOP。
