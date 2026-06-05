Feature: manage discovery impact matrix

  Background:
    Given an impact matrix file at the default test path

  Rule: init creates a valid empty impact matrix
    Example: empty matrix has version and entries list
      When impact matrix init is run on the default test path
      Then the impact matrix YAML should equal:
        """
        version: 1
        entries: []
        """

  Rule: upsert creates and overwrites explicit file entries
    Example: upsert adds one feature entry
      When impact matrix upsert is run with path "packages/01-member-login/features/01-member-login.feature" change_type "update" impact_summary "add last_login_at rule"
      Then impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/features/01-member-login.feature",
            "change_type": "update",
            "impact_summary": "add last_login_at rule"
          }
        ]
        """

    Example: upsert same path overwrites instead of duplicating
      When impact matrix upsert is run with path "packages/01-member-login/dsl.yml" change_type "update" impact_summary "extend login vocabulary"
      And impact matrix upsert is run with path "packages/01-member-login/dsl.yml" change_type "conditional_update" impact_summary "extend login vocabulary only if API exposes it"
      Then impact matrix entries should equal:
        """
        [
          {
            "path": "packages/01-member-login/dsl.yml",
            "change_type": "conditional_update",
            "impact_summary": "extend login vocabulary only if API exposes it"
          }
        ]
        """

  Rule: delete removes one entry by path
    Example: delete removes existing entry
      When impact matrix upsert is run with path "data/member.dbml" change_type "update" impact_summary "add last_login_at column"
      And impact matrix delete is run with path "data/member.dbml"
      Then the impact matrix YAML should equal:
        """
        version: 1
        entries: []
        """

  Rule: validate rejects invalid enum duplicate path missing fields and glob paths
    Example: invalid enum is rejected
      Given an impact matrix file at "reports/impact-matrix.yml" with content:
        """
        version: 1
        entries:
          - path: packages/01-member-login/dsl.yml
            change_type: UPDATE
            impact_summary: bad enum casing
        """
      When impact matrix validate is run on the default test path
      Then impact matrix validation questions should equal:
        """
        - where: reports/impact-matrix.yml:entries[0]
          type: change_type
          text: change_type 'UPDATE' is invalid; must be one of: read_only_compare, update, add, conditional_update
        """

    Example: duplicate path is rejected
      Given an impact matrix file at "reports/impact-matrix.yml" with content:
        """
        version: 1
        entries:
          - path: packages/01-member-login/dsl.yml
            change_type: update
            impact_summary: first entry
          - path: packages/01-member-login/dsl.yml
            change_type: add
            impact_summary: duplicate path
        """
      When impact matrix validate is run on the default test path
      Then impact matrix validation questions should equal:
        """
        - where: reports/impact-matrix.yml:entries[1]
          type: path
          text: duplicate path `packages/01-member-login/dsl.yml`
        """

    Example: glob path is rejected
      Given an impact matrix file at "reports/impact-matrix.yml" with content:
        """
        version: 1
        entries:
          - path: packages/01-member-login/features/*.feature
            change_type: update
            impact_summary: glob is not allowed
        """
      When impact matrix validate is run on the default test path
      Then impact matrix validation questions should equal:
        """
        - where: reports/impact-matrix.yml:entries[0]
          type: path
          text: path `packages/01-member-login/features/*.feature` contains glob markers; impact-matrix.yml v1 requires explicit per-file paths
        """

    Example: custom enum value is rejected
      Given an impact matrix file at "reports/impact-matrix.yml" with content:
        """
        version: 1
        entries:
          - path: contracts/member-api.yml
            change_type: maybe_update
            impact_summary: invented enum
        """
      When impact matrix validate is run on the default test path
      Then impact matrix validation questions should equal:
        """
        - where: reports/impact-matrix.yml:entries[0]
          type: change_type
          text: change_type 'maybe_update' is invalid; must be one of: read_only_compare, update, add, conditional_update
        """

  Rule: CLI emits the same JSON report contract as lib operations
    Example: CLI init returns valid report
      When manage_impact_matrix CLI init is run on the default test path
      Then CLI exit code is 0
      And CLI impact matrix JSON report should equal:
        """
        {
          "entries": [],
          "entries_changed": 0,
          "matrix_yaml": "version: 1\nentries: []\n",
          "ok": true,
          "questions": [],
          "report": {
            "summary": "initialized impact matrix"
          },
          "summary": "initialized impact matrix",
          "warnings": []
        }
        """

    Example: CLI upsert returns changed entry report
      When manage_impact_matrix CLI upsert is run with path "packages/01-member-login/features/01-member-login.feature" change_type "update" impact_summary "add last_login_at rule"
      Then CLI exit code is 0
      And CLI impact matrix JSON report should equal:
        """
        {
          "entries": [
            {
              "change_type": "update",
              "impact_summary": "add last_login_at rule",
              "path": "packages/01-member-login/features/01-member-login.feature"
            }
          ],
          "entries_changed": 1,
          "matrix_yaml": "version: 1\nentries:\n- path: packages/01-member-login/features/01-member-login.feature\n  change_type: update\n  impact_summary: add last_login_at rule\n",
          "ok": true,
          "questions": [],
          "report": {
            "summary": "created impact matrix entry"
          },
          "summary": "created impact matrix entry",
          "warnings": []
        }
        """
