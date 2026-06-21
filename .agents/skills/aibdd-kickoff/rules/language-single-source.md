# 語系單一來源

## Rule 1 — 只改 `PROJECT_SPEC_LANGUAGE` 一處；`_LANGUAGE_REF` 靠 YAML ref 自動跟隨，禁止手改

- `arguments.yml` 裡語系的 SSOT 是 `PROJECT_SPEC_LANGUAGE` 一個欄位；其餘兩個用到語系的位置寫成 YAML internal ref，自動取回該值。切換語系時只改 `PROJECT_SPEC_LANGUAGE` 這一行就夠，兩個 ref 自然跟著變。不要手動編輯那兩個 `_LANGUAGE_REF`：手改會把 reference 改成寫死字面值（之後改 source 不再連動），且三處可能改不同步而漂移。單一來源的價值就在「只有一處可信」，多寫一處就是多一個出錯點。預設 `PROJECT_SPEC_LANGUAGE: zh-hant`，只有當決策語系不是 `zh-hant` 才需改這一行。

### ✅ Good

情境：決策 project_spec_language = ja-jp

```
僅 Edit：PROJECT_SPEC_LANGUAGE: zh-hant → PROJECT_SPEC_LANGUAGE: ja-jp
兩個 _LANGUAGE_REF（YAML ref）自動解析為 ja-jp，不動。
```

### ❌ Bad

```
Edit PROJECT_SPEC_LANGUAGE → ja-jp
Edit _LANGUAGE_REF #1       → ja-jp   （把 ref 改成字面值，連動斷掉）
Edit _LANGUAGE_REF #2       → 漏改，仍 zh-hant   （三處漂移）
```

**預期改法**
- 只 Edit `PROJECT_SPEC_LANGUAGE` 一行；`_LANGUAGE_REF` 兩處原封不動，交給 YAML ref 跟隨。
