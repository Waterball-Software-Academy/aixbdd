---
name: truth-delta
description: 維護每次 plan package 內的 `truth-delta.md`，讓 truth owner skill 以共同格式記錄本輪對 `specs/truth/**` 的 ADD / MODIFY / DELETE / NOOP 語意單元變更。Use when a truth owner skill has inspected or changed truth specs and must initialize, append, update, or validate the current plan package truth delta handoff.
disable-model-invocation: true
---

# Truth Delta

`truth-delta` 是 truth owner skill 的共同 handoff skill。它不決定要怎麼改 truth，也不替 owner 寫 OpenAPI、DBML、feature 或 DSL；它只負責把已確認的 truth 變更，以固定格式寫入當前 plan package 的 `truth-delta.md`，讓下游 skill 能接續推理。

# SOP

## Phase 1 -- 對齊 plan package 與 truth owner

1. READ 讀取呼叫者 handoff、當前 plan package 路徑、truth root、truth owner 名稱、已檢查或已修改的 truth 規格清單，以及既有 `truth-delta.md` 內容。
2. READ 讀取 `rules/Truth變更分類與粒度判準.md`，確認 owner section、動作分類、語意單元粒度與 NOOP 記錄規則。
3. READ 若 `truth-delta.md` 尚不存在，讀取 `templates/truth-delta.md` 與 `templates/truth-delta.example.md`，確認初始化骨架與完成樣貌。
4. WRITE 若 `truth-delta.md` 尚不存在，於當前 plan package 建立該檔案，並填入 plan package、truth root 與四個 truth owner section。

## Phase 2 -- 收斂本輪 truth 變更紀錄

1. THINK 依已載入規則，把呼叫者提供的 truth 改動整理成語意單元列；每列必須包含 `ADD`、`MODIFY`、`DELETE` 或 `NOOP`，以及 truth 規格、改動摘要與原因。
2. THINK 若呼叫者宣稱有高影響 `MODIFY` 或 `DELETE`，但 handoff 未說明已完成 `/clarify` 或明確風險決策，停止寫入並要求呼叫者先補齊確認依據。
3. THINK 若同一 truth owner 本輪沒有 truth 變更，收斂一列 `NOOP`，明示已檢查但無需變更的 truth 範圍與原因。

## Phase 3 -- 更新 owner section

1. WRITE 在 `truth-delta.md` 的對應 owner section 追加或更新本輪表格列；若該 section 仍是 placeholder 或既有 `NOOP` 已被實際改動取代，先清理再寫入。
2. READ 回頭檢查 `truth-delta.md` 是否仍保留每個 truth owner 各一張表，且所有列都符合固定欄位、動作值與語意單元粒度；若不符合，立即修正。

## Phase 4 -- 交付下游 handoff

1. WRITE 向呼叫者回報已更新的 `truth-delta.md` 路徑、owner section、ADD / MODIFY / DELETE / NOOP 數量，以及是否仍有需回到 `/clarify` 的高影響 truth 變更。
