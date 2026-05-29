Feature: apply when format to When placeholders

  Rule: 後置（狀態） - 單一 feature 內所有 When placeholder 應替換為選定 format
    Example: 多個 Example 共用同一 when format
      Given a temporary file at "game.feature" with content:
        """
        Feature: 商品庫存

            Rule: 前置（狀態） - 商品庫存必須大於 0

                Example: 庫存不足時加入購物車失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - product.state-builder
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "庫存不足"

            Rule: 前置（狀態） - 商品必須存在

                Example: 商品不存在時加入購物車失敗
                  When <dsl>
                  Then 操作失敗，錯誤為 "商品不存在"
        """
      When when-format apply is run on the last feature file with format:
        """
        玩家 "<playerKey>" 加入購物車
        """
      Then the last feature file content should equal:
        """
        Feature: 商品庫存

            Rule: 前置（狀態） - 商品庫存必須大於 0

                Example: 庫存不足時加入購物車失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder
                  # rule: dsl-arrangement-rules/shared-given-law.md
                  # candidates:
                  #   - product.state-builder
                  Given <dsl>
                  When 玩家 "<playerKey>" 加入購物車
                  Then 操作失敗，錯誤為 "庫存不足"

            Rule: 前置（狀態） - 商品必須存在

                Example: 商品不存在時加入購物車失敗
                  When 玩家 "<playerKey>" 加入購物車
                  Then 操作失敗，錯誤為 "商品不存在"
        """

  Rule: 後置（回應） - 無 When placeholder 時不變更
    Example: 已是具體 When 行時 apply 為 no-op
      Given a temporary file at "concrete-when.feature" with content:
        """
        Feature: 已套用

            Rule: 前置（狀態） - x

                Example: y
                  When 玩家 "P1" 加入購物車
                  Then 操作成功
        """
      When when-format apply is run on the last feature file with format:
        """
        玩家 "<playerKey>" 加入購物車
        """
      Then the last feature file content should equal:
        """
        Feature: 已套用

            Rule: 前置（狀態） - x

                Example: y
                  When 玩家 "P1" 加入購物車
                  Then 操作成功
        """

  Rule: 後置（狀態） - 第二次 apply 不變更
    Example: 同 format 重跑 idempotent
      Given a temporary file at "idempotent.feature" with content:
        """
        Feature: idempotent

            Rule: 前置（狀態） - x

                Example: y
                  When <dsl>
                  Then 操作失敗
        """
      And when-format apply is run on the last feature file with format:
        """
        玩家 "<playerKey>" 加入購物車
        """
      When when-format apply is run again on the last feature file with format:
        """
        玩家 "<playerKey>" 加入購物車
        """
      Then the last feature file content should equal:
        """
        Feature: idempotent

            Rule: 前置（狀態） - x

                Example: y
                  When 玩家 "<playerKey>" 加入購物車
                  Then 操作失敗
        """

  Rule: 後置（回應） - 空 format 不改檔且記錄 question
    Example: 空 format 保留原文
      Given a temporary file at "empty-format.feature" with content:
        """
        Feature: 空 format

            Rule: 前置（狀態） - x

                Example: y
                  When <dsl>
                  Then 操作失敗
        """
      When when-format apply is run on the last feature file with empty format
      Then when format questions should equal:
        """
        - where: empty-format.feature:1
          type: missing-when-format
          text: --format must be a non-empty when step format for empty-format.feature
        """
      And the last feature file content should equal:
        """
        Feature: 空 format

            Rule: 前置（狀態） - x

                Example: y
                  When <dsl>
                  Then 操作失敗
        """

  Rule: 後置（回應） - apply_when_format CLI 回傳 JSON report
    Example: 成功 apply 時 JSON report 含 updated_when_count
      Given a temporary file at "cli.feature" with content:
        """
        Feature: cli

            Rule: 前置（狀態） - x

                Example: y
                  When <dsl>
                  Then 操作失敗
        """
      When apply_when_format CLI is run on the last feature file with format:
        """
        玩家 "<playerKey>" 加入購物車
        """
      Then CLI exit code is 0
      And CLI apply JSON report should equal:
        """
        {
          "changed_count": 1,
          "feature_count": 1,
          "changed_features": ["cli.feature"],
          "updated_when_count": 1,
          "questions": [],
          "report": {
            "summary": "changed=1 features=1 whens=1 questions=0"
          }
        }
        """
      And no file exists at "reports/bdd-analyze-cic.md"
