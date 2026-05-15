# Boundary preset、`$HANDLER_ROUTING` 與 `dsl-writing-rules-for-each-part`

自 `${BOUNDARY_YML}` 到載入與 boundary `type` 成對之 profile、同目錄 `handler-routing.yml`（含 `dsl-writing-rules-for-each-part`）、L4 履約與 TodoWrite。

SSOT：`aibdd-core` hub 之 `assets/boundaries/<boundary.type>/`（見 `.claude/skills/aibdd-core/SKILL.md` §2 ASSETS）。相對 `${CWD}`：

- profile：`.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/profile.yml`
- handler routing：`.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/handler-routing.yml`


1. PARSE `${BOUNDARY_YML}` → `$boundary_type`
   - 鎖定本輪 boundary 條目（`id`／`role` 與 plan 一致），讀其 `type`。
   - 可執行 preset／範式由此決定；不得以 arguments 內其他鍵（例如自訂 preset 別名）凌駕 boundary 宣告。

2. READ boundary preset profile → `$BOUNDARY_PROFILE`
   - READ `.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/profile.yml`（相對 `${CWD}`），結果記為 `$BOUNDARY_PROFILE`。
   - 本 phase 以其中 `operation_contract_specifier`／`state_specifier`（skill／format／output 相關欄位）為 formulation 管線依據；其餘擴充欄位若存在僅作選讀，未宣告者不強制。

3. READ `$HANDLER_ROUTING`
   - READ `.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/handler-routing.yml`（與上列 profile 同目錄）。
   - 上述檔須含 `dsl-writing-rules-for-each-part`（與 `routes` 同檔）；各 handler key 對應 `required_source_kinds`、`optional_source_kinds`（若有）、`l4_requirements`。此區段為依 handler 撰寫 L4 之規範 SSOT；不得只讀 `routes` 而略過。
   3.1 逐條、依序、全遵守
      - 凡某句／某筆 DSL entry 分類到 `L4.preset.handler = H`，必須對照 `dsl-writing-rules-for-each-part.H`。
      - `l4_requirements` 陣列每一元素為一則完整規範（同則內若含 Example 段落仍視為單一 requirement，不可再拆）；依檔內順序逐則檢驗並體現在該 entry 之 `L4`（bindings、`source_refs`、`callable_via` 等）。
      - 不得跳項、倒序、合併成概括句或「心證帶過」。
   3.2 TodoWrite（強制）
      - 已鎖定 `H` 時，對 `dsl-writing-rules-for-each-part.H.l4_requirements` 每一元素各自恰好一個 todo item（順序與 YAML 一致；文案可辨識對應哪一則 requirement）。
      - 禁止單一 todo 代表整組 handler 規範；該 entry 僅當這些 todo 全數 resolved／completed 後才算履約完成。
      - 與 DSL synthesis per-feature LOOP 搭配（上層 SOP 若對 `$DSL_FEATURE_WORKSET` 逐檔迭代，例如 `experiemented-skills/aibdd-plan/04-dsl-synthesis/SOP.md`）：外層須對當次迭代之所屬 `.feature` 至少一項 todo（標題或可辨識欄須含該檔相對於 repo 的路徑或穩定 basename），表示「該檔此輪 DSL 區塊」之進度邊界；內層維持上兩項——對 `l4_requirements` 每一元素仍各一 todo。同一檔未完成內層全部對應 todos 之前，不得將外層「該檔」標為完成並進入下一 `$feature_path`。

4. （建議）機械化查重與搜尋：`dsl-cli`（[`scripts/dsl-cli/run.py`](../../../../scripts/dsl-cli/run.py)；併入 skill package 後改為同名模組進入點，無獨立 README）
   - 在 merge 任一 `packages/*/dsl.yml` 或 `shared/dsl.yml` 之前／之後，對 `${TRUTH_BOUNDARY_ROOT}` 執行 `verify`／`search`。路徑參數擇一：`--boundary <邊界目錄 basename>`（並視需要 `--specs-root`，預設相對 cwd 之 `specs`），或 `--root` 直指該 boundary 根目錄；細節以 `run.py` 頂部註解與 `--help` 為準，`uv run …/run.py` 載入 PEP 723 依賴。用以補「跨 function package 是否已存在同表／同 operation 之 state-builder 或 invoke entry」之可驗性；**不**取代 3.1 對 `l4_requirements` 的逐則履約。
