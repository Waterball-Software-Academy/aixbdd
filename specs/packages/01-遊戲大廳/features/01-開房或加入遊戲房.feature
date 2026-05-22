Feature: 開房或加入遊戲房

    玩家透過 HTTP 呼叫 openOrJoinRoom，以四位房號開新房或加入現有房。

    Rule: 前置（參數） - 房號必須為四位數字（0–9）
        Scenario Outline: <參數名> = <無效值> 時 <操作> 失敗
          # @dsl
          # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/precondition_building.md
          Given <dsl>
          # @dsl
          # handler-candidate-kinds: operation-invoke
          # rule: ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/rules/operation_invocation.md
          When <dsl>
          Then 操作失敗，錯誤為 "<具體驗證錯誤訊息>"

    Rule: 前置（狀態） - 加入現有房時房間人數必須少於 10
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

    Rule: 後置（狀態） - 若房號不存在，應建立新房間
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

    Rule: 後置（狀態） - 若房號不存在，玩家應成為房主（P1）
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

    Rule: 後置（狀態） - 若房號已存在，玩家應加入該房間
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

    Rule: 後置（狀態） - 若房號已存在，玩家應依序取得最小未使用的玩家編號

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
