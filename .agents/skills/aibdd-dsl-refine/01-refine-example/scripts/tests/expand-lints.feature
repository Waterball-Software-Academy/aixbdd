Feature: expand_isa 展開 lint
  作為 dsl-refine 的 sub-SOP 步驟 d
  我要 在把展開交進 batch review 之前機械攔下五類「機械全綠、語意翻車」的推導
  以便 這些事故不必等到 red／green 階段才炸

  # 每個 fixture 都是 fitbook benchmark 事故的最小重現。同一組 fixture 在修復前的
  # expand_isa（HEAD）上一律 exit 0、stderr 全空——舊版靜默通過，新版正確攔截。

  Rule: #24 同一個 example 對同一 entity 佈建兩次即阻斷（duplicate-entity-setup）

    Example: B-71 兩個前置句各自展開出同一筆會員
      Given fixture "duplicate-entity-setup"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code                    | 訊息含   |
        | fail     | duplicate-entity-setup  | 被佈建兩次 |

  Rule: #40 Given 佈建值／When 送出值／Then 斷言值三方必須自洽（seed-assertion-consistency）

    Example: B-66 不變斷言的值與 Given 佈建值矛盾
      Given fixture "seed-assertion-invariant"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code                       | 訊息含   |
        | fail     | seed-assertion-consistency | 不變斷言 |

    Example: 變更斷言的值與 Given 佈建值相同（恆真）
      Given fixture "seed-assertion-tautology"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code                       | 訊息含 |
        | fail     | seed-assertion-consistency | 恆真   |
      And lint 只回報 1 筆

    Example: Example 標題的數值語意與展開後的 seed 值不一致
      Given fixture "seed-assertion-title-number"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code                       | 訊息含 |
        | fail     | seed-assertion-consistency | 標題寫 |

  Rule: #35 isa_step 引用本 example 未捕獲的 VAR 即阻斷（undefined-var）

    Example: 「標的不存在」情境沒有 seed，卻仍送 $alias.id
      Given fixture "undefined-var"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code          | 訊息含                   |
        | fail     | undefined-var | SYMBOL_VAR_KEY_NOT_FOUND |

  Rule: #23 param 有預設又被 feature DataTable 供值只提醒、不阻斷（default-vs-datatable）

    Example: B-40 到期日宣告成空字串預設，DataTable 的值被靜默蓋掉
      Given fixture "default-vs-datatable"
      When 執行 expand_isa
      Then 退出碼為 0
      And lint 回報:
        | severity | code                 | 訊息含       |
        | warn     | default-vs-datatable | 靜默蓋掉 |

  Rule: #52 param 預設值命中 PM 字面樣式即阻斷（param-default-pm-literal）

    Example: M2 預設寫成空白分隔無時區的時間與含（台北時間）的字面
      Given fixture "param-default-pm-literal"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code                     | 訊息含       |
        | fail     | param-default-pm-literal | 非 ISO-8601  |
        | fail     | param-default-pm-literal | 中文括號註記 |

  Rule: 正確的推導不得被誤報

    Example: 對照組——五條 lint 全數通過
      Given fixture "clean"
      When 執行 expand_isa
      Then 退出碼為 0
      And lint 沒有任何回報

  Rule: 推導中的定義住 `.dsl.yml.draft`，展開時自動一併載入（#46）

    Example: 本尊尚無定義、草稿已有定義，展開仍算得出來
      Given fixture "draft-load"
      When 執行 expand_isa
      Then 退出碼為 0
      And lint 沒有任何回報
      And 展開結果含 "準備一個會籍, with table:"

  Rule: #35 的 VAR 來源包含 isa.yml 指令契約宣告的 export_vars（驗收期發現的誤報）

    Example: 引用來源是 custom 契約的 export_vars，不得誤報
      Given fixture "export-vars-source"
      And 只展開 Example "業務提交新客授信申請，提交成功"
      When 執行 expand_isa
      Then 退出碼為 0
      And lint 沒有任何回報

    Example: 真的沒有任何來源的 VAR 仍然被攔下
      Given fixture "export-vars-source"
      And 只展開 Example "引用完全沒有來源的變數，應該仍被攔下"
      When 執行 expand_isa
      Then 退出碼為 3
      And lint 回報:
        | severity | code          | 訊息含      |
        | fail     | undefined-var | $查無此人.id |
