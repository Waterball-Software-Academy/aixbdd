# 事故蒸餾：SKILL-GAPS #23（fitbook B-40）——param 宣告成有預設（空字串），
# 展開一律套預設、不會被 feature DataTable 的同名欄覆寫，PM 給的值被靜默蓋掉。
Feature: 會籍佈建

  Rule: 後置（狀態） - 會籍到期日依方案推算

    Example: 以資料表佈建生效中月卡會籍
      Given "陳美惠" 有一筆會籍：
        | 狀態 | 方案 | 到期日 |
        | 生效中 | 月卡 | 2026-02-13 |
      When 系統查詢 "陳美惠" 的會籍
      Then 系統回應 "查詢成功"
