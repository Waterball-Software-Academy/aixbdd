Feature: apply form-lock Example skeleton insertion

  Background:
    Given a form-lock profile at "fixtures/web-service/sbe-form-lock/form-lock.profile.yml" with content:
      """
      boundary_type: web-service
      rule_prefix_to_template:
        - rule_prefix: "前置（狀態"
          template: precondition-state.tmpl
        - rule_prefix: "前置（參數"
          template: precondition-param.tmpl
        - rule_prefix: "後置（回應"
          template: postcondition-response.tmpl
        - rule_prefix: "後置（狀態"
          template: postcondition-state.tmpl
      """
    And canonical web-service templates are copied beside the profile

  Rule: 後置（狀態） - 含 description 與既有 comment 的 Rule 應把 Example 插在 description 之後
    Example: description bullet 在 Example 之前
      Given a temporary file at "game.feature" with content:
        """
        Feature: 房主開始遊戲

            Rule: 前置（狀態） - 觸發者必須為房主（P1）
                - 產生魔王為系統自動副作用
                # 這條舊註解應由 skeleton 取代
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 房主開始遊戲

            Rule: 前置（狀態） - 觸發者必須為房主（P1）
                - 產生魔王為系統自動副作用

                Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-state.md 補 `前置（狀態）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體錯誤訊息>"
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md 理解失敗情境下 Then 怎麼推理，再用其中 `前置（狀態）` 小節判斷這裡該怎麼驗證操作失敗後系統狀態沒有變動。
                  And <dsl>
        """

    Example: 多行 description 與 comment 的最後一行之後插入 Example
      Given a temporary file at "state-change.feature" with content:
        """
        Feature: 開始遊戲

            Rule: 後置（狀態） - 遊戲狀態切為進行中
                倒數必須已經完成
                - 房主按下開始按鈕
                # 舊的人工提示會被 skeleton 取代
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 開始遊戲

            Rule: 後置（狀態） - 遊戲狀態切為進行中
                倒數必須已經完成
                - 房主按下開始按鈕

                Example: <操作> 後 <狀態主詞> 變為 <新狀態>
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-postcondition-state.md 補 `後置（狀態）` 所需建構出的可量測初始狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作成功
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-success-law.md 理解成功情境下 Then 怎麼推理，再用其中 `後置（狀態）` 小節判斷這裡該怎麼驗證操作成功後系統狀態已經改成預期結果。
                  And <dsl>
        """

  Rule: 後置（狀態） - 無 description 的 Rule 仍應插入 Example
    Example: Rule 下直接插入 skeleton
      Given a temporary file at "simple.feature" with content:
        """
        Feature: 玩家準備

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 玩家準備

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）

                Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-state.md 補 `前置（狀態）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體錯誤訊息>"
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md 理解失敗情境下 Then 怎麼推理，再用其中 `前置（狀態）` 小節判斷這裡該怎麼驗證操作失敗後系統狀態沒有變動。
                  And <dsl>
        """

    Example: 不同 prefix template 且緊鄰檔尾時仍插入 skeleton
      Given a temporary file at "response.feature" with content:
        """
        Feature: 建立遊戲房

            Rule: 後置（回應） - 回傳房間代碼
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 建立遊戲房

            Rule: 後置（回應） - 回傳房間代碼

                Example: <操作> 後 <回應主詞> 為 <期望值>
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-postcondition-response.md 補 `後置（回應）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作成功
                  # @dsl
                  # handler-candidate-kinds: response-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-success-law.md 理解成功情境下 Then 怎麼推理，再用其中 `後置（回應）` 小節判斷這裡該怎麼驗證操作成功後回應內容符合預期。
                  And <dsl>
        """

  Rule: 後置（狀態） - 已 form-locked 的 Rule 重跑不應重複插入
    Background:
      Given a temporary file at "locked.feature" with content:
        """
        Feature: 已鎖定

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）
        """

    Example: 第二次 apply 不變更
      Given form-lock apply is run on the last feature file
      When form-lock apply is run again on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 已鎖定

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）

                Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-state.md 補 `前置（狀態）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體錯誤訊息>"
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md 理解失敗情境下 Then 怎麼推理，再用其中 `前置（狀態）` 小節判斷這裡該怎麼驗證操作失敗後系統狀態沒有變動。
                  And <dsl>
        """

    Example: 預先已含完整 skeleton 的 Rule 第一次 apply 也不變更
      And a temporary file at "prelocked.feature" with content:
        """
        Feature: 已預先鎖定

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）

                Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-state.md 補 `前置（狀態）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體錯誤訊息>"
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md 理解失敗情境下 Then 怎麼推理，再用其中 `前置（狀態）` 小節判斷這裡該怎麼驗證操作失敗後系統狀態沒有變動。
                  And <dsl>
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 已預先鎖定

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）

                Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-state.md 補 `前置（狀態）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體錯誤訊息>"
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md 理解失敗情境下 Then 怎麼推理，再用其中 `前置（狀態）` 小節判斷這裡該怎麼驗證操作失敗後系統狀態沒有變動。
                  And <dsl>
        """

  Rule: 後置（回應） - 未知 prefix 不 fallback 且記錄問題
    Example: 非合法 prefix 不插入 Example
      Given a temporary file at "unknown.feature" with content:
        """
        Feature: 未知

            Rule: 非法前綴 - 不應匹配
        """
      When form-lock apply is run on the last feature file
      Then unknown prefix questions should equal:
        """
        - where: unknown.feature:3
          type: 非法前綴
          text: unknown rule type prefix `非法前綴`; must match form-lock.profile.yml rule_prefix_to_template
        """
      And the last feature file content should equal:
        """
        Feature: 未知

            Rule: 非法前綴 - 不應匹配
        """

    Example: 含 description 與 comment 的未知 prefix 仍不插入且保留原文
      Given a temporary file at "unknown-with-description.feature" with content:
        """
        Feature: 未知

            Rule: 未定義分類 - 仍不應匹配
                - 這段 description 必須保留
                # 這段 comment 也不能被誤刪
        """
      When form-lock apply is run on the last feature file
      Then unknown prefix questions should equal:
        """
        - where: unknown-with-description.feature:3
          type: 未定義分類
          text: unknown rule type prefix `未定義分類`; must match form-lock.profile.yml rule_prefix_to_template
        """
      And the last feature file content should equal:
        """
        Feature: 未知

            Rule: 未定義分類 - 仍不應匹配
                - 這段 description 必須保留
                # 這段 comment 也不能被誤刪
        """

  Rule: 後置（狀態） - Rule 底下既有 comment 在首次 form-lock 時應由 Example skeleton 取代
    Example: 任意 comment 都會被 replace
      Given a temporary file at "flex.feature" with content:
        """
        Feature: 彈性占位

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）
                # 這裡原本留了一段人工提示
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 彈性占位

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）

                Example: <主詞> 不滿足 <條件> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-state.md 補 `前置（狀態）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體錯誤訊息>"
                  # @dsl
                  # handler-candidate-kinds: state-verifier
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-then-failure-law.md 理解失敗情境下 Then 怎麼推理，再用其中 `前置（狀態）` 小節判斷這裡該怎麼驗證操作失敗後系統狀態沒有變動。
                  And <dsl>
        """

    Example: 連續多行 comment 會整段被 replace
      Given a temporary file at "param-comment.feature" with content:
        """
        Feature: 參數占位

            Rule: 前置（參數） - 房間名稱不可為空字串
                # 第一段人工提示
                # 第二段人工提示
        """
      When form-lock apply is run on the last feature file
      Then the last feature file content should equal:
        """
        Feature: 參數占位

            Rule: 前置（參數） - 房間名稱不可為空字串

                Scenario Outline: <參數名> = <無效值> 時 <操作> 失敗
                  # @dsl
                  # handler-candidate-kinds: state-builder | operation-invoke | time-control | external-stub
                  # rule: 先讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/shared-given-law.md 理解 shared arrangement 作為你的推理流程，再讀 ${SKILL_HOME}/aibdd-core/assets/boundaries/web-service/dsl-arrangement-rules/given-delta-precondition-param.md 補 `前置（參數）` 所需建構出的系統合法狀態。
                  Given <dsl>
                  When <dsl>
                  Then 操作失敗，錯誤為 "<具體驗證錯誤訊息>"

                  Examples:
                    | 參數名   | 無效值   | 操作   | 具體驗證錯誤訊息   |
                    | <參數名> | <無效值> | <操作> | <具體驗證錯誤訊息> |
        """

  Rule: 後置（回應） - apply_form_lock CLI 回傳 JSON report
    Example: unknown prefix 出現在 stdout JSON 而不會寫到檔案系統做任何 plan report
      Given a temporary file at "unknown-cli.feature" with content:
        """
        Feature: 未知

            Rule: 非法前綴 - 不應匹配
        """
      When apply_form_lock CLI is run on the last feature file
      Then CLI exit code is 0
      And CLI apply JSON report should equal:
        """
        {
          "changed_count": 0,
          "feature_count": 1,
          "changed_features": [],
          "questions": [
            {
              "where": "unknown-cli.feature:3",
              "type": "非法前綴",
              "text": "unknown rule type prefix `非法前綴`; must match form-lock.profile.yml rule_prefix_to_template"
            }
          ],
          "report": {
            "summary": "changed=0 features=1 questions=1"
          }
        }
        """
      And no file exists at "reports/bdd-analyze-cic.md"

    Example: 成功 apply 時 JSON report 含 changed_count
      Given a temporary file at "cli-simple.feature" with content:
        """
        Feature: 玩家準備

            Rule: 前置（狀態） - 觸發者必須為房客（非房主）
        """
      When apply_form_lock CLI is run on the last feature file
      Then CLI exit code is 0
      And CLI apply JSON report should equal:
        """
        {
          "changed_count": 1,
          "feature_count": 1,
          "changed_features": ["cli-simple.feature"],
          "questions": [],
          "report": {
            "summary": "changed=1 features=1 questions=0"
          }
        }
        """
