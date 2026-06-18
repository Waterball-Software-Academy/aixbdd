Feature: DBMLSpecParser preserves DBML column type text

  Rule: 後置（狀態）- column type 可包含括號參數
    Example: varchar(255) and decimal(10,2) are preserved
      Given a temporary file at "data/types.dbml" with content:
        """
        Table products {
          sku varchar(255) [pk]
          price decimal(10,2) [not null]
        }
        """
      When DBMLSpecParser parses the last file
      Then the part named "products" has columns:
        | name  | type          | nullable | is_pk | has_default |
        | sku   | varchar(255)  | false    | true  | false       |
        | price | decimal(10,2) | false    | false | false       |

  Rule: 後置（狀態）- column type 可用雙引號包住包含空白的型別
    Example: "double precision" is preserved without quotes
      Given a temporary file at "data/types.dbml" with content:
        """
        Table measurements {
          value "double precision" [not null]
        }
        """
      When DBMLSpecParser parses the last file
      Then the part named "measurements" has columns:
        | name  | type             | nullable | is_pk | has_default |
        | value | double precision | false    | false | false       |
