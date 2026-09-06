# Phase 0 技術堆疊總結：照片日期相簿整理

## 技術堆疊總覽

### 前端

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 建置工具 | `Vite` | 本地開發與前端建置 |
| UI 技術 | `HTML` / `CSS` / `JavaScript` | 頁面結構、樣式與互動 |
| 拖放互動 | `HTML Drag and Drop API` | 同日期相簿內的照片排序 |

### 後端

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 執行環境 | `Node.js` | 後端執行環境 |
| HTTP 框架 | `Express` | API 路由與伺服器處理 |
| 上傳處理 | `multer` | 多檔照片上傳 |

### 資料與媒體處理

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 資料庫 | `MySQL` | 儲存相簿、照片與排序資料 |
| ORM / Schema | `Prisma` | schema、migration 與資料模型存取 |
| EXIF 解析 | `exifr` | 讀取拍攝日期 |
| 縮圖處理 | `sharp` | 產生縮圖與圖片處理 |

### 測試與驗證

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 前端 BDD techstack | `Playwright` | webapp E2E，跑前端 Gherkin |
| 後端 BDD techstack | `behave` | 後端 E2E，跑後端 Gherkin，驗 API 與權威狀態 |

## 本次開發不引入的技術

- `React` 或其他前端框架
- 第三方拖放套件（如 `SortableJS`）
- 檔案系統路徑式圖片儲存
