# 驗收期第二輪發現：export key 的 `{{alias}}` 屬於 instruction 自己的 format 具名群組，
# 與 dsl_step 怎麼命名自己的 param 無關。dsl_step 用中文佔位名 `{業務}` 時，
# 舊解析（用 dsl_step 的 vmap 內插）會靜默丟失 export，undefined-var 照樣誤報。
Feature: 授信申請

  Rule: 後置（狀態） - 業務提交申請後落庫

    Example: 以中文佔位名宣告的身分前置，仍導出得到 id
      Given 已登入的業務 "業務阿宏"
      When "業務阿宏" 提交新客授信申請
      Then 系統回應 "提交成功"
