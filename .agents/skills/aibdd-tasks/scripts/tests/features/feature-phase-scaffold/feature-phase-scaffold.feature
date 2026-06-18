Feature: build and check feature phase scaffold from matrix-derived scope

  Rule: ordered feature paths drive scaffold across multiple packages
    Example: scaffold preserves semantic order without plan impacted section
      Given a temporary tasks project at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        SPECS_ROOT_DIR: specs
        TRUTH_BOUNDARY_ROOT: specs
        BOUNDARY_MAP_FILE: specs/boundary-map.yml
        CURRENT_PLAN_PACKAGE: specs/plans/<<NNN-plan-slug>>
        PLAN_MD: ${CURRENT_PLAN_PACKAGE}/plan.md
        PLAN_REPORTS_DIR: ${CURRENT_PLAN_PACKAGE}/reports
        IMPACT_MATRIX_YML: ${PLAN_REPORTS_DIR}/impact-matrix.yml
        PLAN_IMPLEMENTATION_DIR: ${CURRENT_PLAN_PACKAGE}/implementation
        """
      And a file at "specs/plans/demo-plan/plan.md" with content:
        """
        # Demo Plan

        Derived human summary only.
        """
      And a file at "specs/plans/demo-plan/reports/impact-matrix.yml" with content:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000001
          owner: aibdd-flows-specify
          quotes:
          - scope
          rationale: scope
          status: pending
          specs:
          - path: packages/01-room/features/open-room.feature
            status: inconsistent
          - path: packages/02-game/features/set-secret.feature
            status: inconsistent
          - path: packages/02-game/features/guess-number.feature
            status: inconsistent
        """
      And a file at "specs/packages/01-room/features/open-room.feature" with content:
        """
        Feature: 開房或加入
        """
      And a file at "specs/packages/02-game/features/set-secret.feature" with content:
        """
        Feature: 設置密碼
        """
      And a file at "specs/packages/02-game/features/guess-number.feature" with content:
        """
        Feature: 猜測魔王數字
        """
      When build_feature_phase_scaffold is run with plan package "specs/plans/demo-plan" and feature paths:
        """
        ["packages/01-room/features/open-room.feature","packages/02-game/features/set-secret.feature","packages/02-game/features/guess-number.feature"]
        """
      Then CLI exit code is 0
      And JSON ok is true
      And JSON feature_phases paths should equal:
        """
        [
          "packages/01-room/features/open-room.feature",
          "packages/02-game/features/set-secret.feature",
          "packages/02-game/features/guess-number.feature"
        ]
        """
      And CLI stdout JSON field integration_phase.phase_number equals 5

  Rule: scaffold checker validates ordered membership from matrix scope
    Example: checker passes for consistent scaffold
      Given a temporary tasks project at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        SPECS_ROOT_DIR: specs
        TRUTH_BOUNDARY_ROOT: specs
        BOUNDARY_MAP_FILE: specs/boundary-map.yml
        CURRENT_PLAN_PACKAGE: specs/plans/<<NNN-plan-slug>>
        PLAN_MD: ${CURRENT_PLAN_PACKAGE}/plan.md
        PLAN_REPORTS_DIR: ${CURRENT_PLAN_PACKAGE}/reports
        IMPACT_MATRIX_YML: ${PLAN_REPORTS_DIR}/impact-matrix.yml
        PLAN_IMPLEMENTATION_DIR: ${CURRENT_PLAN_PACKAGE}/implementation
        """
      And a file at "specs/plans/demo-plan/plan.md" with content:
        """
        # Demo Plan
        """
      And a file at "specs/plans/demo-plan/reports/impact-matrix.yml" with content:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000002
          owner: aibdd-flows-specify
          quotes:
          - scope
          rationale: scope
          status: pending
          specs:
          - path: packages/01-room/features/open-room.feature
            status: inconsistent
          - path: packages/02-game/features/guess-number.feature
            status: inconsistent
        """
      And a file at "specs/packages/01-room/features/open-room.feature" with content:
        """
        Feature: 開房或加入
        """
      And a file at "specs/packages/02-game/features/guess-number.feature" with content:
        """
        Feature: 猜測魔王數字
        """
      Given build_feature_phase_scaffold is run with plan package "specs/plans/demo-plan" and feature paths:
        """
        ["packages/01-room/features/open-room.feature","packages/02-game/features/guess-number.feature"]
        """
      When check_feature_phase_scaffold is run
      Then CLI exit code is 0
      And checker summary is feature phase scaffold check
      And JSON ok is true

  Rule: tasks.md checker works without plan impacted section
    Example: tasks.md structure matches matrix-derived ordered scope
      Given a temporary tasks project at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        SPECS_ROOT_DIR: specs
        TRUTH_BOUNDARY_ROOT: specs
        BOUNDARY_MAP_FILE: specs/boundary-map.yml
        CURRENT_PLAN_PACKAGE: specs/plans/<<NNN-plan-slug>>
        PLAN_MD: ${CURRENT_PLAN_PACKAGE}/plan.md
        PLAN_REPORTS_DIR: ${CURRENT_PLAN_PACKAGE}/reports
        IMPACT_MATRIX_YML: ${PLAN_REPORTS_DIR}/impact-matrix.yml
        PLAN_IMPLEMENTATION_DIR: ${CURRENT_PLAN_PACKAGE}/implementation
        """
      And a file at "specs/plans/demo-plan/plan.md" with content:
        """
        # Demo Plan
        """
      And a file at "specs/plans/demo-plan/reports/impact-matrix.yml" with content:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000003
          owner: aibdd-flows-specify
          quotes:
          - scope
          rationale: scope
          status: pending
          specs:
          - path: packages/01-room/features/open-room.feature
            status: inconsistent
          - path: packages/02-game/features/guess-number.feature
            status: inconsistent
        """
      And a file at "specs/packages/01-room/features/open-room.feature" with content:
        """
        Feature: 開房或加入
        """
      And a file at "specs/packages/02-game/features/guess-number.feature" with content:
        """
        Feature: 猜測魔王數字
        """
      And a file at "specs/plans/demo-plan/tasks.md" with content:
        """
        # Phase 1 - Infra setup

        ## Tasks

        - prepare infra

        # Phase 2 - 開房或加入

        ## RED

        - red

        ## GREEN

        - green

        ## Refactor

        - refactor

        # Phase 3 - 猜測魔王數字

        ## RED

        - red

        ## GREEN

        - green

        ## Refactor

        - refactor

        # Phase 4 - Integration

        ## Tasks

        - integrate
        """
      When check_tasks_md is run with plan package "specs/plans/demo-plan" and feature paths:
        """
        ["packages/01-room/features/open-room.feature","packages/02-game/features/guess-number.feature"]
        """
      Then CLI exit code is 0
      And checker summary is tasks.md structure check
      And JSON ok is true
