# State schema 疑慮分析切角

1. 目的
   1. 本檔只列出在本 skill 中，對草稿 `$STATE_TARGETS` 可能產生疑慮的分析切角。
   2. 本檔將切角分成兩類：
      1. `$NEED_TO_CLARIFY`：代表目前需求真相不足，交給當步 clarify 流程補問。
      2. `$NEED_TO_FIX`：代表目前 state 設計已可直接判定有問題，應重新推論，不必先訪談。

2. `$NEED_TO_CLARIFY`
   1. state 邊界不唯一
      1. 要看什麼：某份資料到底屬於同一 aggregate、獨立 entity、read model，還是只是 runtime artifact，不足以唯一決定。
      2. 需求訪談重點：要確認使用者真正想穩定保存、驗證或追蹤的是哪一層 truth。
      3. 例：付款授權碼不確定要成為 persisted payment state，還是只存在於 response payload。
   2. operation 與 state 的責任分界模糊（domain-membership）
      1. 要看什麼：某個需求面向到底應由 data state schema 承接，還是應由 operation contract 承接，或兩邊都要承接但當前缺少清楚分工。
      2. 需求訪談重點：要確認哪些是執行後必須留下的系統狀態，哪些是對外互動承諾，以此把責任分界問成可判定的高品質澄清題，不要把問題直接退化成「屬不屬於本 skill」。
      3. 答覆處理（跨域歸屬）：本 skill 僅持有 data domain。澄清結論若指向「系統狀態」→ 納入本 skill 建模並導成 state target；若指向「對外互動承諾（operation contract）」、或本就不屬於本 skill domain → 不納入，本 skill 不為它建任何 target，明確留給 api plan。
      4. 例：建立訂單成功後的「確認訊息」不確定是 notification state 變化，還是 response contract 保證。
   3. coverage gap（state）
      1. 要看什麼：feature truth 已明示某個執行後必須留下的系統狀態，但目前 state 整體設計沒有任何 target 承接它；若該結果可能屬 operation contract，先依切角 2 做 domain-membership 澄清。
      2. 需求訪談重點：要確認這個狀態是本輪 data 必做範圍，還是刻意不納入。
      3. 例：需求明講退款失敗要留下審計紀錄，但目前沒有任何 audit data target。
   4. conditional scope 尚無結論（state）
      1. 要看什麼：某個 state target 是否納入本輪，仍取決於尚無結論的需求決策，沒有結論前無法定其去留。
      2. 需求訪談重點：要確認這些 target 是這輪正式規劃的一部分，還是先留給後續 phase 或後續 package；結論納入者才導成 target，否則本輪不建。
      3. 例：是否把促銷推薦資料寫成正式 state schema，仍取決於這輪是否真的要支援推薦規則。
   5. 不同視角下的替代 state 設計都成立
      1. 要看什麼：從 lifecycle、actor handoff、external dependency、auditability 等不同角度重看後，出現另一套同樣合理的 state 組合。
      2. 需求訪談重點：要確認使用者偏好的設計優先序，避免 planner 只因為先想到某個角度就提前收斂。
      3. 例：同一個付款流程既可以 payment-first 建模，也可以 order-first 建模，兩者都能覆蓋目前需求。

3. `$NEED_TO_FIX`
   1. scope 外 target 被納入本 skill
      1. 要看什麼：state target 的 `target_path` 超出 `$PLAN_SCOPE`、`${DATA_DIR}` 或本輪 `$WORKLIST` impact 所允許的範圍。
      2. 如何修正：重新過濾 scope，只保留本輪授權 target 後重新推論。
      3. 例：本輪只涵蓋 checkout package，卻把 account profile 的 data target 一起切進來。
   2. target_path 不合法
      1. 要看什麼：`target_path` 落在錯目錄、帶有 `<<NN-functional-module>>` 借位、重複、或無法對應到相對 `${DATA_DIR}` 的 flat path 語意。
      2. 如何修正：重新命名與去重後重新推論。
      3. 例：state target path 被寫成 `packages/01-checkout/orders.dbml`，而不是相對 `${DATA_DIR}` 的 flat path。
   3. state 與 feature truth 明顯矛盾
      1. 要看什麼：已導出的 state schema 明顯背離 `${PLAN_SPEC}`、`${FEATURE_SPECS_DIR}` 或 activity truth 所明示的行為與結果。
      2. 如何修正：依 feature truth 重新推論對應 target。
      3. 例：feature truth 是「保存已取消訂單的狀態」，state schema 卻只建了查詢用 read model 而無取消狀態欄位。
   4. target 與驅動 impact 對映不正確
      1. 要看什麼：某 target 的 `impact_id` 指到不是驅動它的 `$WORKLIST` impact、某個 `$WORKLIST` impact 的 quotes 沒有任何 target 承接（漏做）、或 target 的 `target_path` 與它要回寫的 impact spec 對不上。
      2. 如何修正：重新比對 `$WORKLIST_QUOTES` 與各 target，修正 `impact_id` 與 `target_path` 對映、補上漏做的 target。
      3. 例：某 pending impact 的 quotes 講保存退款紀錄，`$STATE_TARGETS` 卻沒有任何 target 承接它。
   5. 同一設計問題被重複拆成多個 state target
      1. 要看什麼：本可由單一 state schema 表達的設計，被過度拆散成多個重複 target。
      2. 如何修正：去重與重組，只保留最直接承接需求真相的那組 target。
      3. 例：同一份訂單資料被拆成三份只差欄位的 schema 檔。
   6. 直接可判定的 state 缺口未補
      1. 要看什麼：feature truth 已明示某個須保存的 state 面向，但現在只是漏掉，並非需求模糊（亦非 domain-membership 不明）。
      2. 如何修正：補齊缺失 target 後重新推論。
      3. 例：需求明講建立訂單後要保存訂單狀態，但目前完全沒有 `orders` state schema。

4. 使用提醒
   1. 同一個問題可以同時命中多個切角；不要因為它已被歸進某一類，就停止從其他角度檢查。
   2. 若同一個問題同時落在 `$NEED_TO_FIX` 與 `$NEED_TO_CLARIFY` 的邊界，先問自己：目前是需求真相不足，還是當前 state 設計明顯推錯；前者歸 clarify，後者歸 fix。涉及跨 operation／data 歸屬者一律走切角 2 的 domain-membership 澄清。
