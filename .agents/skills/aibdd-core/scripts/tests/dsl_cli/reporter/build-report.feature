Feature: reporter renders GenerationReport / EvalReport as human-readable text

  Rule: 後置（狀態）- GenerationReport 應列每條新增 entry 與目的檔
    Example: 兩條新增 entry 各列一行
      When a GenerationReport with the following added entries is rendered:
        | entry_name                | target_file           | handler                  |
        | joinRoom.operation-invoke | contracts/room.dsl.yml| operation-invoke         |
        | users.state-builder       | data/data.dsl.yml     | state-builder            |
      Then the rendered generation report contains "Added 2 entries:"
      And the rendered generation report contains "joinRoom.operation-invoke -> contracts/room.dsl.yml (operation-invoke)"
      And the rendered generation report contains "users.state-builder -> data/data.dsl.yml (state-builder)"

  Rule: 後置（狀態）- 無 violation 之 EvalReport 應顯示 "No violations."
    Example: PASS 報告
      When an EvalReport with status "PASS" total_entries 5 and no violations is rendered
      Then the rendered eval report contains "PASS"
      And the rendered eval report contains "Total entries: 5"
      And the rendered eval report contains "No violations."

  Rule: 後置（狀態）- FAIL EvalReport 應列出每條 violation 之 rule_id / entry_name / message / hint
    Example: 一條 format-params-cap violation
      When an EvalReport with status "FAIL" and the following violations is rendered:
        | rule_id           | entry_name                | entry_file              | message                          | hint                                  |
        | format-params-cap | joinRoom.operation-invoke | contracts/room.dsl.yml  | format 句型含 4 個參數，超過上限 3 | 拆成兩條 DSL instruction               |
      Then the rendered eval report contains "[format-params-cap] joinRoom.operation-invoke @ contracts/room.dsl.yml"
      And the rendered eval report contains "format 句型含 4 個參數，超過上限 3"
      And the rendered eval report contains "hint: 拆成兩條 DSL instruction"
