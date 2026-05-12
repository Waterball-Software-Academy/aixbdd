# OpenAPI 格式、型別推斷與命名規則

## api.yml 格式

OpenAPI 3.0.0：

```yaml
openapi: 3.0.0
info:
  title: <系統名稱>
  version: 1.0.0

paths:
  /<resource>:
    post:
      operationId: <camelCase>
      summary: <中文功能名>
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/<RequestBody>'
      responses:
        '200': { $ref: '#/components/schemas/<Response>' }
        '400': { $ref: '#/components/schemas/Error' }

components:
  schemas:
    Error:
      type: object
      required: [message]
      properties:
        message: { type: string }
```

## Endpoint Path 命名規則

- 資源名稱：kebab-case，複數形式（`/orders`、`/video-progresses`）
- 巢狀資源：`/courses/{courseId}/progress`
- 避免動詞出現在 path（用 HTTP Method 表達動詞）

## Response Status Code 對應

| .feature Rule 類型 | 失敗情境 | Status Code |
|-------------------|---------|-------------|
| 前置（狀態）失敗 | 資源不存在 | `404` |
| 前置（狀態）失敗 | 業務規則不滿足 | `422` |
| 前置（參數）失敗 | 參數缺少或格式錯誤 | `400` |
| 權限不足 | 角色無權限 | `403` |

## 型別推斷規則

| 範例值 | 推斷型別 |
|--------|---------|
| `1`、`42` | `integer` |
| `45000.5` | `number` |
| `"Alice"` | `string` |
| `true`、`false` | `boolean` |
| `2026-01-01` | `string` (format: date) |
| `2026-01-01T00:00:00Z` | `string` (format: date-time) |
| 有限值域 | `string`（搭配 `enum`） |

## 便條紙規則

YAML 行尾 comment：`# CiC(<CATEGORY>): ...`

完整格式定義見 `../../aibdd-form-activity/references/cic-format.md`。

| 代碼 | 何時標記 |
|------|---------|
| `GAP` | 無法從 .feature 推斷 HTTP Method 或 Path |
| `ASM` | 推斷了 enum 值域但不確定完整性 |
| `AMB` | 同操作可能多種 HTTP Method（PUT vs PATCH） |
