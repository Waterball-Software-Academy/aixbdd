Feature: resolve tasks paths from impact matrix and aibdd-core resolver

  Rule: unresolved plan package slot fails with explicit message
    Example: CURRENT_PLAN_PACKAGE still contains slot placeholder
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
        """
      When resolve_tasks_paths is run
      Then CLI exit code is 1
      And JSON reason contains CURRENT_PLAN_PACKAGE unresolved

  Rule: plan package override resolves multi-package matrix feature paths
    Example: two function packages contribute add features
      Given a temporary tasks project at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        SPECS_ROOT_DIR: specs
        TRUTH_BOUNDARY_ROOT: specs
        TRUTH_BOUNDARY_PACKAGES_DIR: specs/packages
        BOUNDARY_MAP_FILE: specs/boundary-map.yml
        CURRENT_PLAN_PACKAGE: specs/plans/<<NNN-plan-slug>>
        PLAN_MD: ${CURRENT_PLAN_PACKAGE}/plan.md
        PLAN_REPORTS_DIR: ${CURRENT_PLAN_PACKAGE}/reports
        IMPACT_MATRIX_YML: ${PLAN_REPORTS_DIR}/impact-matrix.yml
        PLAN_IMPLEMENTATION_DIR: ${CURRENT_PLAN_PACKAGE}/implementation
        PLAN_INTERNAL_STRUCTURE: ${PLAN_IMPLEMENTATION_DIR}/internal-structure.class.mmd
        """
      And a file at "specs/plans/demo-plan/plan.md" with content:
        """
        # Demo Plan

        No impacted section here on purpose.
        """
      And a file at "specs/plans/demo-plan/reports/impact-matrix.yml" with content:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000004
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
          - path: contracts/room.api.yml
            status: inconsistent
        """
      When resolve_tasks_paths is run with plan package "specs/plans/demo-plan"
      Then CLI exit code is 0
      And JSON ok is true
      And JSON matrix_feature_paths should equal:
        """
        [
          "packages/01-room/features/open-room.feature",
          "packages/02-game/features/guess-number.feature"
        ]
        """

  Rule: empty feature scope fails fast at scaffold time
    Example: matrix has no add or update feature entries
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
      And a file at "specs/plans/empty-scope/plan.md" with content:
        """
        # Empty Scope Plan
        """
      And a file at "specs/plans/empty-scope/reports/impact-matrix.yml" with content:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000005
          owner: aibdd-flows-specify
          quotes:
          - scope
          rationale: scope
          status: pending
          specs:
          - path: contracts/common.yml
            status: inconsistent
        """
      When build_feature_phase_scaffold is run with plan package "specs/plans/empty-scope"
      Then CLI exit code is 1
      And JSON reason contains impact matrix has no add/update .feature entries

  Rule: resolve_tasks_paths output is idempotent for the same project fixture
    Example: repeated invocation returns identical matrix_feature_paths
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
        """
      And a file at "specs/plans/demo-plan/reports/impact-matrix.yml" with content:
        """
        version: 2
        impacts:
        - id: 00000000-0000-4000-8000-000000000006
          owner: aibdd-flows-specify
          quotes:
          - scope
          rationale: scope
          status: pending
          specs:
          - path: packages/01-room/features/open-room.feature
            status: inconsistent
        """
      When resolve_tasks_paths is run with plan package "specs/plans/demo-plan"
      Then JSON matrix_feature_paths should equal:
        """
        [
          "packages/01-room/features/open-room.feature"
        ]
        """
      When resolve_tasks_paths is run with plan package "specs/plans/demo-plan"
      Then JSON matrix_feature_paths should equal:
        """
        [
          "packages/01-room/features/open-room.feature"
        ]
        """
