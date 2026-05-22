Feature: 玩家準備

    Rule: 前置（狀態） - 觸發者必須為房客（非房主）
        Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
          # @dsl
          # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/precondition_building.md
          Given <dsl>
          # @dsl
          # handler-candidate-kinds: operation-invoke
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/operation_invocation.md
          When <dsl>
          Then 操作失敗，錯誤為 "<具體錯誤訊息>"
          # @dsl
          # handler-candidate-kinds: state-verifier
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/state_verification_unchanged.md
          And <dsl>

    Rule: 後置（狀態） - 玩家應標記為已準備

        Example: <操作> 後 <狀態主詞> 變為 <新狀態>
          # @dsl
          # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/precondition_building.md
          Given <dsl>
          # @dsl
          # handler-candidate-kinds: operation-invoke
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/operation_invocation.md
          When <dsl>
          Then 操作成功
          # @dsl
          # handler-candidate-kinds: state-verifier
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/state_verification_changed.md
          And <dsl>
