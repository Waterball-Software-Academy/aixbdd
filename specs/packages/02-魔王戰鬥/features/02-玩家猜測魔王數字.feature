Feature: 玩家猜測魔王數字

    Rule: 前置（狀態） - 遊戲必須處於階段二（對戰階段）
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

    Rule: 前置（狀態） - 必須輪到該玩家的回合
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

    Rule: 前置（狀態） - 玩家必須存活（未出局）
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

    Rule: 前置（參數） - 猜測數字必須為四位數字（0–9）
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

    Rule: 前置（參數） - 猜測數字的四位必須各不重複
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

    Rule: 後置（狀態） - 猜測結果應依 1A2B 規則計算 A 值與 B 值
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

    Rule: 後置（狀態） - 魔王血量應依加權公式（基於 A、B 值）扣除傷害值
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

    Rule: 後置（狀態） - 若魔王血量歸零，遊戲應結束且玩家勝利
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

    Rule: 後置（狀態） - 玩家隊存活玩家全數行動後，應自動觸發魔王回合
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

    Rule: 後置（狀態） - 魔王回合應依機率選擇行動（群傷 40%／單體 30%／自療 20%／改密碼 10%）
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

    Rule: 後置（狀態） - 若本輪任一玩家曾猜中魔王 4A，魔王行動應強制為改變密碼
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

    Rule: 後置（狀態） - 魔王攻擊後若玩家血量歸零，玩家應出局
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

    Rule: 後置（狀態） - 所有玩家出局後，遊戲應結束且玩家失敗

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
