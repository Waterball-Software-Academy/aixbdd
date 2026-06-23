# Function Package 顆粒度

### 用需求敘事做「一條對外主線」檢查

對每個候選 package 問三個斬釘截鐵的問題（全過才保留成獨立一個 package；任一失敗就合併到主線最強的那個 package，或拆開成兩條主線）：

1. 單一對外入口：是否存在一個使用者或第三方可理解的主要入口（例如「完成登入」「送出訂單」），讓這個 package 內的 `.feature` 主軸不需要跨 package 才能完成一條完整 uat slice？
2. 狀態所有權：這個 package 是否擁有可講完的一段狀態生命週期（建立、進行、終止或失敗）而不強迫讀者跳到另一個 package 才懂「誰是權威狀態」？
3. 變更爆炸半徑：若本批次只改這一個 package，其餘候選 package 是否仍能以「純讀取或純呼叫契約」理解而不必同步改規格？若否，合併或重新切主線，直到「改 A 不必連坐改 B」成立。

## 反例

- 用技術層名詞當 package 名主軸（`redis-cache`、`utils`）：bottom-up 的單位是一段對外行為，不是基礎設施分層。
- 用單一 `.feature` 檔當拆 package 理由：檔是載體；package 是責任邊界。多個 feature 仍可屬於同一個 package，只要共用同一條對外主線與狀態所有權。
- 為了對齊人類組織圖開 package：組織圖是 top-down；這裡只看 impact 表面積與敘事主線。
