Feature: eval rule `format-params-cap` enforces ≤ 3 placeholders in format

  Rule: 後置（狀態）- format 句型內 3 個 {key} 以內應 PASS
    Example: 3 個參數的 invoke entry 通過
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 於房號 "{房號}" 以暱稱 "{暱稱}" 加入
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/playerId
              房號:
                target: contracts/room.api.yml#/paths/~1rooms/post/parameters/0
              暱稱:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/nickname
            datatable_bindings: {}
        """
      When evaluate runs
      Then EvalReport status is "PASS"

  Rule: 後置（回應）- format 句型內 > 3 個 {key} 應產出 format-params-cap violation
    Example: 4 個參數的 invoke entry 違規
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 於房號 "{房號}" 以暱稱 "{暱稱}" 與標籤 "{標籤}" 加入
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/playerId
              房號:
                target: contracts/room.api.yml#/paths/~1rooms/post/parameters/0
              暱稱:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/nickname
              標籤:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/tag
            datatable_bindings: {}
        """
      When evaluate runs
      Then EvalReport status is "FAIL"
      And a violation with rule_id "format-params-cap" is present
