# External boundary surface 顆粒度

- **計數單位**：以「**一條 consumer→provider edge**」為單位；每條 edge 必有 (1) provider contract reference 或顯式 non-contract reason；(2) 若 mockable 則必有 test double policy；(3) 3rd-party 必有 external stub candidate（含 payload 與 response binding source）。
- **same-boundary internal collaborator 不是 edge**：同一 boundary 內部之 class／module 互呼**不**列入 external surface，**禁止**標為 mock target。
- **failure-mode 覆蓋**：當該 edge 之行為依賴 provider failure（譬如「金流失敗則訂單回滾」），edge 上**必有** failure-mode anchor（指回對應 atomic rule 之「後置（狀態）」或「後置（回應）」）。
- **reset 行為**：每條 stub edge 必有 per-scenario reset 或 lifecycle 註記；無 reset 則跨 scenario 狀態洩漏，導致 red 端非 deterministic。
- **provider 同質性**：同一 provider 之多 operation 屬同一 edge group，**不**逐 operation 拆 edge；mock policy 以 group 為單位。

# 反例

- 把同 boundary 內 `OrderRepository → OrderService` 列為 mock edge——同 boundary 內部協作者**不**模擬，違反 external surface 定義；DSL `external-stub` 也不得指向此處。
- 第三方金流 edge 只標 contract reference，未標 failure-mode（atomic rule 明寫「失敗時回滾」）——下游 DSL 將缺 failure path stub，red 端無法測試失敗分支。
- stub edge 缺 reset policy——多 scenario 同跑會狀態互染，gate `check_external_mock_policy.py` 必 fail。
- 一條 edge 對應 `payment.charge` 與 `payment.refund` 兩個 operation 各自獨立列——應收斂為同一 edge group，mock policy 共用。

# 禁止自生

- **不得**為 raw 未授權之 provider 加 stub；每條 external edge 必須能在 boundary-map／atomic rule／activity 中找到 provider 名稱出處。
- **不得**自填 SLA／retry／timeout／circuit-breaker 等技術參數；raw 沒講就不寫，僅保留契約 anchor。
- **不得**為「完整性」自加 logging／metrics／monitoring 之 external edge；cross-cutting concerns 不屬 atomic rule 驅動之 surface。
