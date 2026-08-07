# 事故蒸餾：SKILL-GAPS #48——M1 已 green-evaluate PASS，但 red-execute 對 .dsl.yml 做機械修補時
# 新增／拆分出來的定義沒補標 `# done`，worklist 於是把整個已收官模組永久 report 成 pending。
Feature: 會籍凍結

  Rule: 後置（狀態） - 凍結生效中的會籍後狀態轉為已凍結

    Example: 店員凍結生效中的會籍，凍結成功
      Given "陳美惠" 有一筆 "生效中" 的 "月卡" 會籍
      When "林小柔" 凍結 "陳美惠" 的會籍
      Then "陳美惠" 的會籍變成 "已凍結"
