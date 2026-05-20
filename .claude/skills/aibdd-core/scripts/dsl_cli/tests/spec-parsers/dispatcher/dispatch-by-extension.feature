Feature: dispatch_spec_parser routes a spec file to its concrete parser by suffix

  Rule: 後置（狀態）- *.api.yml 應路由到 OpenAPISpecParser
    Example: contracts/room.api.yml → OpenAPISpecParser
      Given a temporary file at "contracts/room.api.yml" with content:
        """
        openapi: 3.0.0
        """
      When dispatch_spec_parser is called on the last file
      Then the dispatched parser is an instance of "OpenAPISpecParser"

  Rule: 後置（狀態）- *.openapi.yml 也應路由到 OpenAPISpecParser
    Example: contracts/order.openapi.yml → OpenAPISpecParser
      Given a temporary file at "contracts/order.openapi.yml" with content:
        """
        openapi: 3.0.0
        """
      When dispatch_spec_parser is called on the last file
      Then the dispatched parser is an instance of "OpenAPISpecParser"

  Rule: 後置（狀態）- *.dbml 應路由到 DBMLSpecParser
    Example: data/data.dbml → DBMLSpecParser
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users { id int [pk] }
        """
      When dispatch_spec_parser is called on the last file
      Then the dispatched parser is an instance of "DBMLSpecParser"

  Rule: 後置（狀態）- 同一 scenario 內可對多份不同副檔名的檔案各自正確 dispatch
    Example: 同時放 .api.yml 與 .dbml，兩者 dispatch 結果獨立正確
      Given a temporary file at "contracts/a.api.yml" with content (saved as "api"):
        """
        openapi: 3.0.0
        """
      And a temporary file at "data/b.dbml" with content (saved as "dbml"):
        """
        Table t { id int [pk] }
        """
      When dispatch_spec_parser is called on the file aliased "api"
      Then the dispatched parser is an instance of "OpenAPISpecParser"
      When dispatch_spec_parser is called on the file aliased "dbml"
      Then the dispatched parser is an instance of "DBMLSpecParser"

  Rule: 後置（回應）- 未知副檔名應 raise ValueError
    Example: random.txt → ValueError
      Given a temporary file at "stray/random.txt" with content:
        """
        nothing structured
        """
      When dispatch_spec_parser is called on the last file and captures the exception
      Then the captured exception is of type "ValueError"
