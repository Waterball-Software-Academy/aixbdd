Feature: eval rule `residual-candidate-comment-block` rejects leftover generator comments

  Rule: 後置（狀態）- 候選參數註解區塊殘留應 FAIL
    Example: format 已填字但候選參數註解未清掉
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 查詢房間 "{房Id}" 快照
            name: getRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1{roomId}/get
              # 候選參數（請挑選後分別填入 param_bindings / datatable_bindings；填完整段註解一併刪除）：
              #   roomId:
              #     target: contracts/room.api.yml#/paths/~1rooms~1{roomId}/get/parameters/0
            param_bindings:
              房Id:
                target: contracts/room.api.yml#/paths/~1rooms~1{roomId}/get/parameters/0
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "residual-candidate-comment-block" is present
