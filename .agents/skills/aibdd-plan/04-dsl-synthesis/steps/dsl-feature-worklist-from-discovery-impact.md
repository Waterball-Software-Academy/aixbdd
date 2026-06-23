# BUILD `$DSL_FEATURE_WORKLIST`（Discovery Impact matrix）

由 `${IMPACT_MATRIX_YML}` 決定「本輪須對哪些 `.feature` 做 DSL 迭代」的可列舉工作集，輸出 **`$DSL_FEATURE_WORKLIST`**。

1. 以 `read --spec-path '\.feature$' --spec-status inconsistent` 取仍待落地的 `.feature` 工作清單（每個 spec 仍 `inconsistent` 才算待做）；攤平 `impacts[].specs[].path`，依 `${SPECS_ROOT_DIR}` 物化、去重後排序，記為 **`$DSL_FEATURE_WORKLIST`**。CLI 用法詳見 `aibdd-core::impact-matrix/cli-usage.md`。
   物化規則：若 `path` 未以 `${SPECS_ROOT_DIR}/` 開頭，則 prefix `${SPECS_ROOT_DIR}/`。
   若自 `/aibdd-plan` 呼叫，FILTER：只保留 path 落在 `$PLAN_SCOPE.function_package_slugs[]` 所屬 `${TRUTH_BOUNDARY_PACKAGES_DIR}/<slug>/**` 的 path。

2. ASSERT **`$DSL_FEATURE_WORKLIST`** 非空 **或** 明確為「本輪無任一 `.feature` 屬新建／更新 DSL 所需」並在後續以 `no_op_reason` 收斂；所有 `.feature` spec 皆已 `consistent`（無 inconsistent feature spec）且無別檔需寫 DSL 者得視為合法空 worklist。
