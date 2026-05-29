# Variant: <variant-id>

1. 一個 variant 描述「同一個 boundary preset 的 handler，渲染到某個具體技術棧」時的機制。
2. 一個 boundary 可以有多個 variant（例：後端的 python-e2e / java-e2e；前端的 nextjs-playwright），各自一份 .md。實際採用哪個 variant 由 plan 的 `L4.preset.variant` 選定。
3. 邊界：variant 只定義 rendering 機制（語言、框架、context 物件、step 檔佈局），不分類 sentence part、不挑 handler（那是 `part_to_dsl.py` 與 DSL entry `handler` 的事）。

## Role

1. 一句話：`<variant-id>` 把 <boundary-id> preset 的 handler 渲染成 <語言/框架> 的 step definitions。

## Runtime Contract

1. 列出此 variant 的技術棧約束，逐項說明：
   1. Language：<語言版本>
   2. BDD framework：<框架>
   3. 其他 runtime 依賴（HTTP client / persistence access / app access / context 物件 / 時間控制 / 外部資源）。

## Required Context Fields

1. 列出每個 test case 開始前必須初始化的 context 欄位（以 code block 給具體初始化片段）。

```text
<context.field = ...>
```

## Step File Layout

1. 說明 step 檔的目錄結構：每個 handler 對應一個子目錄（handler 名的連字號轉成該語言慣用的命名）。
2. 用 code block 畫出目錄樹。

## <框架> Matcher Contract

1. 列出此框架的 step matcher 規則（用哪些 decorator、第一參數慣例、placeholder 型別對應）。

## Forbidden

1. 逐條列出此 variant 禁止的渲染行為，每條附 why（例：不得在 contract 外臆測 endpoint path、不得在 Then handler 發第二次呼叫）。

## Legal Red Expectation

1. 定義「什麼樣的 step definition 才算合法 red」：matcher 來自精確 L1、值來自 L4 bindings、preset tuple 解析到本 variant、且能跑到足以暴露缺漏的產品實作。
2. 強調反例：缺 truth 不是合法 red，必須在 render 前停下。
