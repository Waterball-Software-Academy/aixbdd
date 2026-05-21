Feature: dsl_cli eval grades a corpus end-to-end

  Rule: 後置（狀態）- 合規之 corpus 應 PASS
    Example: 單條合規 entry
      Given a temporary file at "specs/contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/playerId
            datatable_bindings: {}
        """
      When dsl_cli eval runs against the last file
      Then the eval-run EvalReport status is "PASS"

  Rule: 後置（回應）- 違規之 corpus 應 FAIL 並附對應 rule_id
    Example: 4 個 {key} 觸發 format-params-cap
      Given a temporary file at "specs/contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 於房號 "{房號}" 暱稱 "{暱稱}" 標籤 "{標籤}" 加入
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
      When dsl_cli eval runs against the last file
      Then the eval-run EvalReport status is "FAIL"
      And the eval-run EvalReport violations include rule_id "format-params-cap"
