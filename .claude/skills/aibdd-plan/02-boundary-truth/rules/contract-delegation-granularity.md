# Contract 委派顆粒度

- **唯一寫入管道**：`${TRUTH_BOUNDARY_ROOT}/contracts/**` 之**任何**檔案產生／修改，**必須**透過 `$BOUNDARY_PROFILE.operation_contract_specifier.skill` 之 `DELEGATE`；**禁止**本 skill 手寫 OpenAPI／YAML contract 檔。
- **一個 slice 一次 DELEGATE**：每筆可**獨立命名／獨立驗收／獨立呼叫**之 operation slice 為一次 DELEGATE 之單位；**禁止**把多 slice 包成同一 payload 委派。
- **payload 必含**：`operation_id`／`endpoint`／`method`／`request.params`／`request.body`（含各欄位 required flag）／`request.headers`（含 transport 標記）／`response.fields`／`errors`／`source_refs`（指回 atomic rule、activity step、provider contract）。
- **profile=none**：若 `operation_contract_specifier.skill` 為 `none`／空，`$BOUNDARY_DELTA.contracts` **必須**為空；非空即視為 ownership 違規 **STOP**。
- **不可重 serialize**：specifier 寫完後，本 skill **不得**讀回 contract 檔再 re-render 或補欄位；下一輪修改也須再經 DELEGATE。

# 反例

- 在 `/aibdd-plan` 內直接 WRITE `contracts/orders.yml`，內容是手刻 `operations:` YAML——bypass specifier，違反 ownership。
- 一次 DELEGATE 同時帶 3 個 operation slice，期待 specifier 自行拆——specifier 之契約是「一次處理一個 operation」，多 slice 包裝會讓推理失焦。
- payload 缺 `source_refs`，導致 specifier 寫出的 contract 失去 atomic rule traceability，下游 DSL `source_refs.contracts` 無法 anchor。
- `operation_contract_specifier.skill = none` 但 `$BOUNDARY_DELTA.contracts` 仍含 entry——表示本 boundary 不該有 operation contract，繼續寫即為違規。

# 禁止自生

- **不得**自填 raw 未授權之 HTTP method／status code／path 樣式；endpoint／method 必須在 atomic rule 或 activity step 中找得到原文依據（rule 寫「建立會員」→ method/path 由 specifier 從契約上下文決定，本 skill 之 payload **不**自決 `POST /members`）。
- **不得**自加 raw 未提之 errors／status code 集合；錯誤分類必須對應 atomic rule 之「後置（回應）」rule。
- **不得**自加 raw 未授權之 request input；payload 之 fields 集合必須對齊 atomic rule 之「前置（參數）」rule。
