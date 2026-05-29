Feature: resolve project arguments from CWD-relative manifest

  Rule: missing manifest fails with explicit stderr
    Example: arguments.yml absent at project CWD
      Given a temporary project directory at the default test path
      When resolve_args CLI is run with stdin:
        """
        IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
        """
      Then CLI exit code is 1
      And CLI stderr should equal:
        """
        [resolve-args] arguments.yml not found at {ARGS_PATH}
        """
      And CLI stdout should be empty

  Rule: flat placeholder resolves to arguments value
    Example: single key substitution
      Given a temporary project directory at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        IMPACT_MATRIX_YML: specs/plans/demo/reports/impact-matrix.yml
        """
      When resolve_args CLI is run with stdin:
        """
        IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
        """
      Then CLI exit code is 0
      And CLI stdout should equal:
        """
        IMPACT_MATRIX_YML=specs/plans/demo/reports/impact-matrix.yml
        """

  Rule: nested placeholders expand recursively
    Example: chained PLAN_REPORTS_DIR and IMPACT_MATRIX_YML
      Given a temporary project directory at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        PLAN_REPORTS_DIR: specs/plans/demo/reports
        IMPACT_MATRIX_YML: ${PLAN_REPORTS_DIR}/impact-matrix.yml
        """
      When resolve_args CLI is run with stdin:
        """
        IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
        """
      Then CLI exit code is 0
      And CLI stdout should equal:
        """
        IMPACT_MATRIX_YML=specs/plans/demo/reports/impact-matrix.yml
        """

  Rule: unresolvable placeholder fails with missing key list
    Example: unknown key leaves stdout empty
      Given a temporary project directory at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        SPECS_ROOT_DIR: specs
        """
      When resolve_args CLI is run with stdin:
        """
        foo=${MISSING_KEY}
        """
      Then CLI exit code is 2
      And CLI stdout should be empty
      And CLI stderr should equal:
        """
        [resolve-args] missing keys in .aibdd/arguments.yml:
          - MISSING_KEY
        """

  Rule: cyclic placeholders fail with convergence error
    Example: mutually recursive argument values
      Given a temporary project directory at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        KEY_A: ${KEY_B}
        KEY_B: ${KEY_A}
        """
      When resolve_args CLI is run with stdin:
        """
        value=${KEY_A}
        """
      Then CLI exit code is 3
      And CLI stdout should be empty
      And CLI stderr should equal:
        """
        [resolve-args] placeholder resolution did not converge within 50 passes — likely a cyclic reference in .aibdd/arguments.yml
        """

  Rule: manifest is read from subprocess CWD not script location
    Example: different project directories resolve different values
      Given project directory "project-a" at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        IMPACT_MATRIX_YML: specs/plans/a/reports/impact-matrix.yml
        """
      When resolve_args CLI is run with stdin:
        """
        IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
        """
      Then CLI exit code is 0
      And CLI stdout should equal:
        """
        IMPACT_MATRIX_YML=specs/plans/a/reports/impact-matrix.yml
        """
      Given project directory "project-b" at the default test path
      And an arguments file at ".aibdd/arguments.yml" with content:
        """
        IMPACT_MATRIX_YML: specs/plans/b/reports/impact-matrix.yml
        """
      When resolve_args CLI is run with stdin:
        """
        IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
        """
      Then CLI exit code is 0
      And CLI stdout should equal:
        """
        IMPACT_MATRIX_YML=specs/plans/b/reports/impact-matrix.yml
        """
