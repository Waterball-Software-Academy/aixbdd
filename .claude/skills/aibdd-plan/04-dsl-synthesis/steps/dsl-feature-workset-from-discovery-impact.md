# BUILD `$DSL_FEATURE_WORKSET`（Discovery Impact matrix）

由 `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 `## Impact matrix` 決定「本輪須對哪些 `.feature` 做 DSL 迭代」的可列舉工作集，輸出 **`$DSL_FEATURE_WORKSET`**。

1. READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 `## Impact matrix`。

2. PARSE 表格：取第一欄路徑指向 **`packages/.../features/*.feature`**（相對 `${TRUTH_BOUNDARY_ROOT}`）且 **`變更類型` ≠ `讀取對照`** 之每一列，正規化為相對 `CWD` 之可讀路徑（或與 `Glob ${FEATURE_SPECS_DIR}/*.feature` 同形之 basename 集合），去重後排序，記為 **`$DSL_FEATURE_WORKSET`**。

3. 若 matrix 以單列 **glob**（例如 `packages/.../features/*.feature`）概括多檔：`DERIVE` workset＝`Glob ${FEATURE_SPECS_DIR}/*.feature` 之結果，但必須在當次執行訊息中 **EMIT 警告**：「Impact matrix 未逐檔列舉，workset 由目錄 glob 推導；請於 Discovery 修正為每檔一列以利對拍。」若你方流程約定下游僅依 glob 閉包且不升級矩陣，須於 `discovery-sourcing.md` 之 `Notes` **明文化**該約定，否則不得以此規避 STOP。

4. ASSERT **`$DSL_FEATURE_WORKSET`** 非空 **或** 明確為「本輪無任一 `.feature` 屬新建／更新 DSL 所需」並在後續以 `no_op_reason` 收斂；矩陣全為 `讀取對照` 之 feature 列且無別檔需寫 DSL 者得視為合法空 workset。
