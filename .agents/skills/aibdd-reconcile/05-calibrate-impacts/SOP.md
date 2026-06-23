# SOP

1. 解析 arguments: EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   EOF
   ```

2. 載入 CLI 手冊: READ `aibdd-core::references/impact-matrix/cli-usage.md` 內容，取得通用規則、資料模型、status 語意與各 verb 應用 command。

3. 標記過時 spec：對 `$STALE_SPECS` 每一筆 `{ impact_id, spec_path, owner, quote, rationale }` 執行下列 CLI command；任一 command 回 ok 為 false 時依其 `violations` 修正該 command 後重試，直到 ok。

   3.1 若該筆 `quote` 或 `rationale` 較 `$CURRENT_MATRIX` 現值有更新，EXECUTE command `read --id <impact_id>` 取回該 impact 全貌後 EXECUTE command `write --id <impact_id>` 以更新後的 `quotes` 與 `rationale` 取代該 impact，保留其餘既有 spec 與 quotes 不遺漏；無變化則略過。

   3.2 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status inconsistent`。

4. 新增全新 impact: 對 `$NEW_IMPACTS` 每一筆 `{ owner, quote, rationale }` EXECUTE command `write --owner <owner> --quote <quote> --rationale <rationale>` 新建一個 spec-less 的 `pending` impact；任一 command 回 ok 為 false 時依其 `violations` 修正該 command 後重試，直到 ok。
