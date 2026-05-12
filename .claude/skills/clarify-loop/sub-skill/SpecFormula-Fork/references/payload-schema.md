# Payload Schema — SpecFormula-Fork Route

本檔只描述 **route=`specformula-fork`**（SpecFormula `fork` 工具）所需欄位與禁用規則。

先讀共通契約：[`../../../references/payload-schema.md`](../../../references/payload-schema.md)。

---

## Route-specific Required Fields

每題在 core 必填欄位之外**另外**必填：

- `located_file_type`：`feature` | `activity` | `markdown`
- `located_file_path`：workspace-relative path；檔案必須已存在
- `location`：`readGraph` 回傳 aggregate 內對應實體的 **verbatim id**（字串）

---

## Route-specific Restrictions

- **禁止** `id: OTHER` 或 `free_text: true`
- `location` **禁止** legacy / fuzzy 格式（例如 `STEP:1`、`Scenario: ...`、純 `file:line` 當 graph anchor）

---

## Incomplete Response（此 route）

若 runtime 已選定 `specformula-fork`，但 payload 不符合本檔，router **fail-fast**（不自動降級到 ask route）：

```yaml
status: incomplete
route: specformula-fork
missing:
  - "<missing located_file_type|located_file_path|location or invalid anchor>"
```

---

## Example（fork-ready）

```yaml
questions:
  - id: Q1
    kind: BDY
    context: 訪客觸發登入是新引入的子流程；現有 top-level boundary = features/checkout/
    question: 本流程歸屬 features/auth/ 還是 features/checkout/?
    options:
      - id: A
        label: features/auth/
        impact: 需新建 auth/ boundary
      - id: B
        label: features/checkout/
        impact: 保持單一 boundary
    recommendation: B
    recommendation_rationale: 訪客觸發點是加入購物車，語意上屬於購物流程守衛
    priority_score: 15
    dependencies: []
    located_file_type: activity
    located_file_path: specs/結帳/結帳.activity
    location: node_8f3a2c1b
```
