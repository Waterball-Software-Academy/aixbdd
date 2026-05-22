# Discovery Sourcing Report — 001-1A2B猜數字魔王遊戲

## Impact scope

- 本輪問題一句：新建一套多人 1A2B 猜數字魔王遊戲的完整規格，涵蓋遊戲大廳（開房/加入/準備）與魔王戰鬥（密碼設置、輪流攻防、傷害計算、勝負判定）
- 納入範圍：遊戲大廳流程（開房、加入、準備、開始）；魔王戰鬥流程（階段一密碼設置、階段二玩家輪流攻擊、魔王輪流行動、死亡/勝負判定）；傷害公式參數設計；魔王四個行動規則
- 明確排除：玩家帳號系統（無登入需求）；排行榜、積分持久化；多場次歷史紀錄；聊天室功能

## Impact matrix

| 既有規格檔（相對 `specs`） | 變更類型 | impact 描述 |
|---|---|---|
| `packages/01-遊戲大廳/features/01-開房或加入遊戲房.feature` | 新增 | 全新；涵蓋輸入四位房號、開新房（房不存在）與加入現有房（房已存在）兩分支 Scenario |
| `packages/01-遊戲大廳/features/02-玩家準備.feature` | 新增 | 全新；涵蓋房客按準備、準備狀態變更 |
| `packages/01-遊戲大廳/features/03-房主開始遊戲.feature` | 新增 | 全新；涵蓋房主觸發開始（≥2人且全準備）；產生魔王、進入階段一為 postcondition |
| `packages/02-魔王戰鬥/features/01-玩家設置密碼.feature` | 新增 | 全新；涵蓋玩家平行設置四位不重複密碼、魔王隨機密碼；全員完成後進入階段二為 postcondition |
| `packages/02-魔王戰鬥/features/02-玩家猜測魔王數字.feature` | 新增 | 全新；涵蓋猜測輸入、1A2B 計算、傷害加權公式與爆擊；魔王回合（四種行動）、出局、勝負判定為同 feature 的 Scenario |

## Function package charters

### `packages/01-遊戲大廳`

- **職責一句**：管理遊戲房間的生命週期——開房、加入、玩家準備到開始遊戲
- **納入**：房間號碼唯一性、開房/加入分流、房主/房客角色、準備狀態、人數上下限、開始遊戲觸發
- **排除**：遊戲中對戰邏輯、密碼設置、傷害計算
- **本輪變更型態**：`new-package`
- **本輪規格增量**：建立 `01-開房或加入遊戲房.feature`、`02-玩家準備.feature`、`03-房主開始遊戲.feature`

### `packages/02-魔王戰鬥`

- **職責一句**：管理一場戰鬥的完整生命週期——密碼設置、輪流攻防、傷害治療計算、出局與勝負
- **納入**：階段一密碼設置（玩家平行、魔王隨機）、玩家回合猜測與傷害計算、魔王回合四種行動、玩家出局規則、勝利/失敗判定
- **排除**：房間管理、玩家加入/準備、玩家帳號
- **本輪變更型態**：`new-package`
- **本輪規格增量**：建立 `01-玩家設置密碼.feature`、`02-玩家猜測魔王數字.feature`

## Packaging decision

- 新 plan package：`001-1A2B猜數字魔王遊戲`
- 本輪涉及的 function packages：
  - `packages/01-遊戲大廳`（新開）
  - `packages/02-魔王戰鬥`（新開）
- function package 決策：本輪同時新開 plan package 與兩個 function package；大廳與戰鬥主線彼此無跨包強依賴，狀態所有權清晰可獨立迭代。

## Resolved sourcing decisions（已拍板）

- 是否有既有 contracts／data truth：**否**；specs/ 下 contracts/、data/ 均為空（僅 .gitkeep），本輪全為新建規格
- 傷害加權公式具體係數是否已給定：**否**；需求敘述僅說「依 A、B 加權」，具體公式留待 plan phase 細化或 clarify 補洞
- 魔王對玩家猜測時是否使用玩家密碼（而非玩家猜過的數字）：**是**；需求描述魔王「猜測玩家數字」即對玩家的密碼做 1A2B，並以此計算傷害

## Notes

- `Impact matrix`：逐檔展開，未採 glob 閉包。
- `傷害公式`：需求原文未給出數學式，impact matrix 中相關 feature 後續撰寫時若仍無公式，需於 plan phase 補一次 clarify 詢問。
- 玩家血量上限：需求未明述玩家的血量設定，僅說魔王血量 = 玩家數 × 1000；玩家血量未指定，後續 clarify 補洞。
