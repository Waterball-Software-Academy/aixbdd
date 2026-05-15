# OpenAPI 格式、型別推斷與命名規則

## api.yml 骨架（語法合法）

OpenAPI 3.0.x。`responses` 必須使用 `description`，錯誤回應在 `content.application/json.schema` 內引用 schema，**不可**把 `200` 直接 `$ref` 到 schema 根（那是無效寫法）。

```yaml
openapi: 3.0.0
info:
  title: <系統名稱>
  version: 1.0.0

paths:
  /<resource-collection>:
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
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/<ResponseBody>'
        '400':
          description: 參數或格式錯誤
          content:
            application/json:
              schema:
                $ref: common.yml#/components/schemas/ErrorResponse
        '404':
          description: 資源不存在
          content:
            application/json:
              schema:
                $ref: common.yml#/components/schemas/ErrorResponse
        '422':
          description: 業務規則不滿足
          content:
            application/json:
              schema:
                $ref: common.yml#/components/schemas/ErrorResponse

components:
  schemas: {}
```

共用錯誤型別與 §4／`patterns/error-schema.md` 對齊：`ErrorResponse` 至少 `message` + `code`（放在 `common.yml`）。

## Endpoint Path 命名規則

- 資源名稱：kebab-case，複數形式（`/orders`、`/video-progresses`）
- 巢狀資源：`/courses/{courseId}/lessons`
- path 以**名詞**為主；操作意圖以 **HTTP method + 資源** 表達（細部見 `patterns/rest-naming.md`、`patterns/command-resource.md`）

## Response Status Code 對應

| .feature Rule 類型 | 失敗情境 | Status Code |
|-------------------|---------|-------------|
| 前置（狀態）失敗 | 資源不存在 | `404` |
| 前置（狀態）失敗 | 業務規則不滿足 | `422` |
| 前置（參數）失敗 | 參數缺少或格式錯誤 | `400` |
| 權限不足／身分與操作對象不符 | 呼叫端不具執行權限 | `403` |

若專案統一只用 `422` 表達「不可執行」亦可在推理包註記，但仍須在整份 contract **一貫**，避免同一類失敗混用 `403` 與 `422` 卻未定義判準。

## 型別推斷規則

| 範例值 | 推斷型別 |
|--------|----------|
| `1`、`42` | `integer` |
| `45000.5` | `number` |
| `"Alice"` | `string` |
| `true`、`false` | `boolean` |
| `2026-01-01` | `string` (format: date) |
| `2026-01-01T00:00:00Z` | `string` (format: date-time) |
| 有限值域 | `string`（搭配 `enum`） |

## 便條紙規則

YAML 行尾 comment：`# CiC(<CATEGORY>): ...`

DBML／其他 DSL 交叉引用時仍沿用各自 skill 定義。完整 CiC 類別見 `../../aibdd-form-activity/references/cic-format.md`（若該檔存在於工作樹）。

| 代碼 | 何時標記 |
|------|----------|
| `GAP` | 無法從 .feature 推斷 HTTP Method 或 Path |
| `ASM` | 推斷了 enum 值域但不確定完整性 |
| `AMB` | 同操作可能多種 HTTP Method（PUT vs PATCH） |
