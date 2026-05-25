# <boundary-id> preset — plan-time plugin contract（authoring template）

1. 本檔以人類可讀方式記載此 preset 的 `scripts/part_to_dsl.py` 在「構造期（plan-time）」必須保證的履約規則。plugin 程式碼是行為本體，本檔是規範敘事，兩者語義必須一致。
2. 適用範圍：只談 plan-time（template skeleton 構造）的履約。runtime / red-execute 的 context 讀寫與禁令由 `handlers/<handler>.md` 承載，不在此重述。
3. 撰寫方式：每個 handler 一個 `##` 區段；每段宣告該 handler 的 required source 與 plugin 必須構造性保證的綁定規則。複製下方範本逐 handler 填寫。

## <handler-id>

1. Required source：`<data_model|operation_contract|operation_contract_response|test_strategy|...>`。宣告此 handler 的 template 一定要有哪一類來源 spec 才合法。
2. Optional source：`<provider_contract|...>`（若無可選來源，刪掉本行）。
3. Plugin 構造保證（plan-time 一定成立的不變式，逐條寫清楚 why）：
   1. `target_part_path` 指向什麼錨點（例：`<spec_file>#<table_name>` 或 `<spec_file>#/paths/<escaped_path>/<method>`），以及為什麼必須唯一。
   2. `candidate_bindings` 涵蓋哪些欄位、target 走哪一種 URI scheme（例：DBML anchor / `response:` JSONPath / `literal:` type-hint / `stub_payload:` field），以及不得使用哪種 scheme。
   3. 此 handler 不負責的語意（例：invoke handler 不做 response 斷言），把它推給哪個 sibling handler。
   4. SEMANTIC 階段（AI 填值）必須補到的覆蓋條件（例：100% 覆蓋 NOT-NULL columns，列出例外）。

## Eval-time 補強

1. 以上履約是 plan-time 構造規範，不是 `dsl_cli eval` 規則。
2. `dsl_cli eval` 只跑 6 條 universal rules（format-params-cap、datatable-cap、schema-completeness、name-uniqueness、format-key-binding-bijection、target-uri-scheme-validity），不重複檢查 handler↔scheme 對應。
3. 因此 handler↔scheme 的合法性必須由本 preset 的 `part_to_dsl.py` 構造性保證，不能指望 eval 事後攔截。
