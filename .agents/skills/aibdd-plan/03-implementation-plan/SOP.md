# SOP

緣由：02 已把 boundary 對外契約（operation / state）落地，但只到 e2e 可驗證面；要讓下游 GREEN 不只「過測」、還能「結構 fit」，必須再做一層 internal design——以多條情境的 sequence diagram 為先導，收斂成一張類別圖（C4-Level class diagram）作為實作骨架，遵守 tidy-first（make the change easy, then make the easy change）。

0. **RESOLVE arguments**——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   DEV_CONSTITUTION_PATH=${DEV_CONSTITUTION_PATH}
   PLAN_IMPLEMENTATION_DIR=${PLAN_IMPLEMENTATION_DIR}
   PLAN_INTERNAL_STRUCTURE=${PLAN_INTERNAL_STRUCTURE}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SEQUENCE_DIR=${PLAN_SEQUENCE_DIR}
   EOF
   ```

1. READ `${DEV_CONSTITUTION_PATH}`；後續內部結構與分層須與之一致。如無此檔案則直接 SKIP 此步驟。

2. THINK：設計實作路徑與內部結構
   - READ `rules/sequence-path-granularity.md`、`reasoning/implementation-path-design.md`（SSOT、impact 覆蓋、path 可追溯、`$IMPLEMENTATION_MODEL` 形狀）。
   - 依上列規範 faithful reasoning 產出 `$IMPLEMENTATION_MODEL`；本步不寫檔。

3. CREATE `${PLAN_IMPLEMENTATION_DIR}`、`${PLAN_SEQUENCE_DIR}`；僅目錄，不預建空 `.mmd`。

4. WRITE sequence diagrams via DELEGATE
   - FOR EACH path in `$IMPLEMENTATION_MODEL.paths`：DELEGATE `/aibdd-form-sequence-diagram` with payload `{ target_path: "<scenario_slug>.<category>.sequence.mmd", reasoning: { implementation_path: path } }`。

5. WRITE `${PLAN_INTERNAL_STRUCTURE}` via DELEGATE
   - READ `rules/internal-structure-union.md`（其中定義「結構聯集」並附示意例）；依該定義把 `$IMPLEMENTATION_MODEL.paths` 收成單一 class diagram 之 `collaborators[]` + `relations[]`（去重 + 保留差異 + 註記）。**本步只在 SOP 端完成聯集 reasoning，不寫檔。**
   - DELEGATE `/aibdd-form-class-diagram` with payload `{ target_path: "<basename of ${PLAN_INTERNAL_STRUCTURE}>", reasoning: { implementation_model: $IMPLEMENTATION_MODEL } }`。

6. ASSERT 可追溯性
   - 每個 implementation target（actor、operation、collaborator、provider call、state change）至少可追溯至一條 activity path、atomic rule、provider contract 或 boundary-map dispatch。
   - 無法追溯者寫入 `$IMPLEMENTATION_MODEL.blocked_reasons[]`（含 target、原因），供後續 phase 在 `${PLAN_REPORTS_DIR}` 下由上游指定之 research 檔顯式落地；禁止靜默忽略。
