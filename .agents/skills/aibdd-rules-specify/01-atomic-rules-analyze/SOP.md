# 參數設定

- **需求故事錨點** → `${PLAN_SPEC}`（`${CURRENT_PLAN_PACKAGE}/spec.md`）
- **Discovery 報告** → `${PLAN_REPORTS_DIR}/discovery-sourcing.md`（澄清擱置機讀題組：`${PLAN_REPORTS_DIR}/discovery-clarify-pending.payload.yml`）
- **Feature 規格／`.feature` 根目錄** → `${FEATURE_SPECS_DIR}`

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

0. **RESOLVE arguments**——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   EOF
   ```

1. [LOOP] FOR EACH 上游 `/aibdd-flows-specify` 產出的 Feature File - EXECUTE `steps/enumerage-atomic-rule-for-feature-file.md` 遵照裡面指示來列舉此 Feature File 所有 atomic rules （每一個 Feature File 開設一個 TODO TASK，每個 TASK 進行底下兩步驟）

2. （此步驟必須嚴格遵守，至少要有一條澄清項目）`$NEED_TO_CLARIFY`, `$NEED_TO_FIX` = DO FAITHFUL REASONING 針對所有與範疇內相關的 Feature Files 依照 `steps/derive-findings.md` 中的分析切角去進行深度分析，並找到所有需要修正、澄清的地方。

3. 若 `$NEED_TO_FIX` 非空：UPDATE FEATURE FILES: 針對所有 `$NEED_TO_FIX` 在遵守 `rules/atomic-rule-granularity.md` 的前提下，進行修正。

4. 若 `$NEED_TO_CLARIFY` 非空：針對所有 `$NEED_TO_CLARIFY`，DELEGATE /clarify-loop skill 針對每一題來進行提問。

5. 向使用者說道（語意不變、詞彙可改）：「OK，很好，每個 Feature File 對應的規則我想我們是分析完了，現在每個 Feature File 都定義好了你本次需求的所有規則，你的系統的複雜度以及之後的實作將由這些規則的驗收測試所驅動，你明白嗎？」