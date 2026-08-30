# 範例索引

這個 skill 的完整示範不再集中塞在單一檔案，而是改成一個可直接閱讀的電商 spec package。

## 完整電商 package

路徑：`examples/ecommerce/features/`

結構如下：

```text
examples/ecommerce/
└── features/
    ├── backend/
    │   ├── dsl.md
    │   ├── 折扣碼套用與拒絕.feature
    │   └── 訂單重算與免運判定.feature
    └── frontend/
        ├── dsl.md
        ├── 結帳頁折扣碼輸入.feature
        └── 訂單摘要與免運顯示.feature
```

## 如何閱讀

1. 先讀 `features/backend/` 與 `features/frontend/`，看 feature 如何按功能切分。
2. 再讀各自的 `dsl.md`，確認 Gherkin 句型如何落到測試程式碼。
3. 若要看完整的句型與規則摘要，再回到 `SKILL.md` 與 `STANDARDS.md`。
