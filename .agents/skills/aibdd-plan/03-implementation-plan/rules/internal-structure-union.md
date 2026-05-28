# internal-structure 的「類別圖」要如何用「循序圖」推理出來？

## 定義

**結構聯集**＝對 `$IMPLEMENTATION_MODEL.paths` 內**每一條** path 所出現的協作者、邊界入口操作、以及會碰到的持久化／回合狀態等「結構載體」，做**集合論式的聯集**後，在**同一張** class／module 圖上呈現：

- **去重**：同名、同責任的類別／模組只畫**一次**。
- **保留差異**：若僅在某條 path 出現的型別或關係，仍須出現在聯集圖中（並可依註記標示「僅 err path」等來源，避免誤讀成全域必備）。
- **不收進內容**：step definition 原文、測試佇列、某一條 path 的完整流程敘事；那些屬於 sequence，不是本圖職責。

換句話說：不是「挑一條 happy path 當全圖」，而是「所有 paths 會用到的結構在**一張圖**裡**並起來**」，讓下游做 GREEN 時找得到完整模組邊界。

## 例子（示意）

假設兩條獨立 path（僅說明聯集概念，非專案定稿）：

- Path `join-room.happy`：使用者經由 HTTP boundary → `RoomSessionController` → `JoinOrCreateRoomUseCase` → `RoomRepository`（讀寫 `rooms`、`room_players`）。
- Path `submit-guess.err`：同一 boundary 的另一操作 → `GameController` → `SubmitGuessUseCase` → `RoomRepository` + `CombatRules`（讀寫同一聚合相關表，但多一個純領域服務）。

**結構聯集**後的 class 圖至少應**同時**包含：

- 兩條 path 各自出現的 **HTTP 入口類**（若實作上合成一個 controller，圖上仍應對應到實際會存在的類／模組，不可漏掉某一條 path 的 entry）。
- `JoinOrCreateRoomUseCase`、`SubmitGuessUseCase`（各自職責不同，不可因只畫 happy 而省略 guess）。
- 共用的 `RoomRepository` 只畫**一個**（去重）。
- `CombatRules` 僅在 guess path 出現，仍必須出現在聯集圖中。

若聯集後發現某個型別無法對應到任一 activity、rule 或契約操作，應回到 SOP 步驟 6 的 blocked 流程，而不是在圖上硬留「不知道誰呼叫」的孤兩節點。
