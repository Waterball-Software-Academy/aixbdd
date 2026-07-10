---
name: analyze-and-clarify
description: >
  接收 caller 交辦的一份推論結果，重讀該批次 spec.md 的原始真相（raw idea 全文與過往澄清），稽核該結果是否依所給 rule 與 example 完整且忠實轉換而成，逐條回報 violations 並標注 `fixable`（真相充分、caller 可就地修正）或 `to-clarify`（真相不足、須回頭向使用者釐清，附上可直接提問的 clarification 內容）。只稽核不修改任何檔案。
metadata:
  user-invocable: true
  source: project-level
---

# analyze-and-clarify

稽核一份已推論完成的結果：重讀該批次的原始需求真相，檢核結果是否依所給 rule 與 example 完整且忠實地自原始資訊轉換而成，並把 violations 回報給 caller。只回報 violations，不修改任何 artifact。嚴格遵照底下執行原則來執行 SOP，`# SOP` 下每一個編號項目為有序 step。

## 執行原則

1. 依序執行 `# SOP` 下的編號 step。
2. 每個 step 都不是停點；本 skill 唯一的暫停點是最後一步的回報。
3. 本 skill 只稽核不修改：不得寫入或變更 spec、feature、activity、contract、schema 或 impact matrix。
4. 實際稽核一律由受委派的單一 subagent 執行；收到 `$SUBAGENT_PROMPT` 者即稽核者本人，依該 prompt 執行、不再向下委派；本 skill 的執行者只解析輸入、委派與轉回結果，不得自行稽核，也不得篩改 subagent 回傳的 violations。
5. 稽核基準完全來自 caller 指定的 rule 與 example，不預設結果屬哪一種規格形態。

# SOP

1. 解析稽核輸入: 依據 caller 交辦的上下文以語意理解 REASONING 下列四項輸入，不依賴固定欄位名或呼叫格式。

   1.1 稽核對象：哪一個 plan package、哪一個需求批次的推論結果，綁為 `$PLAN_PACKAGE_SLUG` 與 `$BATCH_NO`。

   1.2 推論目的：caller 依什麼原始資訊推論、要產出什麼結果，含該結果須滿足的整體完整性條件（例：每個需求段落都要被涵蓋），綁為 `$AUDIT_PURPOSE`。

   1.3 稽核基準：caller 指定作為基準的 rule 與 example 檔案路徑，綁為 `$AUDIT_BASIS`。

   1.4 待稽核結果：該結果的完整內容本身，綁為 `$AUDIT_RESULT`。

2. 綁定 `${PLAN_SPEC}`: EXECUTE command 以 resolver 綁定 `${PLAN_SPEC}`，輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   PLAN_SPEC=${PLAN_SPEC}
   EOF
   ```

3. 委派單一 subagent 稽核

   3.1 READ `analyze-and-clarify/assets/templates/subagent-prompt.template.md`，將 `$PLAN_PACKAGE_SLUG`、`$BATCH_NO`、`$AUDIT_PURPOSE`、`$AUDIT_BASIS`、`$AUDIT_RESULT` 與 `${PLAN_SPEC}` 填入其佔位符作為 `$SUBAGENT_PROMPT`；本 skill 每一次被呼叫都必須重新執行本 step、以當輪輸入重新填模板，不得沿用先前輪次的 `$SUBAGENT_PROMPT`；稽核角度與 violation 構成已定義於模板，不得增刪改寫。

   3.2 用執行環境提供的 subagent 能力（例：Task／Agent 或等效工具）DELEGATE 一個全新 subagent，每一次委派（含重稽）prompt 都必須是當輪組裝的 `$SUBAGENT_PROMPT` 全文，不得改寫或節錄、不得接續或重用先前的 subagent、不得夾帶 caller 或本 skill 既有的推理內容，禁止以 skill 名義委派（不得指示 subagent 執行 `/analyze-and-clarify` 或轉述本 SOP）；其回傳的 violations 聯集作為 `$VIOLATIONS`。

4. 回報稽核結果: 將 `$VIOLATIONS` 逐條回報給 caller；若 `$VIOLATIONS` 為空 則回報本輪稽核通過，不得虛列 violation。
