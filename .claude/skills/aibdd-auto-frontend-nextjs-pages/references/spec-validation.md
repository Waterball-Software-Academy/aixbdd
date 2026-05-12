# 規格校驗指南

## 校驗流程

```
1. 讀取 ${SPECS_HOME}/arguments.yml → 取得 PROJECT_ROOT、SPECS_HOME
2. 掃描 ${SPECS_HOME}/activities/*.activity
3. 掃描 ${SPECS_HOME}/features/**/*.feature
4. 判定校驗結果
```

## 校驗規則

### 規則 1：至少擇一存在

| activities 存在 | features 存在 | 結果 |
|:-:|:-:|------|
| ✓ | ✓ | 通過 — 兩者皆可參考，以 Activity 為流程骨架，Feature 為細節 |
| ✓ | ✗ | 通過 — 從 Activity 的 binding 路徑推導功能，但缺少 Feature 細節 |
| ✗ | ✓ | 通過 — 直接從 Feature 推導頁面，缺少流程全貌 |
| ✗ | ✗ | **失敗** |

### 規則 2：失敗處理

預設行為（中斷）：

```
⛔ 規格校驗失敗

找不到任何規格文件：
  - ${SPECS_HOME}/activities/ 目錄不存在或為空
  - ${SPECS_HOME}/features/ 目錄不存在或為空

請至少提供以下其一：
  1. Activity Diagram（.activity 檔案）→ 放入 ${SPECS_HOME}/activities/
  2. Feature Files（.feature 檔案）→ 放入 ${SPECS_HOME}/features/

如需從零開始，建議先執行：
  - /aibdd-form-activity 產出 Activity Diagram
  - /aibdd-form-feature-spec 產出 Feature Files
```

### 規則 3：強行通過（使用者明確要求）

當使用者明確表示「沒有規格也要繼續」時：

1. 掃描 `layout.html` 的頁面結構
2. 從 HTML 結構推測功能模組（表格 → 清單頁、表單 → 新增/編輯頁、按鈕 → 操作）
3. 從現有的 API client 函式（`src/lib/api/`）反推資料模型
4. 產出一份**推測性規格摘要**，列出假設，要求使用者確認

```
⚠️ 腦補模式啟動

以下規格為根據 layout.html 與 API client 推測，非正式規格：

推測頁面清單：
1. /projects — 從 layout.html 的 <table id="project-list"> 推測為專案清單頁
2. /leads — 從 layout.html 的 <form id="lead-form"> 推測為名單管理頁

推測功能：
- createProject() → 專案建立表單
- listLeads() → 名單查詢清單

⚠️ 以上皆為推測，實作後需人工驗證。
```

## 校驗產出

校驗通過後，產出**規格清單摘要**供後續 Phase 使用：

```
規格清單：

Activities（流程骨架）：
  1. 名單管理.activity — 5 個 STEP, 1 個 DECISION
  2. 名單激活.activity — 5 個 STEP, 2 個 DECISION
  3. 專案管理.activity — 5 個 STEP, 無 DECISION

Features（功能細節）：
  lead/匯入名單.feature — 匯入 CSV/Excel 名單
  lead/新增名單.feature — 手動新增單筆名單
  lead/編輯名單.feature — 編輯名單基本資料
  lead/刪除名單.feature — 刪除名單（含確認）
  lead/查詢名單.feature — 搜尋與篩選名單清單
  project/建立專案.feature — 建立新專案
  ...

Layout HTML：
  layout.html — 找到 / 未找到

Test Plans（Optional）：
  名單激活.testplan.md — 4 條路線
```
