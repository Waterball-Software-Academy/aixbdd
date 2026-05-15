# Pattern — Component Candidate Detection

> 純 declarative reference。Phase 5 LOAD 取 6 條 heuristics + always-inline list + 輸出表格契約。

## §1 Heuristics（依序套用，higher-precedence 先命中即 stop 該節點）

### H1 — `reusable: true` 強制 component

任何 `.pen` Entity 帶 `reusable: true` 屬性 → 強制抽成 component。`.pen` 規格的 `Ref` 機制只能指向
`reusable: true` 的節點，這是設計者的「**explicit component intent**」訊號，最強。

### H2 — Numeric-suffix 重複

同 parent 下子節點名稱呈 `<base><digit>` pattern：

- `tile1, tile2, tile3, tile4` → 一個 `<Base>` component；數字差異 → 推導 `state` / `variant` / `index` 列舉
- 推導列舉值的方式：橫向 diff 4 個 instance 的差異欄位（fill / text / icon / opacity）

### H3 — Prefix grouping

兩維前綴：`<kindLetter><indexDigit>` pattern：

- `chipA0, chipA1, chipA2, chipB0, chipB1, chipB2, chipB3` → 推導兩個列舉 `kind: "A"|"B"` × `count: number`
- caller 可改名再跑一次（heuristics 名稱保留 underscore / kebab 但仍可被偵測）

### H4 — 同 subtree 不同 content

子節點結構（type / 數量 / 排列）相同，但 `text.content` 不同：

- 推導 `content` prop（或更語義化的 `label` / `title` / `description`）
- 結構雷同的判定：比對 `.type / .children[] | .type` 序列一致（in-memory tree walk；Phase 5+ 操作的是 Phase 2 已 parse 進 `$$pen_doc` 的 dict，不再 shell-out）

### H5 — 同 subtree 不同 fill / text-color（state pair）

結構與內容皆相同，但 fill / text fill 不同：

- 推導 `state` enum；列舉值取設計者命名線索（`active` / `disabled` / `error` / `success`）

### H6 — `comp/` / `Component/` 前綴

節點 `name` 以 `comp/`、`Component/`、或 `cmp/` 開頭 → 顯式 component intent，強制抽。

## §2 Always inline（不抽 component）

無論結構多重複，下列 element 都 inline 在 page-level layout：

- `topBar` / `header` / `appBar`
- `bottomBar` / `tabBar` / `footer`
- `sidebar` / `drawer` / `nav`
- `hero` / `splash`
- 任何 `name` 以 `page` / `screen` / `route` 開頭的 frame

理由：layout primitive 抽 component 沒回收；scaffold 階段一次性寫進 `app/page.tsx` 即可。

## §3 不抽的 negative rules

- 子節點只出現過一次 → 不抽（無重用）
- 節點只是「容器」（無 fill / no children with own visual） → 不抽
- 節點是 `note` / `prompt` / `context` / `script` → SKIP（author-time annotation）

## §4 輸出表格契約（`$$component_table.rows`）

每一 row schema：

```yaml
Component: <PascalCase string>          # e.g. "PlayerCard"
SourceNodes: <comma-separated id list>  # e.g. "tile1,tile2,tile3,tile4"
DetectedProps:                          # 至少一個 prop
  - name: <camelCase>
    type: <"string" | "number" | "boolean" | enum literal union>
    derived_from: <H1|H2|H3|H4|H5|H6>
Stories: <PascalCase[]>                 # 觀察到的狀態名；3–6 上限
```

範例（人類可讀渲染）：

```
Component   | Source nodes        | Detected props                 | Stories
----------- | ------------------- | ------------------------------ | -------------------------------------
PlayerCard  | tile1–tile4         | name, state, hp, attempts      | Turn / Waiting / Critical / Defeated / Roster
ResultChip  | chipA0–A2, B0–B3    | kind:"A"|"B", count, active    | AHit / BHit / Empty
HPBar       | f4Ky5, t1bar–t4bar  | current, max, variant, defeated | BossFull / BossMid / BossLow / PlayerFull / PlayerLow / PlayerDefeated
```

## §5 顆粒度 sanity checks

- ASSERT 每 row 至少 1 個 prop（無差異 → 該節點實為 inline）
- ASSERT Stories 數量 ≥ 1，建議上限 6（更多 → 多半其實是不同 component，請拆 row）
- ASSERT Component name 為 PascalCase；小寫開頭強制改寫
- ASSERT SourceNodes 無重複（同節點不能屬於兩個 candidate）

## §6 Multi-screen 警告

Phase 5 的 input **只接受單一 screen subtree**。對多 screen 同時跑會導致：

- 同名節點跨 screen 混淆抽象（如 `topBar` 在 home 與 detail 結構不同卻被合併）
- 列舉值膨脹失控
- Component reuse 邊界不清

caller 想轉多個 screen → 多次呼叫本 skill，每次給一個 `screen_id`，最後 component library 自然合併
（同名 component 第二次寫入時走 `mode == "overwrite"` 或 caller 改名）。
