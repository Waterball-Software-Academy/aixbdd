# 骨架 vs 業務語意 取捨守則

- pattern 模板必為「最大集合」骨架；實際 Example 得為其子集，不必每個 placeholder 都填。
- 省略骨架元素僅當該元素在此 case 重複或無業務區別力；禁止為了少寫而省略仍有意義之元素。
- 省略時必須在 Example 上方加註解 `# 取捨：<原因>`；不得省略卻不留註解。
- 取捨決策僅當在 phase 2 step 6 執行；其他 step 不得自作主張省略元素。

## 觸發省略的三種情境

- 兩個骨架元素指向同一觸發動作（例：Command 與 Query 在此 case 為同一動作）: 省略 Given 中重複的那個
- 骨架元素在此 case 無業務區別力（例：Actor 在所有 Example 都一樣）: 可省，但建議只在 Background 集中表達
- 骨架元素於此 case 必為「無」（例：前置失敗的 Event）: 省略，模板本就不應出現

## Good

- Feature `結帳套用優惠券`、PATTERN_A：Given 骨架要求列 `<Command>`（執行結帳），但 When 也是「執行結帳」 → 省略 Given 的 Command，加註解 `# 取捨：Command 與觸發動作為同一事件（執行結帳），故 Given 不重複列`。
- PATTERN_B：Event 在前置失敗為「無」，骨架本就不列；不需要寫註解。

## Bad

- 為了 Example 簡潔，省略 PATTERN_A 的 Input：失敗原因消失，讀者看不出為何失敗；禁止省略 Input。
- 省略 Command／Query 卻不加註解：未來讀者無法判斷是漏寫還是有意取捨；必須註解原因。
- PATTERN_C 省略 Event：後置成功的事件必為驗證核心，省略即破壞 pattern 語意；禁止省略。
- 在 phase 2 step 4（5 元素推導）就決定省略：取捨僅當在 step 6 執行，否則 5 元素檢核會少資料。
