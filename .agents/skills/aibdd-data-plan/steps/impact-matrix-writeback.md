FOR EACH 步驟 8 之 state `target_path`（spec path＝`data/<target_path>`，相對 `${TRUTH_BOUNDARY_ROOT}`），以 `(owner, spec)` 為鍵冪等寫一個 impact，`owner=aibdd-data-plan`：`quotes` 指回驅動該 state schema 的需求原文（≥1，取自 `${PLAN_SPEC}`／feature truth），`rationale` 以現在式一句話描述本 skill 對該 state schema 檔的規格增量。CLI 用法詳見 `aibdd-core::impact-matrix/cli-usage.md`。

1. 冪等 write 規則（依步驟 8 該 target_path 之 change_type 分流）：
   1. `add`／`update`／`conditional_update` → write 該 impact（spec 一律以 `inconsistent` 落地；`conditional_update` 先寫、後續定案再 refine）。先 `read --owner aibdd-data-plan --spec-path '^<escaped exact spec>$'`：回有 impact → 取其 `id` 後 `write --id <id> …` 取代；否則 `write …` 新建（自動 uuid）。
   2. `read_only_compare`（僅供比對、非本 skill 派生）→ **不寫任何 impact**。
   3. `remove` 僅用於本輪「實際刪除該 state schema 檔」時：與刪檔同時，先 `read --owner aibdd-data-plan --spec-path '^<escaped exact spec>$'` 取回 `id` 再 `remove --id <id>`。僅改動而不刪檔者一律走 `update`→`write`（spec 落 `inconsistent` 即提醒下游的訊號），不得 `remove`。
