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

契約欄位（custom isa 契約，外加一個 AIBDD 註記欄 `intent`）：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `name` | 是 | 指令唯一名，同檔不得重複 |
| `format` | 是 | regex，以 `(?P<name>...)` 具名群組擷取參數，`^…$` 包住整句 |
| `instruction_type` | 是 | 固定 `custom` |
| `intent` | 是 | **測試意圖／行為**（給下游 red-execute 實作 step def 用）。一句話描述「這條 custom 觀察到的行為」，含步驟角色（Given 前置／When 動作／Then 斷言）。**只寫 WHAT（可觀察行為），不寫 HOW（不提 context 欄位、status code 範圍、程式呼叫）**。為 AIBDD 註記欄，不影響 isa 指令執行（展開／執行階段忽略未知鍵） |
| `data_format` | 視情況 | `data_table` / `json`（有 payload 時） |
| `export_vars` | 選填 | 輸出契約：執行後導出哪些 `$var`。key 可用 `{{param}}` 插值 format 群組；值含 `type`(String/Number/Boolean)＋`description`＋選填 `example`／`nullable` |
| `datatable_parameters` | 選填 | 輸入契約：DataTable 欄位 schema。每欄 `type`(String/Number/Boolean/Time)＋`description`＋選填 `required`／`enums` |
| `allow_dynamic_parameters` | 選填 | 預設 false；true 時接受未宣告 header |

契約怎麼填，由 step 3-2 推出的測試意圖與資料流決定：此 custom 的 `intent`（觀察到什麼行為）、該輸出什麼 `$var`（供後續 dsl_step 引用）、吃哪些 DataTable 欄位。

`intent` 範例（WHAT，不是 HOW；且前提是「builtin 真的做不到」才宣告 custom）：

- ✅ 好（確實只能 custom —— 外部資源 / 多步前置封裝）：
  - `前置：以 stub 讓外部徵信服務對統編 "{{taxId}}" 回傳「拒絕往來」`（外部資源 mock，無對應 builtin）
  - `前置：建立一筆已過副理、停在區經理關卡的審核中申請（同時寫入申請主檔與逐關審核紀錄）`（跨多表前置，單一 entity_setup 表達不了）
- ❌ 不該宣告 custom（這些有 builtin，請改用，別包成 custom）：
  - `斷言回應為失敗（非 2xx）`、`驗回應的 message 欄位` → builtin `response_validate`（狀態碼寫進句子）
  - `建立一筆 tb_user／單一 entity 並導出 id` → builtin `entity_setup`
  - `呼叫某 API 操作` → builtin `api_call`
- ❌ HOW（實作細節，不論如何都不寫進 intent）：`status 介於 400–499`、`objectMapper.readTree(body).path("message")`

判定 custom 前，先過 `builtin-instruction-decision-tree.md` 的決策流程；**只有走到第 5 點（外部資源 mock／非 HTTP／多步前置封裝）才是 custom**。能用 builtin 拆成數條有序 isa_step 表達的，一律不做 custom。

## 引用 custom 時：把 datatable_parameters 鏡射回 dsl_step

某條 isa_step 對上的指令（custom 或內建）若 `data_format: data_table` 且 isa.yml 宣告了
`datatable_parameters`，**該 dsl_step 必須把欄位 schema 鏡射出來**，否則展開後 DataTable 是空的、
Linter 也驗不到欄位（本流程 step d 的 `expand_isa.py` 會對「缺 params/table」發 lint 警告）：

- `params`：列出 `datatable_parameters` 的全部 key。
  - `required: true` 且無預設 → 進必填清單 `[k1, k2, …]`；
  - 有合理預設（情境無關欄位）→ 用 `{ k: 預設 }`。
- `isa_steps[].table`：每個 key 一列，值預設 `'{{key}}'`（內插同名 param/capture）；
  該欄若要捕獲／斷言／時間，再依符號系統改成 `>`/`<`/`&`/`@`（見 symbol-system-usage.md）。

### Good（isa.yml 宣告 → dsl_step 鏡射）

```yaml
# isa.yml（契約）—— 外部資源 mock（無 builtin），且帶 DataTable
- name: 外部徵信回應設定
  format: ^外部徵信服務對下列統編回應：$
  instruction_type: custom
  intent: 前置：以 stub 設定外部徵信服務對多筆統編的回應（外部資源，無對應 builtin）
  data_format: data_table
  datatable_parameters:
    統編:     { type: String, required: true, description: 公司統一編號 }
    徵信結果: { type: String, required: true, description: 徵信回應（如 拒絕往來／正常） }
```
```yaml
# dsl.yml（鏡射 → 展開後才有完整 DataTable）
- name: 外部徵信回應
  format: '外部徵信服務對下列統編回應：'
  params: [統編, 徵信結果]
  isa_steps:
    - instruction: '外部徵信服務對下列統編回應：'
      table:
        統編: '{{統編}}'
        徵信結果: '{{徵信結果}}'
```

### Bad

```yaml
# 對上 data_table custom 卻只寫 instruction、漏 params/table → 展開 DataTable 全空
- name: 外部徵信回應
  format: '外部徵信服務對下列統編回應：'
  isa_steps:
    - instruction: '外部徵信服務對下列統編回應：'
```

## Good

```yaml
# package 層 isa.yml：把「是一個管理員」封裝成 custom，宣告契約即可（實作留 RED）
- name: Admin setup
  format: ^"(?P<alias>[^"]+)" 是一個管理員, with table:$
  instruction_type: custom
  intent: 前置：建立管理員並一次補齊其角色與權限關聯（跨 user／role／permission／role_permission 多表，單一 entity_setup 表達不了），導出其 id
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
