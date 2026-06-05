# SOP — 02 expand each rule

對 phase 1 產出的 `$rules_to_expand` 每筆 Rule，套對應 pattern 模板、推導 5 元素、補完 Example，最後 UPDATE 回原 `.feature` 檔。

0. RESOLVE arguments——沿用 Phase 1 已 EMIT 之 binding；若缺失則重跑 resolver（manifest 同 `01-scan-and-classify/SOP.md` 步驟 0）。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

1. FOR EACH `$rule` in `$rules_to_expand`：依以下 step 2..7 逐筆處理；單筆失敗不影響其他筆，失敗者記錄到 `$blocked_rules` 供 phase 3 收口。

2. DERIVE `$template_path` 自 `$rule.pattern_label`：
    - `PATTERN_A_PRECONDITION_INPUT` → `templates/pattern-a-precondition-input.template.md`
    - `PATTERN_B_PRECONDITION_STATE` → `templates/pattern-b-precondition-state.template.md`
    - `PATTERN_C_POSTCONDITION_STATE` → `templates/pattern-c-postcondition-state.template.md`
    - `PATTERN_D_POSTCONDITION_RESPONSE` → `templates/pattern-d-postcondition-response.template.md`

3. READ `$template_path`：取得 Given/When/Then 骨架、必填元素清單、pattern 引導一句話。本步只讀模板，不寫檔。

4. DERIVE `$five_elements`（5a 自動推導）：依 `rules/five-elements-mapping.md` 規則，從 `$rule.feature_title` 與 `$rule.rule_title` 文字推導出：
    - `$aggregate`（業務實體 + 業務序號）
    - `$command`（執行動作，顧客視角動詞）
    - `$event`（後置成功必填，業務化通知名；前置失敗填「無」）
    - `$actor`（觸發者，人物名）
    - `$input`（PATTERN_A 必填，其他 pattern 可選）
    自動推導不出來者標記為 `$five_elements.<key> = null`。所有推出之值必為業務語言（依 `rules/business-language-judgments.md` 之 5 維度判準）；技術 ID／英文 enum／API 視角動詞禁止直接填入。本步只產出 in-memory 結構，不寫檔。

5. IF `$five_elements` 任一元素為 `null` 或不符業務語言判準（5b 補問）：DELEGATE 詢問用戶，問句必為該 pattern 模板的「引導一句話」加上缺漏元素名（例：PATTERN_A 缺 `$input` → 問「哪個輸入沒選／沒填？」）。用戶回覆後回填 `$five_elements`；禁止自行猜值或用技術 ID 暫填。

6. THINK：套用 `rules/skeleton-vs-semantics-tradeoff.md` 的取捨守則 — 若 `$command` 與 Given 中其他元素為同一觸發動作或無業務區別力，DERIVE `$omit_elements` 清單並記下取捨原因 `$omit_reason`。本步只產出判斷，不寫檔。

7. UPDATE `$rule.feature_file`：在 `$rule` 對應的 Rule body 下方插入一個 Example block，內容自 `$template_path` 之 Given/When/Then 骨架與 `## Good` 示範取代 placeholder 為 `$five_elements` 之值。Rule 的「類型前綴」已在 phase 1 確認（併在 `Rule:` 標題開頭、以 ` - ` 分隔業務標題），Example 不帶前綴（前綴僅屬 Rule 標題層），不得在 Example 另加前綴。依 `$omit_elements` 刪去重複元素、於 Example 上方加註解 `# 取捨：<$omit_reason>`（若有）。本步僅允許 UPDATE 該 `.feature` 檔之對應 Rule body，禁止修改其他 Rule、其他 Feature 或建立新檔；禁止在本步執行 phase 3 的 cucumber 字面檢核。

8. ASSERT 本筆 Rule 已寫入 Example 後，繼續處理下一 `$rule`；全部處理完後產出 `$expanded_rules` 與 `$blocked_rules` 兩份 in-memory 清單，傳遞給 phase 3。本步僅允許 in-memory 傳遞，禁止建立中介檔。
