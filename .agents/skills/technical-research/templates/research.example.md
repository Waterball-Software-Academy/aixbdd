# Phase 0 研究：照片日期相簿整理

## 決策 1：採用前後端分離的極簡 Web 架構

- **Decision**: 採用 `frontend/` 的 `Vite + 原生 HTML/CSS/JS` 與 `backend/` 的 `Node.js + Express` 分離架構。
- **Rationale**: 此架構最符合「教學友善、套件少、可直接對接照片上傳 API」的需求，也能清楚區分 UI、HTTP 與資料持久化責任。
- **Alternatives considered**:
  - 單體 SSR：初版不需要伺服器端模板渲染，會增加頁面耦合。
  - React SPA：超出使用者要求，並增加概念與依賴複雜度。

## 決策 2：前端僅保留 Vite 作為核心工具

- **Decision**: 前端執行期只使用 `vite`，其餘以瀏覽器原生能力實作狀態管理、資料抓取與圖片顯示。
- **Rationale**: 首頁需求集中在清單渲染、拖放排序、上傳與狀態切換，原生 ES modules 足以支撐；避免額外框架可降低 bundle、學習成本與除錯面積。
- **Alternatives considered**:
  - 引入狀態管理函式庫：對單頁小型應用價值不足。
  - 引入 UI 元件庫：會弱化教學示範的原生基礎。

## 決策 3：拖放排序採用瀏覽器原生 Drag and Drop

- **Decision**: 同一日期相簿內的照片重排優先使用原生 `HTML Drag and Drop API`，不導入第三方拖放套件。
- **Rationale**: 需求只包含「同相簿內重排、不可跨相簿搬移」，互動模型單純；原生 API 足以達成，且較容易在課程中說明 DOM 與排序邏輯。
- **Alternatives considered**:
  - `SortableJS`：雖然方便，但對本案屬額外依賴，且掩蓋核心排序規則。
  - 自行以 `Pointer Events` 全客製：彈性高，但初版成本高於需求。

## 決策 4：後端採用 ORM 管理 MySQL 與資料模型

- **Decision**: 後端使用 `express`、`multer`、`@prisma/client`、`exifr`、`sharp` 作為核心執行期套件，並以 `prisma` 管理 schema 與 migration。
- **Rationale**:
  - `express`：最小且成熟的 HTTP API 框架
  - `multer`：簡化 `multipart/form-data` 多檔上傳
  - `Prisma ORM`：以型別安全的 model、migration 與 relation 管理資料結構，對教學與後續維護更友善
  - `exifr`：解析照片拍攝日期
  - `sharp`：產生縮圖，降低首頁載入成本
- **Alternatives considered**:
  - `mysql2` 直接寫 SQL：依賴較少，但 schema 演進、關聯管理與教學可讀性較差
  - `Knex`：較接近 SQL，但在 model 表達與型別整合上不如 Prisma 直接

## 決策 5：原圖與縮圖直接存入 MySQL BLOB

- **Decision**: 原圖與縮圖都存放在 MySQL 的 `BLOB/LONGBLOB` 欄位中，並由後端 API 直接串流預覽內容給前端。
- **Rationale**: 這能把照片內容與中繼資料一起納入同一交易邊界與備份範圍，對教學示範也較直觀，不需額外管理檔案系統路徑與清理問題。
- **Alternatives considered**:
  - 檔案系統路徑 + DB 中繼資料：較省資料庫容量，但會增加路徑同步與刪除一致性問題
  - 雲端物件儲存：擴充性更好，但超出初版教學目標

## 決策 6：日期分組以 EXIF 為主，匯入日期為最後 fallback

- **Decision**: 優先讀取 EXIF `DateTimeOriginal`，次選其他 EXIF/檔案時間；若都不可用，使用匯入當天日期作為 `album_date`。
- **Rationale**: 這完全對齊規格的澄清答案，且可保證每張照片都能被歸入可瀏覽的日期相簿。
- **Alternatives considered**:
  - 將無日期照片集中到「未知日期」相簿：違反已澄清需求
  - 僅依檔案建立時間：容易與真實拍攝日期不符

## 決策 7：照片預覽以後端圖片端點串流縮圖 BLOB

- **Decision**: `GET /api/albums` 與 `GET /api/albums/{id}/photos` 僅回傳預覽所需中繼資料與 `previewUrl`；`previewUrl` 由後端圖片端點從資料庫中的縮圖 `BLOB` 串流回應。
- **Rationale**: 需求要求最多 200 張可見照片仍能在 2 秒內可瀏覽，因此即使圖片存放在資料庫，也必須優先傳輸較小的縮圖內容而非原圖。
- **Alternatives considered**:
  - 前端自行縮放原圖：浪費頻寬且造成渲染壓力
  - 僅顯示檔名不顯示縮圖：不符合平鋪式預覽需求

## 決策 8：排序持久化採用相簿內 `sort_key`

- **Decision**: 在 `photos` 記錄中保存 `sort_key` 與 `sort_mode`，預設按拍攝時間排序；拖放成功後切換為手動排序。
- **Rationale**: 這能在不新增額外排序表的情況下滿足「立即更新且重新進入後仍維持一致」的要求。
- **Alternatives considered**:
  - 每次拖放重寫整個相簿的連續序號：可行，但更新成本較高
  - 另外建立排序表：對 MVP 過度設計

## 決策 9：BDD techstack 分端指定

- **Decision**: 前端 webapp 的 Gherkin 用 `Playwright` 落地；後端 API 的 Gherkin 用 `behave` 落地。
- **Rationale**: 這是 AIxBDD workflow，BDD techstack 一定要先 clarify。前端驗的是畫面操作，後端驗的是 API 與權威狀態，runner 不能混成一個。
- **Alternatives considered**:
  - 前後端都只用 Playwright：後端權威狀態不該只靠畫面推斷。
  - 前後端都只用 behave：behave 不是前端 webapp E2E 的預設。

## 決策 10：測試策略預設都是 E2E

- **Decision**: 前端用 Playwright 打 webapp E2E；後端用 behave 打 API 與資料庫權威狀態。匯入分組、相簿查詢、排序持久化與跨相簿拒絕都走 E2E，不把主驗收收成單元測或手動 Quickstart。
- **Rationale**: 測試策略沒被改判時，預設都是 E2E。拖放與清單是否真的更新，要在畫面上看到；分組與拒絕，要在後端權威狀態看到。
- **Alternatives considered**:
  - 先 `vitest + supertest`、E2E 以後再補：會把驗收旅程測成假綠燈。
  - 完全不做自動化：Gherkin 沒有落地。
