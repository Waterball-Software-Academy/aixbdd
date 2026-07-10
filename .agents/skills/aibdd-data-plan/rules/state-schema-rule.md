# state schema 約束

state schema 產出須滿足下列約束與驗收標準。operation／state 兩屬歸屬已由上游 aibdd-api-plan 統一把關，本 owner 收到即已定案屬 state。

## 約束

1. state 邊界須明確且反映真正要保存的 truth
   1. 每份要保存的資料，其歸屬層級（同一 aggregate／獨立 entity／read model／runtime artifact）須明確，且反映使用者真正想穩定保存、驗證、追蹤的 truth。
   2. 例：付款授權碼是 persisted payment state 還是只存在於 response payload，須有明確歸屬。

2. 多套等效設計時須採使用者偏好的優先序
   1. 從 lifecycle、actor handoff、external dependency、auditability 等不同角度都能覆蓋需求的 state 組合並存時，採用的設計須符合使用者偏好。

3. 本輪範疇須有依據
   1. 納入本輪的 state target 須有明確範疇依據；取決於尚未拍板的需求決策者不算。
   2. 例：是否把促銷推薦資料寫成正式 state schema，取決於這輪是否真的支援推薦規則。

4. 需求列舉須逐項納入
   1. 需求上下文內須穩定保存的欄位、狀態、紀錄等列舉，須逐項納入 schema，不得概括。
   2. 例：需求逐列列出訂單要保存的 5 個狀態值，schema 不得只給一個未列舉允許值的 status 欄位帶過。

5. target_path 須合法
   1. `target_path` 為相對 `${DATA_DIR}` 的 flat 檔案路徑，不得含 `<<NN-functional-module>>` 借位子層、不得與其他 target 重複，路徑語意依 `aibdd-core::references/ssot/spec-package-paths.md`。

6. target 與 pending impact 須雙向對映
   1. 每個 target 須指回驅動它的 pending impact。
   2. 每個 pending impact 須穩定保存的狀態須有 target 承接。

7. target 不得超出本輪授權範疇
   1. 每個 state target 須落在本輪 plan scope 與 pending impact 授權的範圍內。
   2. 例：本輪只涵蓋 checkout package，不得把 account profile 的 data target 一起切進來。

8. schema 須忠實反映 Discovery 真相
   1. 導出的 state schema 不得背離 spec.md、feature truth 與 activity truth 明示的行為與結果。
   2. 例：feature truth 是「保存已取消訂單的狀態」，不得只建查詢用 read model 而漏掉取消狀態欄位。

9. 不得重複拆分
   1. 可由單一 state schema 表達的資料，不得拆成多個只差細節的重複 target。
   2. 例：同一份訂單資料不得拆成三份只差欄位的 schema 檔。
