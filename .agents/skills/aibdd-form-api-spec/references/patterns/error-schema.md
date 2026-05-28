# Error schema（OpenAPI）

## 統一型別

- 元件名稱固定：`ErrorResponse`
- 放置位置：`common.yml`（或 slice 約定之共用檔）的 `components.schemas`
- **必填欄位**：`message`（`string`）、`code`（`string` 或分類用短碼）

範例：

```yaml
ErrorResponse:
  type: object
  required: [message, code]
  properties:
    message:
      type: string
    code:
      type: string
```

## 引用方式

各 operation 的 `400`／`403`／`404`／`422` 等應在 `content.application/json.schema` 使用相對路徑引用，例如：

```yaml
$ref: common.yml#/components/schemas/ErrorResponse
```

## 與 status code 的搭配

- **`400`**：`code` 可對應 `invalid_argument`、`validation_error` 等（專案內部命名表由推理包或 constitution 約定）
- **`403`**：身分正確但**不容許**此操作（與「規則上此刻不能做」的 `422` 分離；若專案選擇合併，全檔必須一致）
- **`404`**：路徑主體資源不存在（房間、訂單等）
- **`422`**：前置條件／狀態機不允許（庫存不足、回合錯誤、非輪到者出手等）

不在 message 內嵌票號或外部追蹤代號；錯誤文案描述**當下可驗證的規則**即可。
