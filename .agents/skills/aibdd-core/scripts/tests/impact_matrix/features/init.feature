Feature: init

  Background:
    Given an impact matrix at the default test path

  Rule: init creates an empty v2 matrix
    Example: init creates the file and returns an ok envelope
      When the CLI runs init
      Then the CLI exit code is 0
      And the CLI report should equal:
        """
        { "ok": true, "violations": [], "impacts": [] }
        """
      And the impact matrix YAML equals:
        """
        version: 2
        impacts: []
        """

  Rule: init refuses to overwrite an existing matrix
    Example: init on a non-empty matrix is rejected and changes nothing
      Given a matrix file with content:
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
      When impact init runs
      Then the violations should equal:
        """
        [
          { "location": "args.matrix", "type": "ALREADY_EXISTS", "message": "impact matrix already exists; init refuses to overwrite" }
        ]
        """
      And the matrix file is unchanged
