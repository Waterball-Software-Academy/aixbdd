# Boundary preset 解析

stage 4 SOP 僅需要從 `${BOUNDARY_YML}` 抽出 active boundary preset 的 `type` 字串（譬如 `web-service`、`web-frontend`）。該值會作為 `--boundary <type>` 旗標傳給 `dsl_cli`。

## 步驟

1. PARSE `${BOUNDARY_YML}` → `$boundary_type`
   - 鎖定本輪 boundary 條目（`id` / `role` 與 plan 一致），讀其 `type` 欄。
   - 可執行 preset 由此決定；不得以 arguments 內其他鍵（例如自訂 preset 別名）凌駕 boundary 宣告。

2. （選）READ boundary preset profile — `.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/profile.yml` — 供其他 phase 參考；stage 4 本身不再依賴 profile 中任何欄位來規劃 entry 結構（plugin 已自含該知識）。

## stage 4 不讀的檔

- handler 路由由 `scripts/part_to_dsl.py` 在 template 生成期構造性保證；`aibdd-red-execute` 與 SBE 透過 boundary assets（`handlers/`、`variants/`、`kits/`）消費 routing，stage 4 不參與 step→handler 分類。
- 「給定 part-kind，產哪些 handler / 多少 entry / template skeleton 長什麼樣」這套規則由 `assets/boundaries/${boundary_type}/scripts/part_to_dsl.py` 持有，stage 4 SOP 不再參與決定；plugin 在 `generate_templates` 內構造性保證 handler 與 binding scheme 合法性。

## 履約原則

每筆 DSL entry 的履約由兩處共同把關：

- **構造期**（HARNESS step 3）：plugin 在 `generate_templates` 內構造性保證每條 template 的 handler、target_part_path、binding `target` 之 URI scheme 合法（per Policy 2 / Risk R5）；core 不再 re-check handler↔scheme 對應。
- **eval 期**（HARNESS step 5）：core `dsl_cli eval` 跑 6 條 universal rules（見 SOP step 5 列表）；無 handler-specific 規則。

SEMANTIC 端的責任邊界（不得改動 plugin 寫死的欄位）見 SOP step 4.5。
