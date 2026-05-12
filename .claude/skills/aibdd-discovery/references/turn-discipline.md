# Turn Discipline + 狀態外顯規則

> 純 declarative reference。SKILL.md 全 phase 適用，描述本 skill 對 user turn 的紀律。
>
> **流程控制 SSOT**：所有 phase order、互動點、等待點、失敗回跳與寫檔守門，只以 `SKILL.md` §2 SOP 為準。本檔不得宣告任何 phase routing 或互動點枚舉，避免與 SOP 漂移。

## §1 Scope

本檔只描述跨 phase 的非流程型 user-turn discipline：

- formulation skill report 的對外可見性
- CiC / internal metadata 的 user-facing 隱藏規則
- compaction 後恢復時的狀態讀取
- final / progress 回覆不得外顯內部 step 狀態

## §2 DELEGATE 訊號

Formulation skill 的 REPORT 為 Planner 內部訊號，由 Planner 消化後接續推進，不作為 user-facing turn 結尾。

## §3 Compaction 後恢復

讀 TodoWrite，找第一個 `in_progress` 或 `pending` 續跑。

## §4 CiC / internal metadata 隱藏規則

使用者可見文案不得暴露 CiC kind、檔案路徑、`Rule`、`STEP`、`AtomicRule`、reasoning phase id、payload schema、artifact 名稱等內部追蹤詞。

若 SOP 委派 `/clarify-loop`，問題文案必須是自然產品語言；trace-only metadata 只能留在 payload 欄位，不得拼進 `context`、`question`、`options[].label`、`options[].impact` 或 `recommendation_rationale`。

## §5 狀態不外顯

當前 step / 待解便條紙數量維護於 thinking + TodoWrite；回應末尾**不輸出** `> Discovery（Step N/5 …）` 之類狀態行。

狀態外顯會暴露 step 編號 / reasoning phase 名稱，違反 user-facing language discipline。
