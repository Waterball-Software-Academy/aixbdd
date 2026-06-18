Feature: DBMLSpecParser ignores block comments

  Rule: 前置（輸入）- block comment 內的 braces 與假 Table 不應產生 part
    Example: fake Table in block comment is ignored
      Given a temporary file at "data/comments.dbml" with content:
        """
        /*
        Table ghost {
          id int [pk]
          indexes {
            id [unique]
          }
        }
        */

        Table users {
          id int [pk]
        }
        """
      When DBMLSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "users" has target_part_path "data/comments.dbml#users"

  Rule: 前置（輸入）- table 內 block comment 的 braces 不應破壞 table body
    Example: block comment inside table is ignored
      Given a temporary file at "data/comments.dbml" with content:
        """
        Table users {
          id int [pk]
          /*
          indexes {
            id [unique]
          }
          fake_column varchar
          */
          email varchar [not null]
        }
        """
      When DBMLSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "users" has columns:
        | name  | type    | nullable | is_pk | has_default |
        | id    | int     | false    | true  | false       |
        | email | varchar | false    | false | false       |
