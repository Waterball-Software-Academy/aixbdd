# SOP

[LOOP] 針對此 Feature File 中的每一個 DSL Step，為了實作其對應的 StepDefinition，嚴格遵守底下步驟:

1. 首先先參考 `$STEP_DEFINITIONS_RUNTIME_REF` 中本專案存放 Step definition 程式碼的位置，透過 glob, grep 模糊查詢此 DSL Step format 來確認此 DSL 之對應 StepDefinition 是否已經實作在本專案中。

若有，則 SKIP，直接進行下一圈，否則繼續步驟 2

2. 每一個 DSL Step（Given/When/Then 後面的句子）都已儲存在 `**.dsl.yml` 某處；禁止直接 `Read` / `Grep` 任何 `*.dsl.yml`。請遵照 `.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/kits/how-to-look-up-dsl.md` 中的指示，結合底下基本參數用法教學，來查詢 DSL Step 的完整定義 Entries。
    1. `--handler` 與 `--step-text` 至少提供其一；可只傳 `--step-text` 掃完整 corpus，或兩者併用縮小候選。
    2. `--handler` 可重複；只查一般檔時用 `--source-scope regular` 並省略 `--shared-dsl`；只查 `${BOUNDARY_SHARED_DSL}` 時用 `--source-scope shared` 且 `--dsl` 可省略。
    3. 非 0 退出 → 停下來，回報 `stop_reason: dsl_cli_query_failed` 並透傳 stderr。
3. BIND `$DSL_CURRENT_STEP` = 從 dsl_cli query 中解析的 JSON stdout。並進一步確認其包含符合此 DSL Step 之完整定義，定義中必須至少包含 `format`、`handler`、`target_part_path`、`param_bindings`、`datatable_bindings`。
4. 接著要去實作此 StepDefinition 了，你需要閱讀 boundary assets 與 runtime ref 來理解撰寫此 DSL 之對應 StepDefinition 的最佳程式實踐：
    1. READ `${STEP_DEFINITIONS_RUNTIME_REF}` 了解 StepDef 共通管理方式。
    2. IF `.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/handlers/${DSL_CURRENT_STEP.handler}.md` 存在 → READ 它；否則 SKIP（web-frontend 等 boundary 可能尚未建立 handlers/）。
    3. READ `.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/variants/${STARTER_VARIANT}.md`
    4. 結合上述三者之理解，實作此 StepDefinition 之程式。其中最關鍵的要素是：`$DSL_CURRENT_STEP` 中所有 `param_bindings` 和 `datatable_bindings` 中的參數，都要自 gherkin 參數中解析而來（無論 `required 為 true or false`），這樣當 dsl step 中有指定此參數時，測試就能接收到。而另外更重要的：針對 `datatable_bindings` 中`required=false` 但卻有定義 `default_value` 的參數，這代表此參數有預設值，此時一定要在程式中判斷：若 Datatable 無提供此參數，則要在程式碼中直接「寫死」預設值。
      - 例子（python-e2e / Behave，電商）：先定義對應 DSL entry（`$DSL_CURRENT_STEP` 即此筆），再寫 Gherkin 與 StepDefinition。
          ```yaml
          dsl_steps:
            - format: 系統中已存在訂單 "{訂單編號}"
              name: orders.state-builder
              handler: state-builder
              target_part_path: specs/data/orders.dbml#orders
              param_bindings:
                訂單編號:
                  target: specs/data/orders.dbml#orders.order_no
              datatable_bindings:
                訂單狀態:
                  target: specs/data/orders.dbml#orders.status
                  required: false
                  default_value: PENDING
                商品總額:
                  target: specs/data/orders.dbml#orders.subtotal_cents
                  required: false
                運費:
                  target: specs/data/orders.dbml#orders.shipping_cents
                  required: false
          ```
          ```gherkin
          Given 系統中已存在訂單 "ORD-2026-001"
            | 商品總額 | 運費 |
            | 1500     | 80   |
          ```
          ```python
          from behave import given

          @given('系統中已存在訂單 "{訂單編號}"')
          def step_seed_order(context, 訂單編號: str):
              row = _datatable_row(context)
              訂單狀態 = row.get("訂單狀態", "PENDING")
              商品總額 = row.get("商品總額")
              運費 = row.get("運費")
              context.repos.orders.seed(
                  order_no=訂單編號,
                  status=訂單狀態,
                  subtotal_cents=int(商品總額) if 商品總額 is not None else None,
                  shipping_cents=int(運費) if 運費 is not None else None,
              )


          def _datatable_row(context) -> dict[str, str | None]:
              if context.table is None:
                  return {}
              headings = [cell.strip() for cell in context.table.headings]
              cells = [cell.strip() for cell in context.table.rows[0]]
              return {
                  heading: (cell if cell != "" else None)
                  for heading, cell in zip(headings, cells, strict=True)
              }
          ```
          - 上例 DSL 中 `訂單狀態.default_value: PENDING` 對應 StepDef 的 `row.get("訂單狀態", "PENDING")`；DataTable 未提供該欄時套用預設值。`商品總額`、`運費` 有欄則從 table 取值，未提供則為 `None`。
          - 另外，`_datatable_row` 應被抽到專案的共用 helper 中，請先依照 handler 指示使用此專案的共用 helpers。

# Checklist

1. 確認 stepdef 的 matcher 字串，和 `$DSL_CURRENT_STEP.format`一致。
2. 確認內容裡沒有自由發揮的 step-def、沒有寫死的 locator、沒有自己腦補的受測 endpoint／欄位／id。
3. 確認重複註冊的防呆機制下，共用步驟只被註冊剛好一次。
