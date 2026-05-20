# DSL parameters coverage（已遷移）

本檔之前定義的「`S_contract` / `S_dsl` 集合相等」覆蓋規則、`default_bindings` 四鍵契約、L1/datatable 可讀性壓力閘門等，**已隨 schema 廢止而失效**。等價約束改由 `dsl_cli eval` 的 6 條 universal rules 承接（呼叫位置與規則名稱見 [SOP.md](../SOP.md) 步驟 5）：

| 舊規則 | 新對應 |
|---|---|
| L1 句內參數 ≤ 3 | `format-params-cap`（dsl_cli eval rule） |
| Datatable 業務欄位（套用 default 後）≤ 6 | `datatable-cap`（dsl_cli eval rule） |
| `default_bindings` 必含 `target`/`value`/`reason`/`override_via` 四鍵 | `datatable_bindings.<key>.default_value` 一鍵到位；`required: false` 即可選提供，reason 由 PR 描述／spec 文件承載（不再寫入 entry） |
| S_contract 與 S_dsl 鍵層級恰好一一對應 | 部分由 `format-key-binding-bijection`（format ↔ param_bindings 雙向覆蓋）覆寫；至於「coverage of all required spec inputs」屬 SEMANTIC 階段責任（從 plugin 寫入的「候選參數註解區塊」逐條決定 placement，禁止遺漏）。SEMANTIC 完成後若有違背，會在 `target-uri-scheme-validity` 或 `schema-completeness` 等規則被攔截。 |
| operation 之 `param_bindings` 不含 assertion bindings | `handler` 已表達意圖；同一 entry 不會混用 invoke + assert（invoke handler 與 verify handler 不同 entry） |

完整新規格與範例見 `research/aibdd-plan-dsl合成步驟超級 harness 計劃/spec.md`：
- §1 entry schema 與 7-handler 範例
- §1 Target URI Schemes 表
- §3 Solution Summary as Flow（HARNESS / SEMANTIC / EVAL 三階段）
