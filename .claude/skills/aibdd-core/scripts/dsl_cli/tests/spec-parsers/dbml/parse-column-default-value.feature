Feature: DBMLSpecParser extracts column default_value string from DBML options

  Rule: 後置（狀態）- 有 default: '<literal>' 的欄位應帶出 default_value 字串（不含引號）
    Example: role varchar [not null, default: 'guest'] → default_value "guest"
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          role varchar [not null, default: 'guest']
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "users.role" has has_default true
      And the column "users.role" has default_value "guest"

  Rule: 後置（狀態）- 有 default: <integer> 的欄位應帶出 default_value 字串
    Example: score int [default: 0] → default_value "0"
      Given a temporary file at "data/data.dbml" with content:
        """
        Table game {
          score int [default: 0]
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "game.score" has has_default true
      And the column "game.score" has default_value "0"

  Rule: 後置（狀態）- 有 default: `<expression>` 的欄位應帶出 default_value 字串（不含 backtick）
    Example: created_at timestamp [default: `now()`] → default_value "now()"
      Given a temporary file at "data/data.dbml" with content:
        """
        Table events {
          created_at timestamp [default: `now()`]
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "events.created_at" has has_default true
      And the column "events.created_at" has default_value "now()"

  Rule: 後置（狀態）- 無 default 的欄位 default_value 應為 null
    Example: nickname varchar [not null] → default_value null
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          nickname varchar [not null]
        }
        """
      When DBMLSpecParser parses the last file
      Then the column "users.nickname" has has_default false
      And the column "users.nickname" has default_value null
