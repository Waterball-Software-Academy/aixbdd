Feature: 房主開始遊戲

    Rule: 前置（狀態） - 觸發者必須為房主（P1）
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

    Rule: 前置（狀態） - 房間人數必須達到 2 位或以上
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

    Rule: 前置（狀態） - 所有房客必須已準備
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

    Rule: 後置（狀態） - 遊戲應進入階段一（密碼設置階段）
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

    Rule: 後置（狀態） - 魔王血量上限應設為玩家數量乘以 1000

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
