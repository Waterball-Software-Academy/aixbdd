# boundary-map.yml 顆粒度

- **記什麼**：boundary-level 技術路由決策且**無法由 package 結構安全推論**者——boundary-owned modules 拓樸、default dispatch inference contract、explicit `dispatch_overrides`（only 當 inference 錯時）、consumer→provider edges、`persistence_ownership`、testability anchor references。
- **不記什麼**：**逐條** atomic rule 之 ownership **不**寫進 boundary-map；rule 之歸屬已由 `packages/NN-*/features/*.feature`／package-local `dsl.yml`／`contracts/**/*.yml#operations.*` 隱含表達。
- **何時 override**：只有 4 種情境寫顯式 override — (a) cross-boundary ownership、(b) shared operation、(c) 非標準 module、(d) planning gap。其餘**一律**靠 inference contract。
- **persistence_ownership**：每個被本輪 plan 影響之 aggregate-root **必列**；下游 DSL 之 `aggregate-given`（或對應 preset 之 persistence handler）builder 由此節點 anchor。
- **不為前後相容保留**：boundary-map 為當下 boundary 真相，**禁止**寫「之前」「現在」「待替換」之 transitional 敘事或 deprecated entry。

# 反例

- 把 `packages/03-order-create/features/submit.feature` 之 atomic rule 整條搬進 boundary-map 之 `dispatch_overrides`——dispatch 已由 feature 路徑 + dsl 隱含表達，**override 只**在 inference 錯時才寫。
- 為「未來可能會分包」開預留 entry——boundary-map 為 as-is 真相，**不**為假設未來保留 slot。
- `persistence_ownership` 漏掉本輪實際被寫狀態的 aggregate-root——下游 DSL 之 persistence builder 將無 anchor，coverage gate 必 fail。
- 用 boundary-map 取代 `contracts/`／`data/`／`test-strategy.yml`——**ownership 違規**：四檔各有責任，不得替代或鏡像。

# 禁止自生

- **不得**長出 `${TRUTH_BOUNDARY_ROOT}` 下不存在的 module 名／operation id／entity 名作 dispatch target；每筆 target 必須在 contracts／data／packages 之中找得到對應出處。
- **不得**自填 `provider_edges` 之 mock policy 內容；策略 SSOT 為 `test-strategy.yml`，boundary-map 僅作 anchor reference。
- **不得**自填 SLA／retry／timeout 等 raw 未提之技術參數；boundary-map 不是運維 spec。
