# 事故蒸餾：SKILL-GAPS #35（fitbook 03／04／05 各一例）——成功情境與「標的不存在」情境
# 是同一句、對到同一個 dsl_step，不存在情境沒有 seed 該筆資料，
# 展開後執行期 SYMBOL_VAR_KEY_NOT_FOUND。
Feature: 會籍付款

  Rule: 前置（狀態） - 標記付款完成的會籍必須存在

    Example: 標記不存在的會籍付款完成，操作沒成功
      Given 已登入的店員 "林小柔"
      When "林小柔" 標記 "陳美惠" 的會籍付款完成
      Then 系統回應 "查無會籍"
