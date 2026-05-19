# SOP

緣由：實作計畫（對外契約、對內結構）就緒後，本 phase 把「Gherkin business-statement-step → 可執行自動化步驟與斷言」之映射規則，依顆粒度寫入 `${BOUNDARY_PACKAGE_DSL}`、`${BOUNDARY_SHARED_DSL}`。

1. DERIVE `${DSL_KEY_LOCALE}`
   - 依 `steps/dsl-key-locale.md` 1.1–1.3 執行；其餘以該檔為準。

2. READ boundary preset（SSOT：`${BOUNDARY_YML}`）
   - 依 `steps/boundary-preset-and-handler-routing.md` 執行其中所有步驟：解析 boundary type、載入 boundary-type profile、讀取 profile 所指之 handler routing 文檔（含 `dsl-writing-rules-for-each-part`）、L4 履約順序與 TodoWrite、persistence 相關變數與 gate ASSERT；STOP 條件見該檔。
   - 當本 phase 進入「依 feature 檔迭代」時，TodoWrite 粒度須符合該檔「與 per-feature loop 搭配」之規定（外層：目前迭代之 `.feature`；內層：該 entry 之 `l4_requirements`）。

3. BUILD `$DSL_FEATURE_WORKSET`（Discovery 閉包）
   - 依 `steps/dsl-feature-workset-from-discovery-impact.md`；其餘以該檔為準。

4. **LOOP** per `$feature_path` in `$DSL_FEATURE_WORKSET`（固定排序；一檔一迭代；budget = `len($DSL_FEATURE_WORKSET)`；exit on iterator exhaustion）

   4.1 READ `rules/01-dsl-entry-schema.md`、`rules/02-dsl-parameters-coverage.md`（首次迭代後可快取；以快取為由跳過重讀時須 ASSERT 規則檔未變更）。

   4.2 PARSE 本迭代 `$feature_path` 為 atomic rules 列表 `$rules`：每一條 `Rule:` 區塊為一筆，含完整 rule 文字（含子條目／example）。禁止合併多條 rule 為單筆；禁止跳過任何 rule（純文字陳述也需走 4.3 CLASSIFY）。

   4.3 **LOOP** per `$rule` in `$rules`（budget = `len($rules)`；exit on iterator exhaustion）

      4.3.1 **CLASSIFY** `$rule` 之語意 kind（依規則文字 prefix／結構，由 boundary handler-routing 之 `routes[].keyword` 與 `dsl-writing-rules-for-each-part` 共同決定，逐字對照不得心證），enum 至少含：
      - `precondition-parameter`（前置參數／參數合法性／輸入形狀規則）
      - `precondition-state`（需事先存在的 entity／aggregate 狀態）
      - `precondition-time` / `precondition-external`（時間／外部資源前置）
      - `operation-target`（操作本身的可呼叫面——通常隱含於 feature 標題，每個 feature 至少 1 條）
      - `postcondition-state`（持久化變更後該存在／不存在的狀態）
      - `postcondition-response`（API 回應形狀／status／payload／拒絕訊號）
      - `read-only-reference`（純文字對照、無可落地面）

      4.3.2 **BRANCH** on classified kind → 對照 boundary `handler-routing.yml` 之 `routes[].part` 與 `dsl-writing-rules-for-each-part`，列舉本 rule 必須產生之 entry 集合（下表以 web-service／web-backend handler ids 為例；其他 boundary 以該 boundary handler-routing 為準）：

      | rule kind | 必出 handler / surface_kind | 顆粒度 |
      |---|---|---|
      | `precondition-parameter` | 併入該 feature 之 `operation-invoke` entry 之 `param_bindings` 覆蓋；不獨立成 entry | 不獨立 |
      | `precondition-state` | `state-builder`（surface_kind=`state-builder`）；每個參與 entity／DBML table 各一筆 | per entity |
      | `precondition-time` | `time-control` | per clock surface |
      | `precondition-external` | `external-stub` | per external resource |
      | `operation-target` | `operation-invoke`（surface_kind=`operation`） | 一 feature 至少一筆 |
      | `postcondition-state` | `state-verifier`（surface_kind=`state-verifier`） | per verified field／entity |
      | `postcondition-response` | `operation-response-success-and-failure` 或 `operation-response-success-readmodel`（依規則語意擇一） | per asserted response surface |
      | `read-only-reference` | 無 entry；於本迭代 `no_op_reason` 累計該 rule anchor | 累計理由 |

      4.3.3 **FAITHFUL REASONING** 推演 `$rule` 對應 entry 集合（欄位以 `rules/01-dsl-entry-schema.md` 為準；`L4.preset.{name,handler,variant}` 對齊本輪 boundary preset 與 `handler-routing.yml`，不得自造 handler id；`L4.source_refs.boundary` 指向實際載入之 `handler-routing.yml` 路徑）。禁止為其他 `.feature` 檔代推 entry。

      4.3.4 在落 candidate entries 之前，EXECUTE `scripts/dsl-cli/run.py`：先用 `search <query> --boundary <邊界目錄 basename>`（basename 為 `${TRUTH_BOUNDARY_ROOT}` 最末路徑段，例：`…/specs/backend` → `backend`）在 `shared/dsl.yml` 與 `packages/*/dsl.yml` 做子字串比對——`<query>` 可為表／實體名、L1 句型片段、`surface_id`、`operationId` 片段、`source_refs.contract` 內檔名字段；可選 `--fuzzy`（門檻見 `--help`）；若要比對 `operationId` 是否已在 OpenAPI 露面，帶 `--contracts-root ${CONTRACTS_DIR}`。接著對目前 registry 跑 `verify [--strict] --boundary …` 抓全域 `id` 重複與語意層警示／嚴格錯——確認本 rule 之 entry 候選不致不當重複（譬如 state-builder／invoke 已定義在 shared 或其他 package，沿用既有 entry id 並記入本 rule 的 `covered_by_existing` 列表，勿再複製）。

      4.3.5 **ASSERT** 本 `$rule` 之 entry 集合非空（kind=`read-only-reference` 允許空但須累計 `no_op_reason` anchor；其餘 kind 至少 1 筆新增或沿用既有 entry id）。違反 → 列出 rule anchor／kind／預期 handler／實際輸出，**STOP**。

   4.4 WRITE DSL registries（merge）
   - 本迭代之 `local_entries` 非空 → merge 進 `${BOUNDARY_PACKAGE_DSL}`（保留既有 `entries`，以 `id` 去重；衝突則 **STOP** 並列出 id）。
   - 本迭代之 `shared_entries` 非空 → merge 進 `${BOUNDARY_SHARED_DSL}`。
   - 兩者皆空 → ASSERT 該檔之 `no_op_reason` 非空（須對應 4.3.1 標為 `read-only-reference` 之 rule anchor 列表），否則 **STOP**。

   4.5 寫入前或寫入後，本迭代涉及之 entry 須滿足下列規則檔全文約束（違規時列出 entry id／欄位或 binding key／原因；禁止刪除 assertion 或以弱 placeholder 繞過；**STOP**）。不得以本節條列取代規則檔正文：
   - `rules/01-dsl-entry-schema.md`
   - `rules/02-dsl-parameters-coverage.md`（每筆 operation entry 完整套用 §1–§3）

   **END LOOP** (per `$rule`)

   **END LOOP** (per `$feature_path`)

5. **AGGREGATE ASSERT** — 全 workset 覆蓋率自驗（不得跳過）

   5.1 COMPUTE `$total_rules` ＝ 對 `$DSL_FEATURE_WORKSET` 內每檔以 4.2 PARSE 規則重數加總。
   5.2 COMPUTE `$total_entries_emitted` ＝ 本輪在 `${BOUNDARY_PACKAGE_DSL}`／`${BOUNDARY_SHARED_DSL}` 新增或沿用之 entry id 集合大小（去重）。
   5.3 COMPUTE `$rules_covered` ＝ 從 4.3.3／4.3.5 紀錄之 rule→entry-ids 反查表中，至少對應一筆 entry id（含 `covered_by_existing`）之 rule 數；`read-only-reference` rule 視為涵蓋。
   5.4 ASSERT `$rules_covered == $total_rules`；違反時列出未覆蓋之 rule anchor 與其分類 kind，**STOP**（禁止為通過 ASSERT 而把缺項硬塞為 `read-only-reference`；該 reclassify 必須回到 4.3.1 重新依規則文字判定）。
   5.5 ASSERT 每筆 `precondition-state` rule 至少有 1 筆 `surface_kind=state-builder` entry 涵蓋；每筆 `postcondition-state` rule 至少有 1 筆 `surface_kind=state-verifier` entry 涵蓋；每筆 `postcondition-response` rule 至少有 1 筆 `surface_kind` 屬 `operation-response-*` family 之 entry 涵蓋。違反 → **STOP** 並列出缺漏配對。
