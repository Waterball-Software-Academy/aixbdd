Feature: DBMLSpecParser accepts quoted column names

  Rule: 後置（狀態）- column name 可用雙引號包住包含空白的名稱
    Example: "display name" becomes a column named display name
      Given a temporary file at "data/quoted-columns.dbml" with content:
        """
        Table users {
          id int [pk]
          "display name" varchar [not null]
        }
        """
      When DBMLSpecParser parses the last file
      Then the part named "users" has columns:
        | name         | type    | nullable | is_pk | has_default |
        | id           | int     | false    | true  | false       |
        | display name | varchar | false    | false | false       |
      And the column "users.display name" has target_part_path "data/quoted-columns.dbml#users.display name"
