Feature: write

  Background:
    Given an impact matrix at the default test path
    And a matrix file with content:
      """
      version: 2
      impacts: []
      """

  Rule: write creates one impact with an auto-generated id
    Example: a new impact persists to the file and returns in the envelope
      Given the impact id sequence is "00000000-0000-4000-8000-000000000001"
      When the CLI runs with payload:
        """
        {
          "argv": [
            "write",
            "--owner", "aibdd-flows-specify",
            "--rationale", "建立房間流程新增密碼設定步驟與密碼驗證情境",
            "--quote", "建立房間時必須設定密碼，未設定不可建立",
            "--spec", "packages/01-room/features/create-room.feature"
          ]
        }
        """
      Then the CLI exit code is 0
      And the CLI report should equal:
        """
        {
          "ok": true,
          "violations": [],
          "impacts": [
            {
              "id": "00000000-0000-4000-8000-000000000001",
              "owner": "aibdd-flows-specify",
              "quotes": ["建立房間時必須設定密碼，未設定不可建立"],
              "rationale": "建立房間流程新增密碼設定步驟與密碼驗證情境",
              "status": "pending",
              "specs": [
                { "path": "packages/01-room/features/create-room.feature", "status": "inconsistent" }
              ]
            }
          ]
        }
        """
      And the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 建立房間時必須設定密碼，未設定不可建立
          rationale: 建立房間流程新增密碼設定步驟與密碼驗證情境
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
        """

    Example: an impact may carry several quotes and several specs
      Given the impact id sequence is "00000000-0000-4000-8000-000000000001"
      When impact write runs with payload:
        """
        {
          "owner": "aibdd-flows-specify",
          "quotes": ["玩家可以建立遊戲房", "建立遊戲房必須設定密碼"],
          "rationale": "建房與密碼設定屬同一流程",
          "specs": [
            "packages/01-room/features/create-room.feature",
            "packages/01-room/activities/create-room.activity"
          ]
        }
        """
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 玩家可以建立遊戲房
          - 建立遊戲房必須設定密碼
          rationale: 建房與密碼設定屬同一流程
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
          - path: packages/01-room/activities/create-room.activity
            status: inconsistent
        """

  Rule: write without any spec creates a spec-less pending impact
    Example: omitting --spec yields an impact whose specs list is empty
      Given the impact id sequence is "00000000-0000-4000-8000-000000000001"
      When the CLI runs with payload:
        """
        {
          "argv": [
            "write",
            "--owner", "aibdd-api-plan",
            "--rationale", "本輪新增匯出房間設定的對外端點，spec 路徑待 api-plan 定檔",
            "--quote", "使用者可以匯出房間設定"
          ]
        }
        """
      Then the CLI exit code is 0
      And the CLI report should equal:
        """
        {
          "ok": true,
          "violations": [],
          "impacts": [
            {
              "id": "00000000-0000-4000-8000-000000000001",
              "owner": "aibdd-api-plan",
              "quotes": ["使用者可以匯出房間設定"],
              "rationale": "本輪新增匯出房間設定的對外端點，spec 路徑待 api-plan 定檔",
              "status": "pending",
              "specs": []
            }
          ]
        }
        """
      And the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-api-plan
          quotes:
          - 使用者可以匯出房間設定
          rationale: 本輪新增匯出房間設定的對外端點，spec 路徑待 api-plan 定檔
          status: pending
          specs: []
        """

  Rule: write with an explicit id replaces that impact instead of appending
    Example: replacing keeps the id and overwrites the fields
      Given the impact id sequence is "00000000-0000-4000-8000-000000000001"
      And impact write runs with payload:
        """
        {
          "owner": "aibdd-flows-specify",
          "quotes": ["玩家可以建立遊戲房"],
          "rationale": "初版建房流程",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      When impact write runs with payload:
        """
        {
          "id": "00000000-0000-4000-8000-000000000001",
          "owner": "aibdd-flows-specify",
          "quotes": ["玩家可以建立遊戲房", "建立遊戲房必須設定密碼"],
          "rationale": "建房流程補上密碼設定",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 玩家可以建立遊戲房
          - 建立遊戲房必須設定密碼
          rationale: 建房流程補上密碼設定
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
        """

  Rule: a second write appends a new impact, and the same spec may sit under a different owner
    Example: two owners touch the same .feature in distinct impacts
      Given the impact id sequence is "00000000-0000-4000-8000-000000000001, 00000000-0000-4000-8000-000000000002"
      And impact write runs with payload:
        """
        {
          "owner": "aibdd-flows-specify",
          "quotes": ["玩家可以建立遊戲房"],
          "rationale": "建房骨架",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      When impact write runs with payload:
        """
        {
          "owner": "aibdd-spec-by-example",
          "quotes": ["未設定密碼時不可建立遊戲房"],
          "rationale": "補上密碼必填的範例值",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 玩家可以建立遊戲房
          rationale: 建房骨架
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
        - id: 00000000-0000-4000-8000-000000000002
          owner: aibdd-spec-by-example
          quotes:
          - 未設定密碼時不可建立遊戲房
          rationale: 補上密碼必填的範例值
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
        """

  Rule: replacing an impact with an identical payload changes nothing
    Example: re-writing the same fields by id is idempotent
      Given the impact id sequence is "00000000-0000-4000-8000-000000000001"
      And impact write runs with payload:
        """
        {
          "owner": "aibdd-flows-specify",
          "quotes": ["玩家可以建立遊戲房"],
          "rationale": "建房骨架",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      When impact write runs with payload:
        """
        {
          "id": "00000000-0000-4000-8000-000000000001",
          "owner": "aibdd-flows-specify",
          "quotes": ["玩家可以建立遊戲房"],
          "rationale": "建房骨架",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      Then the impact matrix YAML equals:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - 玩家可以建立遊戲房
          rationale: 建房骨架
          status: pending
          specs:
          - path: packages/01-room/features/create-room.feature
            status: inconsistent
        """

  Rule: write rejects an unknown owner and writes nothing
    Example: owner outside the enum
      When impact write runs with payload:
        """
        {
          "owner": "aibdd-unknown",
          "quotes": ["x"],
          "rationale": "r",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      Then the violations should equal:
        """
        [
          {
            "location": "impacts[0].owner",
            "type": "INVALID_VALUE",
            "message": "owner 'aibdd-unknown' is invalid; must be one of: aibdd-flows-specify, aibdd-rules-specify, aibdd-spec-by-example, aibdd-plan, aibdd-api-plan, aibdd-data-plan"
          }
        ]
        """
      And the matrix file is unchanged

  Rule: write rejects empty quotes and writes nothing
    Example: no quotes
      When impact write runs with payload:
        """
        {
          "owner": "aibdd-flows-specify",
          "quotes": [],
          "rationale": "r",
          "specs": ["packages/01-room/features/create-room.feature"]
        }
        """
      Then the violations should equal:
        """
        [
          { "location": "impacts[0].quotes", "type": "MISSING", "message": "quotes must be a non-empty list of non-empty strings" }
        ]
        """
      And the matrix file is unchanged

  Rule: write rejects a duplicate spec path within one impact and writes nothing
    Example: the same spec path twice is rejected, exits 1, and writes nothing
      When the CLI runs with payload:
        """
        {
          "argv": [
            "write",
            "--owner", "aibdd-flows-specify",
            "--rationale", "r",
            "--quote", "x",
            "--spec", "packages/01-room/features/create-room.feature",
            "--spec", "packages/01-room/features/create-room.feature"
          ]
        }
        """
      Then the CLI exit code is 1
      And the CLI report should equal:
        """
        {
          "ok": false,
          "violations": [
            {
              "location": "impacts[0].specs[1].path",
              "type": "DUPLICATE",
              "message": "duplicate spec path `packages/01-room/features/create-room.feature` within impact"
            }
          ],
          "impacts": []
        }
        """
      And the matrix file is unchanged
