```gherkin
Rule: 前置（狀態） - 商品庫存必須大於 0

  Example: <意圖摘要>
    # @dsl
    # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
    # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md
    # candidates:
    #   - product.state-builder
    #   - createProduct.operation-invoke
    #   - adjustProductStock.operation-invoke
    #   - clock.time-control
    #   - inventoryService.external-stub
    Given <dsl>
    When <dsl>
    Then 操作失敗，錯誤為 "<具體錯誤訊息>"
    # @dsl
    # handler-candidate-kinds: state-verifier
    # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md
    # candidates:
    #   - product.state-verifier
    #   - cart.state-verifier
    And <dsl>
```