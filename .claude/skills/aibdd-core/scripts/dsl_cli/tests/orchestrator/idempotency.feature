Feature: generate-dsl-instructions is idempotent — re-running adds 0 new entries

  Background:
    Given a temporary file at "specs/contracts/room.api.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Room API
        version: 1.0.0
      paths:
        /rooms/{roomNo}/join:
          post:
            operationId: joinRoom
            responses:
              '200':
                description: OK
      """
    And a temporary file at "specs/contracts/room.dsl.yml" with content:
      """
      dsl_steps: []
      """

  Rule: 後置（狀態）- 同一 specs 重新 generate 應產生 0 added entries（prefix-match 視作 resolved）
    Example: 跑兩次，第二次的 report 沒有新增
      When dsl_cli generate-dsl-instructions runs for boundary "web-service"
      And dsl_cli generate-dsl-instructions runs again for boundary "web-service"
      Then the second run's GenerationReport has 0 added entries
