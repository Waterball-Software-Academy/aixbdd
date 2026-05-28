Feature: dsl_reader.load_dsl_files reads `*.dsl.yml` into DSLEntry dataclasses

  Rule: 後置（狀態）- 載入後每條 entry 應 hydrate 為 DSLEntry，含 format/name/handler/target_part_path
    Example: contracts/room.dsl.yml 內單條 invoke entry 完整 hydrate
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 於大廳以房號 "{房號}" 開房或加入
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/requestBody/content/application~1json/schema/properties/playerId
              房號:
                target: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/parameters/0
            datatable_bindings: {}
        """
      When dsl_reader loads the last file
      Then loaded entries count is 1
      And entry "joinRoom.operation-invoke" has handler "operation-invoke"
      And entry "joinRoom.operation-invoke" has target_part_path "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post"
      And entry "joinRoom.operation-invoke" has param_binding "玩家Id" with target "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/requestBody/content/application~1json/schema/properties/playerId"

  Rule: 後置（狀態）- 含 required + default_value 的 datatable_bindings 應完整 hydrate
    Example: optional binding with default_value 保留所有欄位
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家 "{玩家Id}" 於大廳開房
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/playerId
            datatable_bindings:
              暱稱:
                required: false
                target: contracts/room.api.yml#/paths/~1rooms/post/requestBody/content/application~1json/schema/properties/nickname
                default_value: "Guest Name"
        """
      When dsl_reader loads the last file
      Then entry "joinRoom.operation-invoke" has datatable_binding "暱稱" with required false and default_value "Guest Name"

  Rule: 後置（狀態）- 空檔（`dsl_steps: []` 或全空）應回傳空 entries 列表
    Example: 空 dsl_steps list → 0 entries
      Given a temporary file at "contracts/empty.dsl.yml" with content:
        """
        dsl_steps: []
        """
      When dsl_reader loads the last file
      Then loaded entries count is 0
