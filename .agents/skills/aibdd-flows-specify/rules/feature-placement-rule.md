# feature 落點約束

flows-specify 把 api-wise action 落成 feature 的落點須滿足下列約束。

## 約束

1. 每個 action 須歸屬到唯一一個 package
   1. 每個證據充足的 action 須歸屬到 `$PLAN_SCOPE` 中唯一一個 `added`／`related` package。
   2. 歸屬須有依據：既有待更新者沿用其來源 impact 既有 spec path 所屬 package；全新者須與某 package 的 rationale 相符。
   3. 一個 action 可合理歸入一個以上 package、或對不到任一 package 時，即為歸屬缺依據。

2. binds_feature 路徑須合法
   1. 每個 action 的 binds_feature 須為其歸屬 package 的 `${FEATURE_SPECS_DIR}/<NN>-<action-slug>.feature`，`<NN>` 為該 package 內兩位數序號。
   2. `.activity` action 節點與 `.feature` 須一一對應，一個 binds_feature 不得同時承接多個 action。
