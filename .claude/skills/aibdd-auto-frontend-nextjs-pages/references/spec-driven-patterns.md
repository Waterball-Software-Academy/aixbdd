# 規格驅動開發模式

## 目標

從 Gherkin Feature Files 和 Activity Diagrams 中提取 UI 需求，
系統性地轉換為 React 頁面元件的具體實作。

## Feature File → UI 元素對照表

### Background Data Table → 資料結構

Feature 的 `Background:` 區塊定義了實體的資料欄位：

```gherkin
Background:
  Given 系統中存在以下記錄:
    | record_id | title   | email              | status  |
    | R001      | 內容A   | test@example.com    | 已發布   |
```

**轉換規則**：

| Data Table 欄位 | UI 元素 |
|----------------|---------|
| 所有欄位 | Table 的欄位定義 |
| 可編輯欄位（排除 id、系統自動生成欄位） | Form 的輸入欄位 |
| status / state 類欄位 | Badge / Tag 元件、篩選器選項 |
| 日期類欄位 | DatePicker 或格式化顯示 |

```typescript
// Data Table → Table columns 定義
const columns = [
  { key: 'title', header: '標題' },
  { key: 'email', header: '信箱' },
  { key: 'status', header: '狀態', render: (v) => <Badge>{v}</Badge> },
]
```

### When 步驟 → 使用者操作

Feature 的 `When` 步驟定義了使用者操作：

```gherkin
When 管理者以下列資料建立記錄:
  | title   | email            |
  | 測試標題  | test@example.com |
```

**轉換規則**：

| When 動詞 | UI 操作 | React 實作 |
|-----------|---------|-----------|
| 建立 / 新增 | 表單提交 | `<form onSubmit={handleCreate}>` |
| 查詢 / 搜尋 | 搜尋或篩選 | `<SearchBar onChange={handleSearch}>` |
| 編輯 / 更新 | 表單提交（預填值） | `<form defaultValues={data} onSubmit={handleUpdate}>` |
| 刪除 | 確認刪除 | `<DeleteConfirm onConfirm={handleDelete}>` |
| 匯入 | 檔案上傳 | `<input type="file" onChange={handleImport}>` |
| 激活 / 啟用 | 操作按鈕 | `<Button onClick={handleActivate}>` |
| 推進 / 移動 | 選擇 + 確認 | `<Select> + <Button onClick={handleAdvance}>` |

### Then 步驟 → UI 回饋

Feature 的 `Then` 步驟定義了預期回饋：

```gherkin
Then 操作成功
And 回應中應包含以下記錄資料:
  | title   | email            |
  | 測試標題  | test@example.com |
```

**轉換規則**：

| Then 描述 | UI 回饋 | React 實作 |
|-----------|---------|-----------|
| 操作成功 | Toast 成功通知 | `toast.success('記錄已建立')` |
| 操作失敗 + 錯誤訊息 | Toast 錯誤通知 | `toast.error(error.message)` |
| 回應中應包含 | 清單更新 / 頁面跳轉 | `router.push()` 或 `mutate()` |
| 回應中不應包含 | 項目從清單移除 | `setData(prev => prev.filter(...))` |
| 驗證錯誤 | 欄位錯誤提示 | `<span className="error">{error}</span>` |

### Rule → 驗證邏輯

Feature 的 `Rule:` 區塊定義了業務規則：

```gherkin
Rule: 信箱不可重複
  Scenario: 使用已存在的信箱建立名單
    When 管理者以下列資料建立名單:
      | email            |
      | existing@test.com |
    Then 操作失敗
    And 錯誤訊息為「信箱已被使用」
```

**轉換規則**：

| Rule 類型 | UI 實作 |
|-----------|---------|
| 必填欄位 | `required` 屬性 + 空值檢查 |
| 格式驗證（信箱、手機） | 正則表達式驗證 |
| 唯一性 / 重複檢查 | API 呼叫後顯示錯誤 |
| 狀態限制（某狀態才能操作） | 按鈕 disabled + Tooltip 說明 |
| 權限限制 | 條件渲染，隱藏或禁用元件 |

## Activity Diagram → 頁面導航

### STEP → 頁面路由

每個 `[STEP]` 對應一個使用者可見的頁面或操作：

```
[STEP:1] @管理者 {specs/features/{{MODULE}}/ImportRecords.feature}
→ /{{MODULE}} 頁面的「匯入」功能（Modal 或子頁面）

[STEP:2] @管理者 {specs/features/{{MODULE}}/QueryRecords.feature}
→ /{{MODULE}} 頁面的主體（表格 + 搜尋）
```

### DECISION → 條件渲染

Activity 的 `[DECISION]` 對應 UI 上的條件分支：

```
[DECISION:3a] 該階段是否有 Automation
  [BRANCH:3a:有] → 顯示「自動化執行中」狀態區塊
  [BRANCH:3a:無] → 顯示「未設定自動化」提示
```

**React 實作**：

```tsx
{hasAutomation ? (
  <AutomationStatus logs={automationLogs} />
) : (
  <EmptyState message="此階段未設定自動化" />
)}
```

### STEP 序列 → 導航流程

Activity 的 STEP 順序暗示了頁面間的導航路徑：

```
STEP:1（建立專案）→ STEP:2（設定階段）→ STEP:3（匯入名單）
```

**React 實作**：操作完成後自動導航到下一步：

```typescript
async function handleCreateProject(data: CreateProjectRequest) {
  const result = await createProject(data)
  // 成功後導航到設定階段
  router.push(`/projects/${result.id}/settings`)
}
```

## 頁面類型模板

### 清單頁（List Page）

**觸發 Feature**：含「查詢」、「清單」、「列表」語意的 Feature

```tsx
// 基本結構
export default function RecordsPage() {
  const [records, setRecords] = useState<RecordResponse[]>([])
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => { fetchRecords() }, [search])

  return (
    <div>
      <PageHeader title="資料管理">
        <Button onClick={openCreateModal}>新增記錄</Button>
        <Button onClick={openImportModal}>匯入</Button>
      </PageHeader>

      <SearchBar value={search} onChange={setSearch} />

      {isLoading ? (
        <LoadingSpinner />
      ) : records.length === 0 ? (
        <EmptyState message="尚無資料內容" />
      ) : (
        <RecordTable records={records} onEdit={...} onDelete={...} />
      )}

      <Pagination ... />
    </div>
  )
}
```

**對應 Feature 的映射**：
- `Background:` data table → Table 欄位
- `When 查詢` → SearchBar + 篩選邏輯
- `When 建立` → 新增按鈕 + CreateModal
- `When 刪除` → 刪除按鈕 + DeleteConfirm
- `Then 回應中應包含` → Table 資料呈現

### 表單頁（Form Page / Modal）

**觸發 Feature**：含「建立」、「新增」、「編輯」語意的 Feature

```tsx
export function RecordForm({ defaultValues, onSubmit }: RecordFormProps) {
  const [formData, setFormData] = useState(defaultValues || initialValues)
  const [errors, setErrors] = useState<Record<string, string>>({})

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    // 前端驗證（來自 Rule）
    const validationErrors = validateRecord(formData)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }
    await onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input
        label="標題"
        value={formData.title}
        onChange={...}
        error={errors.title}
        required
      />
      <Input
        label="信箱"
        value={formData.email}
        onChange={...}
        error={errors.email}
        required
      />
      <Button type="submit">儲存</Button>
    </form>
  )
}
```

**對應 Feature 的映射**：
- `When` data table 的欄位 → Form 的 Input 欄位
- `Rule` 的驗證場景 → `validateLead()` 函式
- `Then 操作失敗 + 錯誤訊息` → `setErrors()` 顯示欄位錯誤

### 詳情頁（Detail Page）

**觸發 Feature**：含「檢視」、「詳情」語意的 Feature，或 Activity 中綁定多個 Feature 的 STEP

```tsx
export default function RecordDetailPage({ params }: { params: { recordId: string } }) {
  const [record, setRecord] = useState<RecordResponse | null>(null)

  useEffect(() => { fetchRecord(params.recordId) }, [params.recordId])

  if (!record) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <PageHeader title={record.title}>
        <Button onClick={handleEdit}>編輯</Button>
        <Button variant="danger" onClick={handleDelete}>刪除</Button>
      </PageHeader>

      <DetailCard>
        <DetailRow label="信箱" value={record.email} />
        <DetailRow label="狀態" value={<Badge>{record.status}</Badge>} />
      </DetailCard>

      {/* 來自 Activity DECISION 的條件區塊 */}
      {record.hasAutomation && <AutomationStatus ... />}
      {record.hasSOP && <SOPTaskList ... />}

      <ActivityTimeline events={record.events} />
    </div>
  )
}
```

## 錯誤處理模式

### API 錯誤 → UI 回饋

從 Feature 的錯誤場景推導錯誤處理：

```gherkin
Scenario: 建立名單失敗 — 信箱重複
  When ...
  Then 操作失敗
  And 錯誤訊息為「信箱已被使用」
```

**React 實作**：

```typescript
async function handleCreate(data: CreateRecordRequest) {
  try {
    await createRecord(data)
    toast.success('記錄已建立')
    router.push('/records')
  } catch (error) {
    if (error instanceof ApiClientError) {
      // 來自 Feature 定義的錯誤訊息
      toast.error(error.message)

      // 若有欄位級錯誤
      if (error.fieldErrors) {
        setErrors(error.fieldErrors)
      }
    }
  }
}
```

### 狀態處理層級

每個頁面元件必須處理以下狀態：

| 狀態 | 觸發條件 | UI 顯示 |
|------|---------|---------|
| Loading | API 呼叫進行中 | `<LoadingSpinner />` |
| Empty | API 返回空陣列 | `<EmptyState message="..." />` |
| Error | API 呼叫失敗 | `<ErrorState message="..." onRetry={...} />` |
| Success | 資料正常載入 | 正常內容渲染 |

## Server Component vs Client Component 決策

| 場景 | 選擇 | 理由 |
|------|------|------|
| 純資料展示（清單、詳情） | Server Component | 減少 client bundle，SSR 直出 |
| 含使用者互動（表單、搜尋、Modal） | Client Component (`'use client'`) | 需要 useState / event handler |
| 混合場景 | Server Component + Client 子元件 | 頁面層 Server，互動區塊 Client |

**實務慣例**：大多數頁面為 Client Component（因含搜尋、表單等互動），除非是純展示的 Dashboard 頁面。
