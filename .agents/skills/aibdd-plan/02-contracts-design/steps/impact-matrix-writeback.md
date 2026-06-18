本 phase 同時回寫 contracts 與 data；兩者皆以 `(owner, spec)` 為鍵冪等寫一個 impact，`owner=aibdd-plan`：`quotes` 指回驅動該 spec 的需求原文（≥1，取自 `${PLAN_SPEC}`／feature truth），`rationale` 以現在式一句話描述本 phase 對該檔的規格增量。CLI 用法詳見 `aibdd-core::impact-matrix/cli-usage.md`。

1. FOR EACH 步驟 2 之 contract `slice.target_path`，spec path＝`contracts/<target_path>`（相對 `${TRUTH_BOUNDARY_ROOT}`）。
2. FOR EACH 步驟 4 之 state `target_path`，spec path＝`data/<target_path>`（相對 `${TRUTH_BOUNDARY_ROOT}`）。
3. 對上述每個 spec 依其 change_type 冪等 write，`owner=aibdd-plan`：
   1. `add`／`update`／`conditional_update` → write 該 impact（spec 一律以 `inconsistent` 落地；`conditional_update` 先寫、後續定案再 refine）。先 `read --owner aibdd-plan --spec-path '^<escaped exact spec>$'`：回有 impact → 取其 `id` 後 `write --id <id> …` 取代；否則 `write …` 新建（自動 uuid）。
   2. `read_only_compare`（僅供比對、非本 phase 派生）→ **不寫任何 impact**。
   3. `remove` 僅用於本輪「實際刪除該契約／state 檔」時：與刪檔同時，先 `read --owner aibdd-plan --spec-path '^<escaped exact spec>$'` 取回 `id` 再 `remove --id <id>`。僅改動而不刪檔者一律走 `update`→`write`（spec 落 `inconsistent` 即提醒下游的訊號），不得 `remove`。
