# 驗收期發現的誤報最小重現：`$業務阿宏.id` 的來源是 isa.yml 指令契約宣告的
# export_vars（不是 DataTable 表頭的 `>alias` 捕獲），舊版 lint 認不得而阻斷級誤報。
Feature: 授信申請

  Rule: 後置（狀態） - 業務提交申請後落庫

    Example: 業務提交新客授信申請，提交成功
      Given 已登入的業務 "業務阿宏"
      When "業務阿宏" 提交新客授信申請
      Then 系統回應 "提交成功"

    Example: 引用完全沒有來源的變數，應該仍被攔下
      When "業務阿宏" 為 "查無此人" 提交新客授信申請
      Then 系統回應 "查無此人"
