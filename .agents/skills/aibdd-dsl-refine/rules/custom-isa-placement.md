# custom isa 放置與宣告

某條 isa_step 對不上任何內建型別（見 [builtin-instruction-decision-tree.md](builtin-instruction-decision-tree.md)
決策流程第 5 點：外部資源 mock、非 HTTP 操作、把多步前置語意封裝成一句）時，走 custom。
本檔規範「先找、找不到才宣告、宣告寫哪層、宣告寫到什麼程度」。

## 先找：由內往外到 specs

custom 的真相同樣是 isa.yml，但分層。判斷該 custom 是否已定義，從該 feature 的 package 層往最外層找：

1. 該 feature 所在 package 的 `*.isa.yml`（最內）
2. `specs/isa.yml`（最外）

任一層已有 format 對得上的 custom 指令 → 直接引用，不重複宣告。

## 找不到才宣告：放哪層

未定義時當場宣告，放置優先序：

- 預設寫進**該 feature 所在 package 目錄**的 isa.yml（檔不存在則建立）——模組分割優先，custom 跟著用到它的模組走。
- 僅當判斷**可共用**才上 `specs/isa.yml`：跨 ≥2 個 package 會用到，或本質是跨領域的外部資源（如 payment gateway stub）。
- 同 package 內可依「面對不同測試設計的步驟」分多個 `*.isa.yml`（如 mock-api、外部 stub 各一檔）。

## 宣告到什麼程度：只寫契約

phase 2 只寫 isa.yml 的**契約**，供 Linter 驗證 feature 用法；
Cucumber Step Definition（Java 實作）由 **RED 階段**完成，本階段不得寫實作。

契約欄位（忠實對應框架 custom config）：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `name` | 是 | 指令唯一名，同檔不得重複 |
| `format` | 是 | regex，以 `(?P<name>...)` 具名群組擷取參數，`^…$` 包住整句 |
| `instruction_type` | 是 | 固定 `custom` |
| `data_format` | 視情況 | `data_table` / `json`（有 payload 時） |
| `export_vars` | 選填 | 輸出契約：執行後導出哪些 `$var`。key 可用 `{{param}}` 插值 format 群組；值含 `type`(String/Number/Boolean)＋`description`＋選填 `example`／`nullable` |
| `datatable_parameters` | 選填 | 輸入契約：DataTable 欄位 schema。每欄 `type`(String/Number/Boolean/Time)＋`description`＋選填 `required`／`enums` |
| `allow_dynamic_parameters` | 選填 | 預設 false；true 時接受未宣告 header |

契約怎麼填，由 step 3-2 推出的測試意圖與資料流決定：此 custom 該輸出什麼 `$var`（供後續 dsl_step 引用）、吃哪些 DataTable 欄位。

## Good

```yaml
# package 層 isa.yml：把「是一個管理員」封裝成 custom，宣告契約即可（實作留 RED）
- name: Admin setup
  format: ^"(?P<alias>[^"]+)" 是一個管理員, with table:$
  instruction_type: custom
  data_format: data_table
  export_vars:
    "{{alias}}.id":
      type: Number
      description: "管理員 ID"
      nullable: false
  datatable_parameters:
    role:
      type: String
      required: true
      description: "管理員角色"
      enums: ["SUPER_ADMIN", "EDITOR", "VIEWER"]
```

## Bad

```yaml
# 兩三條 entity_setup 就能達成卻硬包成 custom（應直接用內建 entity_setup）
- name: Trivial seed
  format: ^建立一筆資料$
  instruction_type: custom
# format 用 {name} 佔位（custom 的 isa 指令 format 必須是 regex 具名群組）
- name: Bad format
  format: '"{alias}" 是一個管理員'        # 應為 ^"(?P<alias>[^"]+)" 是一個管理員$
  instruction_type: custom
# 在 isa.yml 契約裡塞 handler 實作細節 / Step Definition（屬 RED，不在此階段）
```
