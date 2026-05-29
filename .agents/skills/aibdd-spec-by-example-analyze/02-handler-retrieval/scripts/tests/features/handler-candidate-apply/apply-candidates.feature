Feature: apply handler candidates to # @dsl blocks

  Background:
    Given a temporary file at "contracts/game.dsl.yml" with content:
      """
      dsl_steps:
        - format: 玩家加入購物車
          name: addToCart.operation-invoke
          handler: operation-invoke
          target_part_path: contracts/cart.api.yml#/paths/~1cart/post
          param_bindings: {}
          datatable_bindings: {}
        - format: 建立商品
          name: createProduct.operation-invoke
          handler: operation-invoke
          target_part_path: contracts/product.api.yml#/paths/~1products/post
          param_bindings: {}
          datatable_bindings: {}
        - format: 商品狀態
          name: product.state-builder
          handler: state-builder
          target_part_path: data/product.dbml#products
          param_bindings: {}
          datatable_bindings: {}
        - format: 商品驗證
          name: product.state-verifier
          handler: state-verifier
          target_part_path: data/product.dbml#products
          param_bindings: {}
          datatable_bindings: {}
      """
    And a temporary file at "data/inventory.dsl.yml" with content:
      """
      dsl_steps:
        - format: 調整庫存
          name: adjustProductStock.operation-invoke
          handler: operation-invoke
          target_part_path: data/inventory.dbml#stock
          param_bindings: {}
          datatable_bindings: {}
      """
    And a temporary shared DSL file at "shared/boundary.dsl.yml" with content:
      """
      dsl_steps:
        - format: 時鐘
          name: clock.time-control
          handler: time-control
          target_part_path: literal:clock
          param_bindings: {}
          datatable_bindings: {}
        - format: 庫存 stub
          name: inventoryService.external-stub
          handler: external-stub
          target_part_path: stub_payload:inventory
          param_bindings: {}
          datatable_bindings: {}
      """

  Rule: 後置（狀態） - 無 candidates 時應插入在 rule 之後
    Example: 多 kind ordered union 含 shared-only kinds
      Given a temporary file at "game.feature" with content:
        """
        Feature: 商品庫存

            Rule: 前置（狀態） - 商品庫存必須大於 0

                Example: 庫存不足時加入購物車失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "庫存不足"
        """
      When handler-candidate apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 商品庫存

            Rule: 前置（狀態） - 商品庫存必須大於 0

                Example: 庫存不足時加入購物車失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - product.state-builder
                  #   - addToCart.operation-invoke
                  #   - createProduct.operation-invoke
                  #   - adjustProductStock.operation-invoke
                  #   - clock.time-control
                  #   - inventoryService.external-stub
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "庫存不足"
        """

  Rule: 後置（狀態） - 已有 candidates 時整段覆寫
    Example: 新 catalog 順序覆寫舊 candidates
      Given a temporary file at "overwrite.feature" with content:
        """
        Feature: 覆寫

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: state-builder
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - stale.state-builder
                  Given <dsl>
                  When <dsl>
        """
      When handler-candidate apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 覆寫

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: state-builder
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - product.state-builder
                  Given <dsl>
                  When <dsl>
        """

  Rule: 後置（狀態） - shared-only dsl kinds 不誤吃 regular dsl kinds
    Example: time-control 只來自 shared 檔
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 錯誤 scope
            name: clock.time-control
            handler: time-control
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      And a temporary file at "shared-only.feature" with content:
        """
        Feature: shared only

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: time-control
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
        """
      When handler-candidate apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: shared only

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: time-control
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - clock.time-control
                  Given <dsl>
                  When <dsl>
        """

  Rule: 後置（回應） - 缺少 handler-candidate-kinds 不改檔且記錄 question
    Example: 缺 kinds 欄位 skip block
      Given a temporary file at "missing-kinds.feature" with content:
        """
        Feature: 缺 kinds

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
        """
      When handler-candidate apply is run on the last feature file
      Then handler candidate questions should equal:
        """
        - where: missing-kinds.feature:6
          type: missing-handler-candidate-kinds
          text: # @dsl block at missing-kinds.feature:6 has no # handler-candidate-kinds:
        """
      And the last feature file content should equal:
        """
        Feature: 缺 kinds

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
        """

  Rule: 後置（回應） - union 為空時保留空 candidates 並記錄 question
    Example: 未知 kind 零命中
      Given a temporary file at "empty-union.feature" with content:
        """
        Feature: 空 union

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: unknown-kind
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
        """
      When handler-candidate apply is run on the last feature file
      Then handler candidate questions should equal:
        """
        - where: empty-union.feature:6
          type: no-candidates-found
          text: kinds ['unknown-kind'] matched no dsl entry in empty-union.feature:6
        """
      And the last feature file content should equal:
        """
        Feature: 空 union

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: unknown-kind
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  Given <dsl>
                  When <dsl>
        """

  Rule: 後置（狀態） - 第二次 apply 不變更
    Example: idempotent re-run
      Given a temporary file at "idempotent.feature" with content:
        """
        Feature: idempotent

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: state-builder
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
        """
      And handler-candidate apply is run on the last feature file
      When handler-candidate apply is run again on the last feature file
      Then the last feature file content should equal:
        """
        Feature: idempotent

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: state-builder
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - product.state-builder
                  Given <dsl>
                  When <dsl>
        """

  Rule: 後置（回應） - apply_handler_candidates CLI 回傳 JSON report
    Example: 成功 apply 時 JSON report 含 changed_count
      Given a temporary file at "cli.feature" with content:
        """
        Feature: cli

            Rule: 前置（狀態） - x

                Example: y
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  Given <dsl>
                  When <dsl>
        """
      When apply_handler_candidates CLI is run on the last feature file
      Then CLI exit code is 0
      And CLI apply JSON report should equal:
        """
        {
          "changed_count": 1,
          "feature_count": 1,
          "changed_features": ["cli.feature"],
          "updated_block_count": 1,
          "questions": [],
          "report": {
            "summary": "changed=1 features=1 blocks=1 questions=0"
          }
        }
        """
      And no file exists at "reports/bdd-analyze-cic.md"
