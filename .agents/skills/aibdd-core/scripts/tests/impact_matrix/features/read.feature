Feature: read

  Background:
    Given an impact matrix at the default test path
    And a matrix file with content:
      """
      version: 2
      impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
            - 玩家可以建立遊戲房
          rationale: 建房流程
          status: pending
          specs:
            - path: packages/01-room/features/create-room.feature
              status: inconsistent
            - path: packages/01-room/activities/create-room.activity
              status: consistent
        - id: 00000000-0000-4000-8000-000000000002
          owner: aibdd-api-plan
          quotes:
            - 後端回傳房內玩家清單
          rationale: 加入房 API
          status: resolved
          specs:
            - path: contracts/join-room.api.yml
              status: consistent
      """

  Rule: read with no filters returns every impact unchanged
    Example: list all
      When impact read runs
      Then the read result should equal:
        """
        [
          {
            "id": "00000000-0000-4000-8000-000000000001",
            "owner": "aibdd-flows-specify",
            "quotes": ["玩家可以建立遊戲房"],
            "rationale": "建房流程",
            "status": "pending",
            "specs": [
              { "path": "packages/01-room/features/create-room.feature", "status": "inconsistent" },
              { "path": "packages/01-room/activities/create-room.activity", "status": "consistent" }
            ]
          },
          {
            "id": "00000000-0000-4000-8000-000000000002",
            "owner": "aibdd-api-plan",
            "quotes": ["後端回傳房內玩家清單"],
            "rationale": "加入房 API",
            "status": "resolved",
            "specs": [
              { "path": "contracts/join-room.api.yml", "status": "consistent" }
            ]
          }
        ]
        """

  Rule: an impact-grain filter drops whole non-matching impacts
    Example: only pending impacts
      When impact read runs with query:
        """
        { "impact_status": "pending" }
        """
      Then the read result should equal:
        """
        [
          {
            "id": "00000000-0000-4000-8000-000000000001",
            "owner": "aibdd-flows-specify",
            "quotes": ["玩家可以建立遊戲房"],
            "rationale": "建房流程",
            "status": "pending",
            "specs": [
              { "path": "packages/01-room/features/create-room.feature", "status": "inconsistent" },
              { "path": "packages/01-room/activities/create-room.activity", "status": "consistent" }
            ]
          }
        ]
        """

    Example: filter by owner
      When impact read runs with query:
        """
        { "owners": ["aibdd-api-plan"] }
        """
      Then the read result should equal:
        """
        [
          {
            "id": "00000000-0000-4000-8000-000000000002",
            "owner": "aibdd-api-plan",
            "quotes": ["後端回傳房內玩家清單"],
            "rationale": "加入房 API",
            "status": "resolved",
            "specs": [
              { "path": "contracts/join-room.api.yml", "status": "consistent" }
            ]
          }
        ]
        """

  Rule: a spec-grain filter keeps only matching specs and drops emptied impacts
    Example: only inconsistent specs (the drain worklist)
      When impact read runs with query:
        """
        { "spec_status": "inconsistent" }
        """
      Then the read result should equal:
        """
        [
          {
            "id": "00000000-0000-4000-8000-000000000001",
            "owner": "aibdd-flows-specify",
            "quotes": ["玩家可以建立遊戲房"],
            "rationale": "建房流程",
            "status": "pending",
            "specs": [
              { "path": "packages/01-room/features/create-room.feature", "status": "inconsistent" }
            ]
          }
        ]
        """

    Example: spec-path regex selects .feature specs only
      When impact read runs with query:
        """
        { "spec_path": "\\.feature$" }
        """
      Then the read result should equal:
        """
        [
          {
            "id": "00000000-0000-4000-8000-000000000001",
            "owner": "aibdd-flows-specify",
            "quotes": ["玩家可以建立遊戲房"],
            "rationale": "建房流程",
            "status": "pending",
            "specs": [
              { "path": "packages/01-room/features/create-room.feature", "status": "inconsistent" }
            ]
          }
        ]
        """

  Rule: a filter that matches nothing returns an empty list
    Example: no impact is owned by rules-specify
      When impact read runs with query:
        """
        { "owners": ["aibdd-rules-specify"] }
        """
      Then the read result should equal:
        """
        []
        """

  Rule: filters compose with AND semantics
    Example: pending impacts whose specs are still inconsistent, owned by flows-specify
      When impact read runs with query:
        """
        { "owners": ["aibdd-flows-specify"], "spec_status": "inconsistent" }
        """
      Then the read result should equal:
        """
        [
          {
            "id": "00000000-0000-4000-8000-000000000001",
            "owner": "aibdd-flows-specify",
            "quotes": ["玩家可以建立遊戲房"],
            "rationale": "建房流程",
            "status": "pending",
            "specs": [
              { "path": "packages/01-room/features/create-room.feature", "status": "inconsistent" }
            ]
          }
        ]
        """
