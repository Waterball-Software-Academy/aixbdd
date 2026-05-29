Feature: eval rule `format-key-binding-bijection` enforces format ↔ param_bindings key mutual coverage

  Rule: 後置（回應）- format 引用 {key} 但 param_bindings 未定義 → FAIL
    Example: format 含 {房號}，param_bindings 缺
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 於房號 "{房號}" 加入
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/playerId
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "format-key-binding-bijection" is present

  Rule: 後置（回應）- param_bindings 定義 key 但 format 未引用 → FAIL
    Example: param_bindings 多了 暱稱 但 format 未含 {暱稱}
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 加入
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/playerId
              暱稱:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/nickname
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "format-key-binding-bijection" is present
