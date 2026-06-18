Feature: remove

  Background:
    Given an impact matrix at the default test path
    And a matrix file with content:
      """
      version: 2
      impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
            - 建立房間時必須設定密碼
          rationale: 建房流程
          status: pending
          specs:
            - path: packages/01-room/features/create-room.feature
              status: inconsistent
            - path: packages/01-room/activities/create-room.activity
              status: inconsistent
      """

  Rule: removing a spec drops it from the impact
    Example: remove one spec of two
      When impact remove runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/activities/create-room.activity"
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 建立房間時必須設定密碼
          rationale: 建房流程
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
        """

  Rule: removing the last spec leaves the impact in place with no specs
    Example: a single-spec impact survives spec removal with an empty specs list
      Given a matrix file with content:
        """
        version: 2
        impacts:
          - id: 00000000-0000-4000-8000-000000000009
            owner: aibdd-flows-specify
            quotes:
              - 移除訪客試玩
            rationale: 淘汰訪客流程
            status: pending
            specs:
              - path: packages/01-room/features/guest-trial.feature
                status: inconsistent
        """
      When impact remove runs with id "00000000-0000-4000-8000-000000000009" spec "packages/01-room/features/guest-trial.feature"
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000009
          owner: aibdd-flows-specify
          quotes:
          - 移除訪客試玩
          rationale: 淘汰訪客流程
          status: pending
          specs: []
        """

  Rule: remove without a spec deletes the whole impact at once
    Example: removing by id alone clears all its specs
      When impact remove runs for whole impact "00000000-0000-4000-8000-000000000001"
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts: []
        """

  Rule: removing a spec that is already absent changes nothing
    Example: remove is idempotent for an absent spec
      When impact remove runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/leave-room.feature"
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 建立房間時必須設定密碼
          rationale: 建房流程
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
          - path: packages/01-room/activities/create-room.activity
            status: inconsistent
        """
