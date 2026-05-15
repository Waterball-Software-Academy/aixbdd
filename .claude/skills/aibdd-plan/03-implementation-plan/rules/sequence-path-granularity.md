# Sequence path 顆粒度

- **計數單位**：以「**一條主要實作路徑**」為一張 `.sequence.mmd`；happy／alt／err 三類**各為獨立路徑**，**不得**塞同一檔。
- **檔名約定**：`<scenario_slug>.<category>.sequence.mmd`，`<category> ∈ {happy, alt, err}`；`<scenario_slug>` 為可讀的業務 slug（可為當地語言），與對應 activity flow／feature 主軸對齊。
- **每張 sequence 必含**：actor、boundary entry operation、internal collaborators、provider contract calls、state changes、response verifier candidates；只列舉能力或規格項而**無**控制流主軸者**不**另立。
- **traceability**：每個 actor／operation／collaborator／provider call／state change 至少能指回一條 activity flow／atomic rule／contract operation／boundary-map dispatch override；做不到則記入 `$IMPLEMENTATION_MODEL.blocked_reasons[]`，**不**靜默忽略。
- **不夾帶**：sequence 為實作計畫 artifact；**不得**含 product code patch、step definition、test queue 狀態、commit hash／PR # 等 tracking artifact。

# 反例

- 把 happy／alt／err 三條路徑合畫成一張 `submit.sequence.mmd`——讀者無法快速辨識本輪驗收主軸，下游 task 規劃無法逐路徑展開。
- 用 legacy 命名 `submit.backend.sequence.mmd`——非當前約定，gate `check_sequence_diagrams.py` 必 fail。
- 一條 sequence 含 `OrderService::calculatePrice` 但無 atomic rule／activity step 對應——traceability gap，必須回頭找依據或在 `blocked_reasons[]` 標出；**不**靜默畫上去。
- 把純查詢 dashboard 列出獨立 sequence 而 atomic rule 無對應後置狀態變化——查詢無狀態遷移者**不**另立 sequence，併入主流程之讀取段。

# 禁止自生

- **不得**畫出 raw 未授權之 internal class／function 名作 collaborator；命名要等同 code skeleton 既有 module 或 plan 已決定要新增的模組。
- **不得**為「完整性」自加 logging／metrics／tracing 互呼；那些 cross-cutting concern 不屬 atomic rule 驅動之 sequence。
- **不得**自加 raw 未提之 retry／circuit-breaker 互動；非功能需求若未在 rule 中出現，不畫進 sequence。
