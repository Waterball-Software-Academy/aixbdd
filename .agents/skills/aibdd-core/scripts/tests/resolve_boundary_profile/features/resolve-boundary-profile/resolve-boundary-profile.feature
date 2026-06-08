Feature: resolve merged boundary profile from base preset + boundary.yml overrides

  Rule: missing boundary.yml fails with explicit stderr
    Example: boundary.yml absent at the project path
      Given a temporary project directory at the default test path
      When resolve_boundary_profile CLI is run
      Then CLI exit code is 1
      And CLI stdout should be empty
      And CLI stderr should equal:
        """
        [resolve-boundary-profile] boundary.yml not found at specs/architecture/boundary.yml
        """

  Rule: boundary.yml without a type fails
    Example: boundary.yml present but no type field
      Given a temporary project directory at the default test path
      And a boundary file at "specs/architecture/boundary.yml" with content:
        """
        id: backend
        role: backend
        """
      When resolve_boundary_profile CLI is run
      Then CLI exit code is 1
      And CLI stdout should be empty
      And CLI stderr should equal:
        """
        [resolve-boundary-profile] boundary.yml has no 'type' field
        """

  Rule: base preset not found for the boundary type fails
    Example: type points at a preset that does not exist in the assets root
      Given a temporary project directory at the default test path
      And a boundary file at "specs/architecture/boundary.yml" with content:
        """
        type: web-service
        """
      When resolve_boundary_profile CLI is run
      Then CLI exit code is 1
      And CLI stdout should be empty
      And CLI stderr should equal:
        """
        [resolve-boundary-profile] base profile not found for boundary type 'web-service' at boundaries/web-service/profile.yml
        """

  Rule: no overrides emits the base preset as the merged profile
    Example: boundary.yml declares only a type
      Given a temporary project directory at the default test path
      And a boundaries assets root with a "web-service" base profile:
        """
        id: web-service
        role: backend
        state_specifier:
          skill: /aibdd-form-entity-spec
          format: dbml
          output_dir_key: DATA_DIR
          default_filename: domain.dbml
        operation_contract_specifier:
          skill: /aibdd-form-api-spec
          format: openapi
          output_dir_key: CONTRACTS_DIR
          default_filename: api.yml
        """
      And a boundary file at "specs/architecture/boundary.yml" with content:
        """
        type: web-service
        """
      When resolve_boundary_profile CLI is run
      Then CLI exit code is 0
      And CLI JSON output should equal:
        """
        {
          "id": "web-service",
          "role": "backend",
          "state_specifier": {
            "skill": "/aibdd-form-entity-spec",
            "format": "dbml",
            "output_dir_key": "DATA_DIR",
            "default_filename": "domain.dbml"
          },
          "operation_contract_specifier": {
            "skill": "/aibdd-form-api-spec",
            "format": "openapi",
            "output_dir_key": "CONTRACTS_DIR",
            "default_filename": "api.yml"
          }
        }
        """

  Rule: an override replaces the whole top-level key
    Example: a complete state_specifier override swaps DBML formulation for DDL
      Given a temporary project directory at the default test path
      And a boundaries assets root with a "web-service" base profile:
        """
        id: web-service
        role: backend
        state_specifier:
          skill: /aibdd-form-entity-spec
          format: dbml
          output_dir_key: DATA_DIR
          default_filename: domain.dbml
        operation_contract_specifier:
          skill: /aibdd-form-api-spec
          format: openapi
          output_dir_key: CONTRACTS_DIR
          default_filename: api.yml
        """
      And a boundary file at "specs/architecture/boundary.yml" with content:
        """
        type: web-service
        profile_overrides:
          state_specifier:
            skill: /aibdd-form-ddl-spec
            format: pg
            output_dir_key: DATA_DIR
            default_filename: domain.sql
        """
      When resolve_boundary_profile CLI is run
      Then CLI exit code is 0
      And CLI JSON output should equal:
        """
        {
          "id": "web-service",
          "role": "backend",
          "state_specifier": {
            "skill": "/aibdd-form-ddl-spec",
            "format": "pg",
            "output_dir_key": "DATA_DIR",
            "default_filename": "domain.sql"
          },
          "operation_contract_specifier": {
            "skill": "/aibdd-form-api-spec",
            "format": "openapi",
            "output_dir_key": "CONTRACTS_DIR",
            "default_filename": "api.yml"
          }
        }
        """

  Rule: whole-key replacement drops base sub-keys the override omits
    Example: override supplying only skill + format loses base output_dir_key and default_filename
      Given a temporary project directory at the default test path
      And a boundaries assets root with a "web-service" base profile:
        """
        id: web-service
        role: backend
        state_specifier:
          skill: /aibdd-form-entity-spec
          format: dbml
          output_dir_key: DATA_DIR
          default_filename: domain.dbml
        """
      And a boundary file at "specs/architecture/boundary.yml" with content:
        """
        type: web-service
        profile_overrides:
          state_specifier:
            skill: /aibdd-form-ddl-spec
            format: pg
        """
      When resolve_boundary_profile CLI is run
      Then CLI exit code is 0
      And CLI JSON output should equal:
        """
        {
          "id": "web-service",
          "role": "backend",
          "state_specifier": {
            "skill": "/aibdd-form-ddl-spec",
            "format": "pg"
          }
        }
        """
