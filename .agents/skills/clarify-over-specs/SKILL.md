---
name: clarify-over-specs
description: 在 `/specify` 產出 `spec.md` 後，主動掃描整份 spec 的高影響需求缺口；若仍有會影響規格正確性、驗收標準或 readiness 的問題，先委派 `/clarify` 訪談使用者，再把答案回寫到 spec、清理矛盾並回刷 checklist。Use when the user asks for post-spec requirement clarification, wants a generated spec professionally reviewed before `/plan`, or needs a spec-level clarify pass after `/specify`.
disable-model-invocation: true
---

# Clarify Over Specs

在 `spec.md` 已存在的前提下，對既有 spec artifact 進行主動式需求澄清。先對齊目標 `spec.md` 與 `checklists/requirements.md`，再以全 spec 掃描方式盤點高影響缺口，只把真正會改變規格正確性、驗收標準、故事邊界、資料模型、NFR 邊界或後續 readiness 判定的問題升級給 `/clarify`；資訊收斂後，將答案整合回 spec、清理矛盾與術語漂移，並同步更新 checklist 與完成回報。

# SOP

## Phase 1 -- 對齊目標 spec 與回寫範圍

1. READ 讀取使用者需求、呼叫者要求、當前上下文、任何顯式覆寫參數，以及目前 feature 的 `spec.md` 與 `checklists/requirements.md`；確認本次要澄清的 spec 目標、是否存在 checklist、是否需要詳記完成回報。若找不到目標 `spec.md`，停止並要求使用者先執行 `/specify` 或明確指定目標 spec 路徑。
2. THINK 若需要決定目標 `SPEC_FILE`、`CHECKLIST_FILE` 與覆寫優先順序，先讀取 `rules/目標spec定位與覆寫優先順序判準.md`，再依其要求收斂本次目標檔案與回寫範圍。

## Phase 2 -- 掃描全 spec 高影響缺口與 clarify 策略

1. THINK 先從整份 `spec.md` 盤點會影響需求正確性、驗收可驗證性、故事切分、資料模型、NFR 邊界、術語一致性或 readiness 判定的模糊、矛盾、缺漏與未拍板決策。
2. THINK 若需要判斷哪些缺口必須升級為 `/clarify`、哪些可直接保留為 deferred 風險或留在 spec 中明示，先讀取 `rules/spec高影響缺口掃描與提問排序判準.md`，再依其要求收斂本輪最高影響的 1 至 3 個缺口、指定提問面向，以及本輪不應追問的低影響細節。
3. DELEGATE 若仍存在會改變 spec 正確性、正式驗收標準、跨故事需求邊界、關鍵資料約束、NFR 承諾或 readiness 判定的高影響缺口，呼叫 `/clarify` 先訪談使用者，指定優先提問面向為本輪已收斂的缺口，並要求本輪只處理 1 至 3 題；未收斂前停止，不自行假設答案。

## Phase 3 -- 將澄清結果整合回 spec

1. READ 讀取 `/clarify` 產出的已確認決策、使用者補充與剩餘風險，確認哪些答案需要回寫到 `spec.md`，哪些缺口仍應保留為 deferred 或 `NEEDS CLARIFICATION`。
2. THINK 若需要判斷答案應寫回哪些 section、哪些舊敘述應被替換或刪除、哪些術語需要統一，先讀取 `rules/spec回寫位置與矛盾清理判準.md`，再依其要求收斂本次要更新的 section、矛盾清理方式與術語統一策略。
3. WRITE 依思考結果更新 `SPEC_FILE`，把已確認答案整合進對應 section，清理被新答案推翻的舊敘述與術語漂移；若仍有高影響缺口未解，明示保留狀態與後續建議，不以腦補補完。

## Phase 4 -- 回驗 spec 與 checklist

1. THINK 若需要判斷哪些 checklist 項應切換狀態、哪些 section 已達到 ready、以及完成回報應呈現哪些更新結果，先讀取 `rules/checklist回刷與完成報告判準.md`，再依其要求收斂本次 checklist 更新、ready 判定、deferred 風險與完成回報重點。
2. WRITE 若 `CHECKLIST_FILE` 存在，依思考結果只更新實際狀態有變化的 checkbox，保留其餘內容不動；若本次沒有 checklist，跳過此步但保留對 ready 狀態的明示說明。
3. READ 回頭檢查 `SPEC_FILE`、`CHECKLIST_FILE`（若存在）與本輪已確認答案是否一致，且沒有遺留被本輪答案推翻的舊敘述、重複規格或衝突結論；若不一致，立即修正。

## Phase 5 -- 交付結果與後續 handoff

1. WRITE 先讀取 `templates/clarify-over-specs-report.md` 與 `templates/clarify-over-specs-report.example.md`，再依其要求向使用者回報本次目標 `SPEC_FILE`、是否進入 `/clarify`、實際處理的高影響缺口、更新 section、checklist 變化、仍 deferred 的風險，以及建議下一步應直接進 `/plan` 或稍後再執行一次 `/clarify-over-specs`。
