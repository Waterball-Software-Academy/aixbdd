# Rule 1 - 只補強與目前 repo 實際相關的 ignore surface

- Level: `MUST`
- Repo hygiene 只應涵蓋目前專案實際使用或即將使用的工具鏈，例如 git、Docker、ESLint 與其等價 ignore surface。
- 是否相關必須依 repo 現況、`plan.md`、`techstack.md`、設定檔存在與否等訊號判斷，不得任意擴張到無關工具。
- 若不存在對應工具鏈，就不應為了形式完整而建立多餘 ignore 檔。

## Good Example

- 這個例子是好的，因為它只補強目前真的會用到的 ignore 面。

```md
repo 是 git repo，且前端會用到 ESLint。
agent 檢查 `.gitignore` 與 `.eslintignore` / `eslint.config.*` 的忽略設定，但不額外建立 `.terraformignore`。
```

## Bad Example

- 這個例子是壞的，因為它把 hygiene 變成無邊界的樣板灌入。

```md
agent 一進 repo 就建立 `.gitignore`、`.dockerignore`、`.eslintignore`、`.npmignore`、`.terraformignore`、`.helmignore`，即使專案根本沒有那些工具鏈。
```

# Rule 2 - 已有 ignore 檔時只能增補缺少的關鍵項目，不得覆寫既有規則

- Level: `MUST`
- 若 ignore 檔已存在，應先保留使用者既有內容，只補上明顯缺失且與目前技術棧直接相關的關鍵 pattern。
- 不得為了追求整齊或統一格式而重寫整份 ignore 檔，也不得刪掉使用者自定義條目。
- 新增的 pattern 應聚焦在實際會污染 repo 或產物的項目，例如 `node_modules/`、`dist/`、`build/`、`.env*`、coverage 或 tool cache。

## Good Example

- 這個例子是好的，因為它以增補為主，不破壞既有規則。

```md
`.gitignore` 已存在，但少了 `node_modules/` 與 `.env*`。
agent 保留原內容，只在適當位置補上缺少的關鍵 pattern。
```

## Bad Example

- 這個例子是壞的，因為它把使用者原本整理好的 ignore 規則整份洗掉重寫。

```md
agent 發現 `.gitignore` 不夠完整，就用一份新的通用 Node 模板直接覆蓋原檔。
```

# Rule 3 - Repo hygiene 應盡量前置，但不得壓過主任務節奏

- Level: `SHOULD`
- Repo hygiene 應在 setup / toolchain 類 task 前後優先處理，或在新工具鏈首次引入時一起補強。
- 若目前 task 與 ignore surface 毫無關聯，且 hygiene 不影響後續執行，可延後到適合的節點，不必為了形式中斷主流程。

## Good Example

- 這個例子是好的，因為它把 hygiene 放在自然的節點處理。

```md
agent 在初始化前後端 workspace 前先補 `.gitignore`，之後在引入 Docker 時再補 `.dockerignore`。
```

## Bad Example

- 這個例子是壞的，因為它把每一輪 task 都切出去重新審查所有 ignore 檔，打亂主流程。

```md
agent 每完成一個 UI task 都重新全面檢查所有 ignore 檔，導致真正的實作節奏反而被 repo hygiene 反覆打斷。
```
