Feature: Activity DSL benchmark fixtures decode 守門
  作為 Activity DSL 維護者
  我要 用 corpus-level fixtures 跑 decoder
  以便 在新增規則時抓回歸（任一 valid fixture 變紅 / err-* fixture 變綠都應立即知道）

  # 來源：packages/core/src/services/graph-drivers/codecs/__tests__/fixtures/activity-benchmark-fixtures
  # 同步：手動複製至 scripts/tests/benchmark-fixtures/（保持 skill 自含）
  #
  # 規約：
  # - 非 `err-*` 開頭的 fixture → decoder 必須 ok=true
  # - `err-*` 開頭的 fixture     → decoder 必須 ok=false
  #   （不檢驗具體 message，由 activity-decode.feature 負責 message 規格）

  Rule: 28 個非 err-* 的 benchmark fixture 必須 decode 成功

    Scenario Outline: <fixture> 應 decode 成功
      Given fixture 檔案 "<fixture>"
      When 執行 decode
      Then decode 成功

      Examples:
        | fixture |
        | 01-單一STEP.activity |
        | 02-二者順序.activity |
        | 03-多角色線性.activity |
        | 04-僅描述無綁定.activity |
        | 05-僅綁定無描述.activity |
        | 06-Actor綁定路徑.activity |
        | 07-引號Actor含空白.activity |
        | 08-Decision帶HTML註解.activity |
        | 09-Decision雙分支.activity |
        | 10-Decision含else.activity |
        | 11-Fork雙並行.activity |
        | 12-簡單迴圈.activity |
        | 13-Decision串接Fork.activity |
        | 14-多終點.activity |
        | 15-Decision巢狀於Branch.activity |
        | 16-Decision巢狀於Parallel.activity |
        | 17-三層Decision巢狀.activity |
        | 18-Fork巢狀於Branch.activity |
        | 19-跨分支迴圈.activity |
        | 20-業務全期複雜網.activity |
        | benchmark-A-user-login.activity |
        | benchmark-B-order-checkout.activity |
        | benchmark-C-refund-inventory.activity |
        | 範例-最小情境.activity |
        | 範例-複雜情境.activity |
        | 行銷.activity |
        | 訂單處理流程.activity |
        | 課程學習流程.activity |

  Rule: 5 個 err-* 的 benchmark fixture 必須 decode 失敗

    Scenario Outline: <fixture> 應 decode 失敗
      Given fixture 檔案 "<fixture>"
      When 執行 decode
      Then decode 失敗

      Examples:
        | fixture |
        | err-01-缺ACTIVITY標頭.activity |
        | err-02-未宣告Actor引用.activity |
        | err-03-重複STEP編號.activity |
        | err-04-孤兒MERGE.activity |
        | err-05-STEP缺Actor.activity |
