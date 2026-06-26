# feature 重構（clarify-loop 確認驅動）

refine 過程中，若 example 的步驟結構不利乾淨對應 isa，可重構該 `.feature`。
重構是寫入 `.feature` 的唯一許可，但有兩條硬規則：

1. 先經 `/clarify-loop` 向使用者確認，取得同意才改——不得逕自改 feature。
2. 只動步驟結構，不改該 example 的驗收意圖（驗什麼、negative 條件、預期結果一律不變）。

重構後依新句子建立 dsl_step（回到 SOP step 7.3）。

## 何時觸發

- 一個 isa 操作被拆成多句業務步驟，其中某句不是獨立可對應的 instruction。
  典型：`Given "Alice" 準備一筆資料齊全的訂單` ＋ `When "Alice" 送出訂單，但沒填收件地址`——
  Given 句不是真正的 entity_setup，兩句合起來才是「一次 api_call：送出一筆除收件地址外都填好的訂單」。
- 一句業務步驟其實混了多個 isa 操作，無法用單一 dsl_step 乾淨表達。
- 步驟資料不自足，無法判斷該帶什麼 payload。

## 重構方向（經 `/clarify-loop` 與使用者確認後選擇，不固定）

- 合併：把「準備」句併進「操作」句，成單一自足步驟（api_call 帶完整 payload、缺指定欄位）。
- 改寫成資料自足：把「準備」句改成明確的 entity_setup／payload，操作句以 `$alias` 引用。
- 拆分：把一句混多操作的步驟拆成數句，各對一個 isa 操作。

## Good

```gherkin
# 原（一個 api_call 被拆成兩句，Given 句空泛無法單獨對 isa）
Given "Alice" 準備一筆資料齊全的訂單
When  "Alice" 送出訂單，但沒填收件地址
Then  送出沒有成功

# 經 /clarify-loop 確認「保留 negative 意圖、只合併結構」後 → 合併為單一自足步驟
When "Alice" 送出一筆收件地址留空、其餘必填欄位皆已填的訂單
Then 送出沒有成功
# → 對應單一 api_call（body 缺 收件地址）＋ response_validate（失敗）
```

## Bad

```gherkin
# 未經 /clarify-loop 確認就逕自改寫／刪句
# 重構時順手把 negative 改成 positive，改變了驗收意圖
When "Alice" 送出訂單   # 漏了「沒填收件地址」→ 變成驗成功，意圖被改掉

# 把空泛的「準備一筆資料齊全的訂單」硬當 entity_setup 塞一筆假資料，
# 與 When 的送出語意脫節（應該合併或改寫，而非硬塞）
```
