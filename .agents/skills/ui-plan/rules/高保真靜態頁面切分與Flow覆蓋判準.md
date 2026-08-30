# Rule 1 - 多頁雛形固定以 `ui/index.html` 作為入口

- Level: `MUST`
- 若 feature 的真實產品流程需要跨頁，`ui-plan` 必須固定使用 `ui/index.html` 作為雛形入口頁。
- 入口頁本身也必須是產品的一部分，而不是 sitemap、說明頁或純連結目錄。
- 若 feature 不需要跨頁，仍至少要有一個可操作的 HTML 頁面。

## Good Example

- 這個例子是好的，因為 `index.html` 本身就是產品入口，而不是額外的導覽文件。

```md
ui/index.html           -> 商品列表入口畫面
ui/product-detail.html  -> 商品詳情畫面
ui/checkout.html        -> 購物車與結帳畫面
```

## Bad Example

- 這個例子是壞的，因為 `index.html` 只是檔案清單，沒有真正承擔產品流程入口。

```md
ui/index.html
- Link: product-detail.html
- Link: checkout.html
- Link: order-success.html
```

# Rule 2 - 雛形必須覆蓋從入口到主要結果的完整使用者流程

- Level: `MUST`
- `ui-plan` 產出的 HTML 雛形至少要覆蓋本次 feature 的主流程入口、關鍵中間狀態與主要結果頁。
- 不可只做單一好看的頁面，卻缺少流程中的等待、錯誤、結果或回合狀態。
- 若畫面數量需要裁切，應優先保留完整流程，而不是只保留視覺最吸睛的片段。

## Good Example

- 這個例子是好的，因為它讓 reviewer 能從瀏覽商品一路走到完成下單。

```md
流程覆蓋：
1. 瀏覽或搜尋商品
2. 查看商品詳情與規格
3. 確認購物車與結帳資訊
4. 查看訂單成功結果
```

## Bad Example

- 這個例子是壞的，因為它只呈現中間一頁，無法 review 真正產品流程。

```md
流程覆蓋：
1. 只做一個訂單成功頁
2. 沒有入口
3. 沒有瀏覽、加入購物車或結帳流程
```

# Rule 3 - 靜態雛形仍必須可操作，並以假資料模擬真實互動

- Level: `SHOULD`
- 雖然雛形不連真實後端，仍應提供可點擊按鈕、可切頁導覽、表單輸入與以假資料呈現的狀態切換，讓使用者能感受真實產品節奏。
- 可用前端假資料、前端條件切換或簡單 JavaScript 模擬購物車狀態、錯誤提示與送單變化。
- 不應只交付靜態截圖式頁面，讓 reviewer 無法操作或感受互動。

## Good Example

- 這個例子是好的，因為它雖然沒有後端，仍能模擬基本互動。

```html
<input placeholder="搜尋商品或品類" />
<button onclick="location.href='product-detail.html'">查看商品</button>
<p id="error">請先輸入搜尋關鍵字</p>
```

## Bad Example

- 這個例子是壞的，因為它只有靜態畫面，沒有任何可操作性。

```html
<img src="checkout-screen.png" alt="結帳畫面截圖" />
<p>這就是之後大概會長這樣。</p>
```
