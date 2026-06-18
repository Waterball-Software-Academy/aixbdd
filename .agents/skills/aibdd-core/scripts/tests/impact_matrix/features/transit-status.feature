Feature: transit-status

  transit-status with --spec sets that spec's status; making a spec inconsistent
  auto-degrades a resolved impact to pending, but making specs consistent never
  auto-resolves. Without --spec it sets the impact's status directly, and resolve
  requires every spec consistent. The invariant (resolved iff all consistent) holds.

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

  Rule: marking a spec consistent updates only that spec and never resolves the impact
    Example: marking one spec consistent keeps the impact pending
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/create-room.feature" status "consistent"
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

    Example: marking every spec consistent still leaves the impact pending
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/create-room.feature" status "consistent"
      And impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/activities/create-room.activity" status "consistent"
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
            status: consistent
        """

  Rule: an impact becomes resolved only by an explicit impact-status command
    Example: resolve an impact whose specs are all consistent
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
                status: consistent
        """
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" status "resolved"
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
        """

  Rule: reopening an impact is an explicit impact-status command
    Example: set a resolved impact back to pending
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
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" status "pending"
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
        """

  Rule: an impact cannot be resolved while any spec is inconsistent
    Example: resolving with an inconsistent spec is rejected and changes nothing
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" status "resolved"
      Then the violations should equal:
        """
        [
          {
            "location": "impacts[0].status",
            "type": "INCONSISTENT",
            "message": "impact `00000000-0000-4000-8000-000000000001` is resolved but spec `packages/01-room/features/create-room.feature` is inconsistent"
          }
        ]
        """
      And the matrix file is unchanged

  Rule: marking a spec inconsistent auto-degrades a resolved impact to pending
    Example: introducing inconsistency re-opens the impact without an explicit command
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
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/create-room.feature" status "inconsistent"
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

  Rule: setting a spec to the status it already holds changes nothing
    Example: transit inconsistent on an already-inconsistent spec is idempotent
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/create-room.feature" status "inconsistent"
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

  Rule: transit-status rejects a status that does not match the grain
    Example: a spec cannot take an impact status
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/create-room.feature" status "resolved"
      Then the violations should equal:
        """
        [
          { "location": "args.status", "type": "INVALID_VALUE", "message": "status 'resolved' is invalid for a spec; must be one of: inconsistent, consistent" }
        ]
        """
      And the matrix file is unchanged

    Example: an impact cannot take a spec status
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" status "consistent"
      Then the violations should equal:
        """
        [
          { "location": "args.status", "type": "INVALID_VALUE", "message": "status 'consistent' is invalid for an impact; must be one of: pending, resolved" }
        ]
        """
      And the matrix file is unchanged

  Rule: transit-status rejects a spec that is not in the impact and changes nothing
    Example: an unknown spec path under a known id is rejected
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000001" spec "packages/01-room/features/leave-room.feature" status "consistent"
      Then the violations should equal:
        """
        [
          {
            "location": "args.spec",
            "type": "NOT_FOUND",
            "message": "spec `packages/01-room/features/leave-room.feature` not found in impact `00000000-0000-4000-8000-000000000001`"
          }
        ]
        """
      And the matrix file is unchanged

  Rule: transit-status rejects an unknown impact id and changes nothing
    Example: the target id is not in the matrix
      When impact transit-status runs with id "00000000-0000-4000-8000-000000000999" status "resolved"
      Then the violations should equal:
        """
        [
          { "location": "args.id", "type": "NOT_FOUND", "message": "impact `00000000-0000-4000-8000-000000000999` not found" }
        ]
        """
      And the matrix file is unchanged
