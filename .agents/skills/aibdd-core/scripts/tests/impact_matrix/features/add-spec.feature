Feature: add a spec to an existing impact

  add-spec attaches one new spec to an impact addressed by id, without
  rewriting the impact. The caller provides the new spec's status: an
  inconsistent spec auto-degrades the impact to pending, while a consistent
  spec leaves the impact's status unchanged.

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
      """

  Rule: add-spec appends a new spec with the given status
    Example: append an inconsistent spec
      When impact add-spec runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/activities/create-room.activity" status "inconsistent"
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

  Rule: adding an inconsistent spec auto-degrades a resolved impact to pending
    Example: the new inconsistent spec re-opens a resolved impact
      Given a matrix file with content:
        """
        version: 2
        impacts:
          - id: 00000000-0000-4000-8000-000000000001
            owner: aibdd-flows-specify
            quotes:
              - 建立房間時必須設定密碼
            rationale: 建房流程
            status: resolved
            specs:
              - path: packages/01-room/features/create-room.feature
                status: consistent
        """
      When impact add-spec runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/activities/create-room.activity" status "inconsistent"
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
            status: consistent
          - path: packages/01-room/activities/create-room.activity
            status: inconsistent
        """

  Rule: adding a consistent spec to a resolved impact keeps it resolved
    Example: the new consistent spec does not re-open the impact
      Given a matrix file with content:
        """
        version: 2
        impacts:
          - id: 00000000-0000-4000-8000-000000000001
            owner: aibdd-flows-specify
            quotes:
              - 建立房間時必須設定密碼
            rationale: 建房流程
            status: resolved
            specs:
              - path: packages/01-room/features/create-room.feature
                status: consistent
        """
      When impact add-spec runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/activities/create-room.activity" status "consistent"
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 建立房間時必須設定密碼
          rationale: 建房流程
          status: resolved
          specs:
          - path: packages/01-room/features/create-room.feature
            status: consistent
          - path: packages/01-room/activities/create-room.activity
            status: consistent
        """

  Rule: add-spec rejects a spec path already present in the impact and changes nothing
    Example: adding a duplicate spec path
      When impact add-spec runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/create-room.feature" status "inconsistent"
      Then the violations should equal:
        """
        [
          {
            "location": "impacts[0].specs[1].path",
            "type": "DUPLICATE",
            "message": "duplicate spec path `packages/01-room/features/create-room.feature` within impact"
          }
        ]
        """
      And the matrix file is unchanged

  Rule: add-spec rejects an unknown impact id and changes nothing
    Example: the target id is not in the matrix
      When impact add-spec runs with id "00000000-0000-4000-8000-000000000999" spec "packages/01-room/activities/create-room.activity" status "inconsistent"
      Then the violations should equal:
        """
        [
          { "location": "args.id", "type": "NOT_FOUND", "message": "impact `00000000-0000-4000-8000-000000000999` not found" }
        ]
        """
      And the matrix file is unchanged
