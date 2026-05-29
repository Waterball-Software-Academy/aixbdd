Feature: append_templates writes HARNESS skeletons into `*.dsl.yml`, preserving existing entries

  Rule: 後置（狀態）- 對不存在之 dsl.yml 應建立新檔並寫入 skeleton
    Example: 寫入單條 operation-invoke skeleton
      When I append a template skeleton with the following fields to "contracts/room.dsl.yml":
        | field            | value                                                              |
        | handler          | operation-invoke                                                   |
        | name             | joinRoom.operation-invoke                                          |
        | target_part_path | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post         |
      Then the file "contracts/room.dsl.yml" contains the text "name: joinRoom.operation-invoke"
      And the file "contracts/room.dsl.yml" contains the text "handler: operation-invoke"
      And the file "contracts/room.dsl.yml" contains the text "<FILL IN>"
      And the file "contracts/room.dsl.yml" loads as a YAML mapping with key "dsl_steps"

  Rule: 後置（狀態）- 寫出之 skeleton 應含候選參數註解區塊
    Example: 兩條候選參數出現在 # 註解區
      When I append a template skeleton with the following fields to "contracts/room.dsl.yml":
        | field            | value                                                              |
        | handler          | operation-invoke                                                   |
        | name             | joinRoom.operation-invoke                                          |
        | target_part_path | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post         |
      And the template has candidate bindings:
        | key      | target                                                                                                                                                                  |
        | playerId | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/requestBody/content/application~1json/schema/properties/playerId                                            |
        | roomNo   | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/parameters/0                                                                                                 |
      And I flush the template buffer to "contracts/room.dsl.yml"
      Then the file "contracts/room.dsl.yml" contains the text "#   playerId:"
      And the file "contracts/room.dsl.yml" contains the text "#   roomNo:"
      And the file "contracts/room.dsl.yml" contains the text "param_bindings: {}"
      And the file "contracts/room.dsl.yml" contains the text "datatable_bindings: {}"
      And the file "contracts/room.dsl.yml" loads as a YAML mapping with key "dsl_steps"

  Rule: 後置（狀態）- 對既有 `dsl_steps: []` 空檔，應以 skeleton 取代 `[]` 不留殘餘
    Example: 從 dsl_steps: [] 起頭，append 後沒有 `[]` 殘留與 skeleton 並存
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps: []
        """
      When I append a template skeleton with the following fields to "contracts/room.dsl.yml":
        | field            | value                                                              |
        | handler          | operation-invoke                                                   |
        | name             | joinRoom.operation-invoke                                          |
        | target_part_path | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post         |
      Then the file "contracts/room.dsl.yml" does not contain the line "dsl_steps: []"
      And the file "contracts/room.dsl.yml" loads as a YAML mapping with key "dsl_steps"

  Rule: 後置（狀態）- 對既有非空 dsl.yml，append 後既有 entries 應原文保留、新 skeleton 接在末尾
    Example: 既有 SEMANTIC-filled entry + append HARNESS skeleton → 兩者同時存在
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 系統中已存在玩家 "{玩家Id}"
            name: users.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#users
            param_bindings:
              玩家Id:
                target: data/data.dbml#users.id
            datatable_bindings: {}
        """
      When I append a template skeleton with the following fields to "contracts/room.dsl.yml":
        | field            | value                                                              |
        | handler          | operation-invoke                                                   |
        | name             | joinRoom.operation-invoke                                          |
        | target_part_path | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post         |
      Then the file "contracts/room.dsl.yml" contains the text "name: users.state-builder"
      And the file "contracts/room.dsl.yml" contains the text "name: joinRoom.operation-invoke"
      And the file "contracts/room.dsl.yml" contains the text "玩家Id"
      And the file "contracts/room.dsl.yml" loads as a YAML mapping with key "dsl_steps"
