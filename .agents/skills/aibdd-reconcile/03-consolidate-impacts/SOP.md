# SOP

1. 解析 arguments: EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   EOF
   ```

2. 載入 CLI 手冊: READ `aibdd-core/references/impact-matrix/cli-usage.md` 內容，取得通用規則、資料模型、status 語意與各 verb 應用 command。

3. 盤點需重建的 impact

   3.1 EXECUTE command 以 `read`（無 filter）讀出 `${IMPACT_MATRIX_YML}` 全部 impact 作為 `$CURRENT_MATRIX` 並對使用者輸出。

   3.2 依據 `$CURRENT_MATRIX` REASONING `$SPEC_ENTRIES`：把每個 impact 的每個 spec 攤平為一筆 `{ owner, spec_path, impact_id, spec_status }`。

   3.3 依據 `$SPEC_ENTRIES` REASONING `$DUP_KEYS`：以 `(owner, spec_path)` group by 統計各自出現於幾個 impact，取數量大於 1 者，數量為 1 者忽略。

   3.4 依據 `$DUP_KEYS`、`$SPEC_ENTRIES` 與 `$CURRENT_MATRIX` REASONING `$REBUILD_IMPACT_IDS`：取「含任一 `$DUP_KEYS` 之 impact」與「`specs` 多於一個之 impact」兩者的 impact id 聯集。

   3.5 依據 `$REBUILD_IMPACT_IDS` 與 `$SPEC_ENTRIES` REASONING `$REBUILD_KEYS`：取 `$REBUILD_IMPACT_IDS` 所有 impact 內出現過的所有 `(owner, spec_path)` 聯集。

4. 重建為單一 spec 的 impact: 對 `$REBUILD_KEYS` 每個 `(owner, spec_path)` 執行下列 CLI command，任一回 ok 為 false 即 STOP 並對使用者輸出其 violations

   4.1 EXECUTE command `write --owner <owner> --quote <quotes> --rationale <rationale> --spec <spec_path>` 新建一個只含該 spec 的 impact，其產生的 id 作為 `$NEW_ID`；由 `quote` 傳入該 `(owner, spec_path)` 在 `$REBUILD_IMPACT_IDS` 所有 impact 的 quotes 聯集，綁為 `$MERGED_QUOTES`；`rationale` 依據 `$MERGED_QUOTES` 新的 quotes 以一句話說明此 impact 在該 owner 下為何要產生該 spec。

   4.2 若該 `(owner, spec_path)` 在 `$CURRENT_MATRIX` 原各 impact 的 spec status 皆為 consistent，EXECUTE command `transit-status --id <$NEW_ID> --spec <spec_path> --status consistent`。

5. 刪除原 impact: 對 `$REBUILD_IMPACT_IDS` 每個 id EXECUTE command `remove --id <id>`，command 回 ok 為 false 即 STOP 並對使用者輸出其 violations。
