Feature: route_template_to_file maps a part's source spec to its sibling `*.dsl.yml`

  Rule: 後置（狀態）- `*.api.yml` 應路由到同目錄、stem strip `.api` 後的 `.dsl.yml`
    Example: contracts/room.api.yml → contracts/room.dsl.yml
      When route_template_to_file routes a template with source_spec_path "contracts/room.api.yml"
      Then the routed path is "contracts/room.dsl.yml"

  Rule: 後置（狀態）- `*.openapi.yml` 應路由到同目錄、stem strip `.openapi` 後的 `.dsl.yml`
    Example: contracts/order.openapi.yml → contracts/order.dsl.yml
      When route_template_to_file routes a template with source_spec_path "contracts/order.openapi.yml"
      Then the routed path is "contracts/order.dsl.yml"

  Rule: 後置（狀態）- `*.dbml` stem 本就無 spec suffix，regex 應 no-op
    Example: data/data.dbml → data/data.dsl.yml
      When route_template_to_file routes a template with source_spec_path "data/data.dbml"
      Then the routed path is "data/data.dsl.yml"

  Rule: 後置（狀態）- 多 dbml 分檔的場景應各自 stem → `.dsl.yml`
    Example: data/core.dbml → data/core.dsl.yml
      When route_template_to_file routes a template with source_spec_path "data/core.dbml"
      Then the routed path is "data/core.dsl.yml"

  Rule: 後置（狀態）- `*.mysql.sql` 應路由到同目錄、stem strip `.mysql` 後的 `.dsl.yml`
    Example: data/domain.mysql.sql → data/domain.dsl.yml
      When route_template_to_file routes a template with source_spec_path "data/domain.mysql.sql"
      Then the routed path is "data/domain.dsl.yml"

  Rule: 後置（狀態）- `*.pg.sql` 應路由到同目錄、stem strip `.pg` 後的 `.dsl.yml`
    Example: data/domain.pg.sql → data/domain.dsl.yml
      When route_template_to_file routes a template with source_spec_path "data/domain.pg.sql"
      Then the routed path is "data/domain.dsl.yml"

  Rule: 後置（狀態）- `*.mssql.sql` 應路由到同目錄、stem strip `.mssql` 後的 `.dsl.yml`
    Example: data/domain.mssql.sql → data/domain.dsl.yml
      When route_template_to_file routes a template with source_spec_path "data/domain.mssql.sql"
      Then the routed path is "data/domain.dsl.yml"

  Rule: 後置（狀態）- 多 SQL DDL 分檔場景應各自 stem strip dialect 後綴 → `.dsl.yml`
    Example: data/orders.pg.sql → data/orders.dsl.yml
      When route_template_to_file routes a template with source_spec_path "data/orders.pg.sql"
      Then the routed path is "data/orders.dsl.yml"
