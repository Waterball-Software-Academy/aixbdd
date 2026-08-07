# 事故蒸餾：SKILL-GAPS #40（fitbook B-66）——Given 把 freeze_count 佈成 0，
# Then 卻斷言「維持 1」；rev1／rev2 兩輪人審全漏，直到 green 才炸。
Feature: 會籍現況查詢

  Rule: 後置（回應） - 查詢會籍回傳剩餘凍結次數

    Example: 已凍結過的會籍查詢，累計凍結次數不受查詢影響
      Given "陳美惠" 有一筆 "生效中" 的 "月卡" 會籍，到期日 "2026-02-13"
      When 系統查詢 "陳美惠" 的會籍
      Then "陳美惠" 的會籍累計凍結次數維持 1
