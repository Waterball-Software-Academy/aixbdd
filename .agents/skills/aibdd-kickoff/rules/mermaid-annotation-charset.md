# Mermaid annotation 字元集

## Rule 1 — `.mmd` 的 `<<...>>` annotation 只能用 `[A-Za-z0-9_]`，hyphen 換 underscore；boundary.yml 保留 hyphen

- 同一個 boundary type（如 `web-service`）落在兩個檔，兩端合法字元集不同。`component-diagram.class.mmd`：type 寫進 Mermaid class 的 `<<...>>` annotation，Mermaid 文法只接受 `[A-Za-z0-9_]+`，出現 hyphen 會解析失敗、整張圖渲染不出來——填這個檔要把 type 的 `-` 全換成 `_`。`boundary.yml`：type 是純 YAML 字串值，hyphen 合法且是 type 的 SSOT 寫法，這端保留 hyphen、不可改成 underscore，否則 boundary truth 走樣。同一個 type 兩端各用各的拼法，不是矛盾，是各自遷就所在檔的合法字元集。

### ✅ Good

情境：type = `web-service`

```
boundary.yml                 type: web-service          ← 保留 hyphen（SSOT）
component-diagram.class.mmd   class X { <<web_service>> } ← 換 underscore（Mermaid 合法）
```

### ❌ Bad

```
component-diagram.class.mmd   <<web-service>>   （Mermaid parse error：annotation 不接受 '-'）
或 boundary.yml               type: web_service  （boundary type SSOT 走樣，跨檔對不上）
```

**預期改法**
- 依目標檔分流：寫 `.mmd` 前對 type 做 `replace('-', '_')`；寫 `boundary.yml` 用原始 hyphen 值。
