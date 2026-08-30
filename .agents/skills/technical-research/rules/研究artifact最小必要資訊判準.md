# Rule 1 - `research.md` 的每個研究決策都必須完整保留標題、Decision、Rationale、Alternatives considered

- Level: `MUST`
- `research.md` 中的每個決策區塊都必須包含決策標題、`Decision`、`Rationale` 與 `Alternatives considered`。
- 不可只列結論而沒有採納理由，也不可只做優缺點摘記卻沒有明確採納方案。
- `Alternatives considered` 至少應列出 1 個有比較價值的替代方案。

## Good Example

- 這個例子是好的，因為它保留了做決策與 review 所需的最小資訊。

````md
## 決策 1：拖放排序採用瀏覽器原生 Drag and Drop

- **Decision**: 同一日期相簿內使用原生 Drag and Drop API。
- **Rationale**: 需求只涵蓋同相簿內重排，原生 API 足以支撐且教學成本較低。
- **Alternatives considered**:
  - `SortableJS`
  - 自行以 `Pointer Events` 全客製
````

## Bad Example

- 這個例子是壞的，因為它沒有清楚交代採納理由與替代方案。

````md
## 決策 1：拖放排序

- 用原生 API。
````

# Rule 2 - `research.md` 必須聚焦支撐後續規劃或實作的決策，而不是寫成泛用教學文章

- Level: `MUST`
- `research.md` 應聚焦本次 feature 需要拍板的技術決策、方案取捨與限制，不可把 artifact 寫成與當前 feature 脫節的通用技術教學或百科整理。
- 每個決策都應能回扣到 `spec.md` 的需求、範圍、成功條件或後續 handoff 所需的設計判斷，而不是改由 `techstack.md` 承擔細部研究理由。
- 若某段內容無法支撐本次 feature 的下一步規劃或實作，應刪除或縮成附帶說明。

## Good Example

- 這個例子是好的，因為每個決策都直接支撐該 feature 的後續規劃。

````md
研究主題：照片日期相簿整理

決策：
- 前端是否採框架
- 圖片儲存於 MySQL BLOB 或檔案系統
- 排序持久化如何建模
````

## Bad Example

- 這個例子是壞的，因為它離開當前 feature，變成泛泛的技術筆記。

````md
研究主題：JavaScript 歷史演進

內容：
- ECMAScript 各版本演進總整理
- JavaScript 語言起源
````

# Rule 3 - `research.md` 的 `Alternatives considered` 必須是有比較價值的真替代方案

- Level: `SHOULD`
- `Alternatives considered` 應列出當前決策下實際可選、且會導致不同 trade-off 的方案，而不是形式上湊數的近義重述。
- 若某個替代方案之所以未採用有明確原因，應簡短說明其不採用理由。
- 當唯一合理替代方案只有 1 個時，可只列 1 個，但仍應保有比較價值。

## Good Example

- 這個例子是好的，因為它列出的是實際會改變架構取捨的方案。

````md
- **Alternatives considered**:
  - `mysql2` 直接寫 SQL：依賴較少，但 schema 演進與教學可讀性較差
  - `Knex`：較接近 SQL，但型別整合不如 Prisma 直接
````

## Bad Example

- 這個例子是壞的，因為它列出的不是有實質差異的替代方案。

````md
- **Alternatives considered**:
  - 更好的做法
  - 另一個差不多的方法
````

# Rule 4 - `research.md` 中未驗證假設與殘留風險必須明示，不可偽裝成已確認事實

- Level: `SHOULD`
- 若某個決策仍依賴尚未驗證的容量、效能、相容性或營運假設，應在 `research.md` 的 `Rationale` 中明示，或在交付時列為後續 spike / 驗證項。
- 不可把尚未量測的數值、尚未確認的邊界或推測中的限制，直接寫成已拍板事實。
- 這樣可讓後續 `/plan-with-class-diagram` 或實作階段清楚接手剩餘風險。

## Good Example

- 這個例子是好的，因為它保留了尚待驗證的容量風險。

````md
- **Rationale**: 原圖與縮圖存入 MySQL BLOB 能簡化教學與一致性；實際容量與備份時間仍需在實作階段驗證。
````

## Bad Example

- 這個例子是壞的，因為它把未驗證結論寫成絕對事實。

````md
- **Rationale**: MySQL BLOB 一定能在所有部署情境下提供最佳效能與最低成本。
````
