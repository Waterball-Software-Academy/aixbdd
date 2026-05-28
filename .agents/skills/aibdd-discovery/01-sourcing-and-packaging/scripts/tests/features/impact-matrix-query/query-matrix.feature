Feature: query discovery impact matrix entries

  Background:
    Given an impact matrix file at the default test path
    And impact matrix upsert is run with path "packages/01-member-login/features/01-member-login.feature" change_type "update" impact_summary "add last_login_at rule"
    And impact matrix upsert is run with path "packages/01-member-login/features/02-login-audit.feature" change_type "read_only_compare" impact_summary "reference existing audit rules"
    And impact matrix upsert is run with path "packages/01-member-login/dsl.yml" change_type "update" impact_summary "extend login vocabulary"

  Rule: query filters entries by suffix change_type and path prefix
    Example: suffix filter returns only feature entries
      When impact matrix query is run with suffix ".feature" change_types "-" path_prefix "-"
      Then queried impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/features/01-member-login.feature",
            "change_type": "update",
            "impact_summary": "add last_login_at rule"
          },
          {
            "path": "packages/01-member-login/features/02-login-audit.feature",
            "change_type": "read_only_compare",
            "impact_summary": "reference existing audit rules"
          }
        ]
        """

    Example: change_type filter uses OR semantics for mutable feature workset
      When impact matrix query is run with suffix ".feature" change_types "update,add,conditional_update" path_prefix "-"
      Then queried impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/features/01-member-login.feature",
            "change_type": "update",
            "impact_summary": "add last_login_at rule"
          }
        ]
        """

    Example: spec-by-example consumer query returns only update and add features
      When impact matrix query is run with suffix ".feature" change_types "update,add" path_prefix "-"
      Then queried impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/features/01-member-login.feature",
            "change_type": "update",
            "impact_summary": "add last_login_at rule"
          }
        ]
        """

    Example: plan consumer query returns mutable entries across artifact types
      When impact matrix upsert is run with path "contracts/member-api.yml" change_type "conditional_update" impact_summary "update contract only if API exposes last_login_at"
      And impact matrix query is run with suffix "-" change_types "update,add,conditional_update" path_prefix "-"
      Then queried impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/features/01-member-login.feature",
            "change_type": "update",
            "impact_summary": "add last_login_at rule"
          },
          {
            "path": "packages/01-member-login/dsl.yml",
            "change_type": "update",
            "impact_summary": "extend login vocabulary"
          },
          {
            "path": "contracts/member-api.yml",
            "change_type": "conditional_update",
            "impact_summary": "update contract only if API exposes last_login_at"
          }
        ]
        """

    Example: path prefix filter narrows entries
      When impact matrix query is run with path_prefix "packages/01-member-login/features"
      Then queried impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/features/01-member-login.feature",
            "change_type": "update",
            "impact_summary": "add last_login_at rule"
          },
          {
            "path": "packages/01-member-login/features/02-login-audit.feature",
            "change_type": "read_only_compare",
            "impact_summary": "reference existing audit rules"
          }
        ]
        """

  Rule: CLI query returns wrapped entries JSON
    Example: CLI query with suffix returns filtered entries
      When manage_impact_matrix CLI query is run with suffix ".feature"
      Then CLI exit code is 0
      And CLI impact matrix JSON report should equal:
        """
        {
          "entries": [
            {
              "change_type": "update",
              "impact_summary": "add last_login_at rule",
              "path": "packages/01-member-login/features/01-member-login.feature"
            },
            {
              "change_type": "read_only_compare",
              "impact_summary": "reference existing audit rules",
              "path": "packages/01-member-login/features/02-login-audit.feature"
            }
          ],
          "entries_changed": 0,
          "ok": true,
          "questions": [],
          "report": {
            "summary": "queried impact matrix entries"
          },
          "summary": "queried impact matrix entries",
          "warnings": []
        }
        """

  Rule: CLI resolves default matrix path from project CWD arguments
    Example: query without matrix flag uses IMPACT_MATRIX_YML from arguments.yml
      Given an impact matrix file at the default test path
      And project arguments bind IMPACT_MATRIX_YML to the default test matrix path
      And impact matrix upsert is run with path "packages/01-member-login/features/01-member-login.feature" change_type "update" impact_summary "add last_login_at rule"
      And impact matrix upsert is run with path "packages/01-member-login/features/02-login-audit.feature" change_type "read_only_compare" impact_summary "reference existing audit rules"
      When manage_impact_matrix CLI query is run with suffix ".feature" from project CWD without matrix flag
      Then CLI exit code is 0
      And CLI impact matrix JSON report should equal:
        """
        {
          "entries": [
            {
              "change_type": "update",
              "impact_summary": "add last_login_at rule",
              "path": "packages/01-member-login/features/01-member-login.feature"
            },
            {
              "change_type": "read_only_compare",
              "impact_summary": "reference existing audit rules",
              "path": "packages/01-member-login/features/02-login-audit.feature"
            }
          ],
          "entries_changed": 0,
          "ok": true,
          "questions": [],
          "report": {
            "summary": "queried impact matrix entries"
          },
          "summary": "queried impact matrix entries",
          "warnings": []
        }
        """
