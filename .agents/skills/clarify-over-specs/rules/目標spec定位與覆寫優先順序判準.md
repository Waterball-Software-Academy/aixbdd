# Rule 1 - 顯式覆寫優先於任何自動推斷

- Level: `MUST`
- 若使用者、呼叫者 skill 或當前上下文已明確指定 `spec.md` 路徑、feature directory 或等價的目標 artifact，必須優先採用該顯式指定，不可再被自動推斷覆蓋。
- 顯式覆寫一旦成立，對應的 `CHECKLIST_FILE` 應以同一 feature directory 下的 `checklists/requirements.md` 為預設配對；若該檔不存在，僅回寫 spec 並在完成回報中明示 checklist 缺席。
- 不可因為 IDE 焦點、最近檔案或既有慣例看起來更常用，就忽略已明講的覆寫目標。

## Good Example

- 這個例子是好的，因為它先採用已明講的 target，再推導對應 checklist。

```md
使用者指定：
- 目標 spec：`specs/003-billing/spec.md`

決策：
- `SPEC_FILE` = `specs/003-billing/spec.md`
- `CHECKLIST_FILE` = `specs/003-billing/checklists/requirements.md`（若存在）
```

## Bad Example

- 這個例子是壞的，因為它忽略已明講的路徑，改去猜目前較像「最新」的 spec。

```md
使用者指定：
- 目標 spec：`specs/003-billing/spec.md`

決策：
- 改用最近剛打開的 `specs/004-search/spec.md`
```

# Rule 2 - 未顯式指定時，依固定順序自動定位目標 spec

- Level: `MUST`
- 若沒有顯式覆寫，目標 `SPEC_FILE` 必須依固定順序定位，不可臨場自由猜測：
  1. 本輪上游 `/specify` 剛產出的 `SPEC_FILE`
  2. 當前上下文中可唯一辨識的 feature directory 對應 `spec.md`
  3. 目前 IDE 焦點中的 `spec.md`
- 若以上來源都不存在，或出現多個候選且無法唯一判定，必須停止並要求使用者指定目標，不可自行在多個 spec 間擇一。
- 自動定位成功後，應以同目錄下的 `checklists/requirements.md` 作為預設 `CHECKLIST_FILE`；若不存在，僅視為 checklist 缺席，不視為 spec 定位失敗。

## Good Example

- 這個例子是好的，因為它用固定順序收斂唯一 target，沒有跳步猜測。

```md
條件：
- 本輪剛執行完 `/specify`
- `/specify` 已回報 `SPEC_FILE = specs/001-online-pvp-1a2b/spec.md`

決策：
- 直接沿用 `specs/001-online-pvp-1a2b/spec.md`
- 不再改看 IDE 焦點或最近檔案
```

## Bad Example

- 這個例子是壞的，因為它沒有固定優先順序，導致不同執行者可能選到不同 spec。

```md
條件：
- 沒有顯式指定
- 最近檔案有兩份不同 `spec.md`

決策：
- 看哪份內容比較像新功能就先用哪份
```

# Rule 3 - 回寫範圍只限目標 spec 與其配對 checklist

- Level: `SHOULD`
- 一旦 `SPEC_FILE` 與 `CHECKLIST_FILE` 收斂完成，本輪回寫範圍應只限這對 artifact，不延伸修改其他 feature directory、其他 checklist 或平行 spec。
- 若發現高影響缺口其實牽涉跨 spec 的產品範圍衝突，應在完成回報中明示風險，必要時要求使用者另外指定其他 artifact，而不是偷偷同步改多份文件。
- 完成回報中應明示本輪實際回寫了哪些檔案，讓使用者知道 skill 的作用邊界。

## Good Example

- 這個例子是好的，因為它把回寫限制在本輪 target，不把跨 feature 問題偷偷擴散。

```md
本輪 target：
- `specs/001-online-pvp-1a2b/spec.md`
- `specs/001-online-pvp-1a2b/checklists/requirements.md`

處理：
- 只更新這兩份檔案
- 在完成回報中註記其他 feature 也可能受影響，但未直接修改
```

## Bad Example

- 這個例子是壞的，因為它在未經使用者指定下，同步改動多個 feature 的 spec。

```md
本輪 target：
- `specs/001-online-pvp-1a2b/spec.md`

處理：
- 另外順手修改 `specs/002-ranking/spec.md`
- 也同步調整另一份 checklist
```
