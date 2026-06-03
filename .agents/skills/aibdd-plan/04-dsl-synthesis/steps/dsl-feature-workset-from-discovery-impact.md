# BUILD `$DSL_FEATURE_WORKSET`（Discovery Impact matrix）

由 `${IMPACT_MATRIX_YML}` 決定「本輪須對哪些 `.feature` 做 DSL 迭代」的可列舉工作集，輸出 **`$DSL_FEATURE_WORKSET`**。

1. TRIGGER impact matrix query（排除 `read_only_compare`）：
   ```bash
   python3 .claude/skills/aibdd-flows-specify/01-sourcing-and-packaging/scripts/cli/manage_impact_matrix.py \
     --matrix ${IMPACT_MATRIX_YML} query \
     --suffix .feature \
     --change-type update \
     --change-type add \
     --change-type conditional_update
   ```

2. PARSE stdout JSON 之 `entries`，依 `${SPECS_ROOT_DIR}` 物化 `path`、去重後排序，記為 **`$DSL_FEATURE_WORKSET`**。
   物化規則：若 `path` 未以 `${SPECS_ROOT_DIR}/` 開頭，則 prefix `${SPECS_ROOT_DIR}/`。
   若自 `/aibdd-plan` 呼叫，FILTER：只保留 path 落在 `$PLAN_SCOPE.function_package_slugs[]` 所屬 `${TRUTH_BOUNDARY_PACKAGES_DIR}/<slug>/**` 的 entry。

3. ASSERT **`$DSL_FEATURE_WORKSET`** 非空 **或** 明確為「本輪無任一 `.feature` 屬新建／更新 DSL 所需」並在後續以 `no_op_reason` 收斂；矩陣全為 `read_only_compare` 之 feature entry 且無別檔需寫 DSL 者得視為合法空 workset。
