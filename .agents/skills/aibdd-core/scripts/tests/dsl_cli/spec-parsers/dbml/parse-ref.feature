Feature: DBMLSpecParser collects ref Parts from DBML relationships

  Rule: 後置（狀態）- top-level Ref 應產出一個 ref Part
    Example: posts.user_id > users.id 會成為 relationship part
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          id int [pk, increment]
        }

        Table posts {
          id int [pk, increment]
          user_id int [not null]
        }

        Ref: posts.user_id > users.id
        """
      When DBMLSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "posts.user_id > users.id" has target_part_path "data/data.dbml#ref:posts.user_id>users.id"

  Rule: 後置（狀態）- inline ref option 應產出一個 ref Part
    Example: memberships.user_id [ref: > users.id] 會成為 relationship part
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          id int [pk, increment]
        }

        Table memberships {
          id int [pk, increment]
          user_id int [not null, ref: > users.id]
        }
        """
      When DBMLSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "memberships.user_id > users.id" has target_part_path "data/data.dbml#ref:memberships.user_id>users.id"

  Rule: 後置（狀態）- table parts 與 relationship parts 應同時存在
    Example: 兩張 table 加一條 Ref 會得到 2 個 table parts 與 1 個 ref part
      Given a temporary file at "data/data.dbml" with content:
        """
        Table rooms {
          id int [pk, increment]
        }

        Table room_members {
          id int [pk, increment]
          room_id int [not null]
        }

        Ref: room_members.room_id > rooms.id
        """
      When DBMLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned

  Rule: 前置（狀態）- malformed ref syntax 不應誤產 ref Part
    Example: inline ref 少了 target table.column 時只保留 table parts
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          id int [pk, increment]
        }

        Table memberships {
          id int [pk, increment]
          user_id int [not null, ref: >]
        }
        """
      When DBMLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 0 parts of kind "ref" are returned
