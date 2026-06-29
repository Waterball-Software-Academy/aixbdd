# 模組化切檔與 $ref

## 典型檔案

- **`common.api.yml`**：`ErrorResponse`、跨 slice 共用 DTO、通用列舉（`$ref` 片段、非獨立 OpenAPI 文件）
- **`main.api.yml`**（或依 `slice_list` 命名的多檔）：路徑與該 slice 專屬 schema

## 相對引用

- 同目錄：`common.api.yml#/components/schemas/ErrorResponse`
- 跨檔 schema：`./other-slice.api.yml#/components/schemas/Foo`
- 單檔內：`#/components/schemas/Foo`

驗證或 lint 時應以**目錄 context** 跑 bundler（例如 Redocly／Swagger CLI），避免只單檔檢查導致 `$ref` 全紅。

## 切檔由誰決定

- `slice_list` 與每個 slice 的 `target_path` **只**能來自 Planner／推理包；本 skill **不自決**切檔粒度。
- 若某 boundary 同時有「公開 API」與「僅測試用」路徑，應在推理包註記是否分檔或分 tag，但路徑仍須符合 `command-resource.md` 與 `anti-patterns.md`。

## info 區塊

- 每個 slice 檔案的 `info.title`／`description` 應反映該 slice 的 scope，避免多份 swagger 看起來像重複的「全系統」。
