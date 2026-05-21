Feature: eval rule `schema-completeness` enforces non-empty required fields

  Rule: 後置（回應）- format 仍為 <FILL IN> 應 FAIL
    Example: HARNESS-only entry 尚未 SEMANTIC 填字
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: "<FILL IN>"
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "schema-completeness" is present
