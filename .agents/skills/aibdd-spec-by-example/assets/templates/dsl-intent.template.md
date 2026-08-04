# DSL Step 推理意圖 — <feature 檔名>

本檔由 /aibdd-spec-by-example 產出、/aibdd-dsl-refine 消費：記錄每個 Example 的測試意圖與逐句觀察意圖，讓下游展開 isa steps 時不必回頭腦補推理。只寫 WHAT（要觀察什麼、為什麼），不寫 HOW（如何實作）。每輪 plan 迭代新增或變更 Example 時同步更新本檔。

## Example: <Example 標題>

- 所屬 Rule: <Rule 標題（含類型前綴）>
- 測試意圖: <這個例子要證明該 rule 的哪一面；類型：happy／negative／邊界／冪等／隔離>
- 關鍵參數: <參數名>=<值>（選值理由：<等價類有效值／邊界 max+1／清單外值／髒水…>）
- 逐句意圖:
  - Given <句子>: <建立什麼狀態、本例為什麼需要它；資料／身分／時間屬哪類前置>
  - When <句子>: <觸發什麼業務操作、關鍵輸入是什麼>
  - Then <句子>: <觀察什麼結果；驗回應層還是資料層（落庫值／不存在）；為什麼這樣驗才算證明>
