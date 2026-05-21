Feature: dsl_reader.index_resolved_parts collects every entry's target_part_path into a set

  Rule: 後置（狀態）- 跨多檔多 entry 的 target_part_path 應 deduplicated 收成 set
    Example: 兩檔三 entry → 三條 unique target_part_path
      Given a temporary file at "contracts/room.dsl.yml" with content (saved as "room"):
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 系統回應加入房間成功
            name: joinRoom.operation-response-success-and-failure
            handler: operation-response-success-and-failure
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post/responses/200
            param_bindings: {}
            datatable_bindings: {}
        """
      And a temporary file at "data/data.dsl.yml" with content (saved as "data"):
        """
        dsl_steps:
          - format: 系統內已存在玩家
            name: users.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#users
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_reader loads files aliased "room" and "data"
      And index_resolved_parts is computed on the loaded entries
      Then the resolved parts set has exactly 3 items
      And the resolved parts set contains "contracts/room.api.yml#/paths/~1rooms/post"
      And the resolved parts set contains "contracts/room.api.yml#/paths/~1rooms/post/responses/200"
      And the resolved parts set contains "data/data.dbml#users"
