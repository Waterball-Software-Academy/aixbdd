---
name: constitution
description: 依使用者需求，以最小、可逐步增量的方式建立或修改模組化憲法。先定位要改的憲法檔，再只對必要的根憲法、共用規則或特定 skill artifact 規則做訪談、收斂與寫入。Use when the user asks to create, split, refine, or extend the modular constitution under `.agents/constitution/`.
disable-model-invocation: true
---

# Constitution

將使用者對 artifact 規範的需求轉成 `.agents/constitution/` 下的最小憲法變更。優先重用
既有 `CONSTITUTION.md`、`shared.md` 與 `skills/<skill>/<artifact>.md`；只有在需求真的
新增治理邊界或新增 artifact 時才建立新檔。若缺口會改變規則落點、適用範圍或規則強度，
先訪談使用者，不自行補完。

# SOP

## Phase 1 -- 定位本次要改的憲法檔

1. READ 讀取使用者需求與 `.agents/constitution/` 現況，確認本次是新增、修改或拆分規則，並收斂候選目標檔為 `CONSTITUTION.md`、`shared.md` 或 `skills/<skill>/<artifact>.md`。
2. READ 若需要判斷規則應落在 shared、根憲法或某個 skill artifact，讀取 `rules/目標檔定位與規則落點判準.md`，再依已載入規則收斂本次最小修改面。
3. THINK 列出本次真正需要新增或修改的檔案；若某條需求不影響現有憲法結構，避免擴張到其他檔案。

## Phase 2 -- 收斂高影響缺口並訪談使用者

1. THINK 先從需求中判斷是否存在會改變規則落點、適用 skill、適用 artifact、規則強度或是否需要新檔的高影響缺口。
2. READ 若需要判斷哪些缺口必須先問，讀取 `rules/高影響缺口與最小訪談判準.md`，再依其要求收斂本輪 1 至 3 題。
3. DELEGATE 若仍有高影響缺口，呼叫 `/clarify`，指定提問面向為規則落點、適用 artifact、硬性程度與是否增量修改；未收斂前停止，不自行假設答案。

## Phase 3 -- 撰寫最小憲法增量

1. THINK 依已確認需求決定本次應修改 `CONSTITUTION.md`、`shared.md` 或單一 `skills/<skill>/<artifact>.md`；若新增 skill artifact 規則檔，沿用既有檔名慣例與 RuleFile 結構。
2. READ 若需要控制改動範圍與避免過度撰寫，讀取 `rules/最小增量與必要覆寫判準.md`，再依其要求只保留支撐本次需求的最小規則集合。
3. WRITE 更新目標憲法檔；若新增或修改 artifact 規則，沿用 `Applies To`、`## Rule N - ...`、`- Level:`、`### Good Example`、`### Bad Example` 的既有格式。
4. READ 回頭檢查是否只動到必要檔案、是否沒有把流程責任寫進 artifact 憲法，以及 shared / skill 落點是否一致；若不符合，立即修正。

## Phase 4 -- 交付與後續 handoff

1. WRITE 向使用者回報本次新增或修改的憲法檔、每個檔新增或調整的規則、是否進行 `/clarify`，以及哪些需求被刻意 defer 到未來 skill 或 artifact。
2. WRITE 若後續還需要把某個 skill 接上憲法讀取流程，明示應由 `/skill-engineering` 或對應 skill 編修接續，不在本 skill 內自動擴張實作。

## Additional Resources

- 規則落點判準：`rules/目標檔定位與規則落點判準.md`
- 最小訪談判準：`rules/高影響缺口與最小訪談判準.md`
- 最小增量判準：`rules/最小增量與必要覆寫判準.md`
