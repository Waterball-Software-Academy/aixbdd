Feature: lint_examples 草稿機械檢核
  作為 spec-by-example 的步驟 8.1／8.2
  我要 在草稿交進 8.4 稽核之前機械抓出「參數逼近上限」與「不可實作的失敗情境」
  以便 稽核者不必逐行手算，也不必等到 red 階段才發現例子做不出來

  # 每個 fixture 都是 fitbook benchmark 事故的最小重現；修復前本 skill 沒有任何腳本，
  # 這些檢核全靠稽核者人眼逐行手算（M2 實測 42 行剛好 4 參數是手算確認的）。

  Rule: #43 單行可綁定參數 >4 阻斷、=4 提醒（cucumber-literal-format 不變式 6 分工）

    Example: Given 資料佈建句 6 個參數，阻斷並建議直接改表
      Given feature fixture "arity-over-limit"
      When 執行 lint_examples
      Then 退出碼為 3
      And lint 回報:
        | severity | code       | 訊息含                          |
        | fail     | step-arity | Given 是資料佈建句              |
        | warn     | step-arity | When／Then 先檢討               |

    Example: 剛好 4 個參數只提醒，不阻斷
      Given feature fixture "arity-exactly-four"
      When 執行 lint_examples
      Then 退出碼為 0
      And lint 回報:
        | severity | code       | 訊息含   |
        | warn     | step-arity | 表格已滿 |

  Rule: #36 對「以具體實例定位的標的」寫「沒指定」即提醒 path 參數不可觀測

    Example: 「標記付款完成但沒指定會籍」被標出
      Given feature fixture "unspecified-path-param"
      When 執行 lint_examples
      Then 退出碼為 0
      And lint 回報:
        | severity | code               | 訊息含       |
        | warn     | unspecified-target | 路由不匹配   |

  Rule: #14 Example 上方的所有註解（不只 `# 取捨：`）之前必為空行

    Example: 測試設計註記緊貼 Rule 標題下方，缺空行
      Given feature fixture "comment-blank-line"
      When 執行 lint_examples
      Then 退出碼為 0
      And lint 回報:
        | severity | code                       | 訊息含   |
        | warn     | example-comment-blank-line | 缺一行空行 |

  Rule: 合規的草稿不得被誤報

    Example: 對照組——三條檢核全數通過
      Given feature fixture "clean"
      When 執行 lint_examples
      Then 退出碼為 0
      And lint 沒有任何回報
