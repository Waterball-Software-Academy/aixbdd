Feature: DBMLSpecParser detects has_increment flag on Column

  Rule: 後置（狀態）- [pk, increment] 欄位 has_increment 應為 true
    Example: id int [pk, increment] → has_increment true
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          id int [pk, increment]
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "users.id" has has_increment true

  Rule: 後置（狀態）- [pk] 欄位（無 increment）has_increment 應為 false
    Example: code varchar [pk] → has_increment false
      Given a temporary file at "data/data.dbml" with content:
        """
        Table products {
          code varchar [pk]
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "products.code" has has_increment false

  Rule: 後置（狀態）- 非 pk 欄位 has_increment 應為 false
    Example: nickname varchar [not null] → has_increment false
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          nickname varchar [not null]
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "users.nickname" has has_increment false
