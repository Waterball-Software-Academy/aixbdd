# Research — 001-1A2B猜數字魔王遊戲

## 澄清略過時的預設（ASM）

使用者略過 plan 澄清問卷，下列數值以可測試預設寫入 contract 敘述與 `domain.dbml`，非需求原文鎖定：

1. **傷害公式**：`damage = A×100 + B×50`；爆擊機率 15%、倍率 2。
2. **玩家血量**：`max_hp = hp = 1000`。

若與產品預期不符，應透過 `/aibdd-reconcile` 或 Discovery 修正後重跑 plan。

## 無阻塞項

- 房間人數上限 10、密碼四位不重複、魔王四種行動機率 — 需求已明示，已反映於 API／DBML。

## blocked_reasons

（空）
