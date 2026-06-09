Feature: MSSQLSpecParser derives not_null_columns from each CREATE TABLE

  Background:
    Given a temporary file at "data/domain.mssql.sql" with content:
      """
      CREATE TABLE room_members (
        room_no NVARCHAR(50) NOT NULL,
        player_id NVARCHAR(50) NOT NULL,
        joined_at DATETIME2
      );
      """

  Rule: 後置（狀態）- NOT NULL 欄位應出現在 not_null_columns
    Example: room_no / player_id 均為 NOT NULL → not_null_columns 包含這兩欄
      When MSSQLSpecParser parses the last file
      Then the part named "room_members" has not_null_columns:
        | name      |
        | room_no   |
        | player_id |

  Rule: 後置（狀態）- 每欄 target_part_path 應為 `<spec>#<table>.<column>`
    Example: room_members.room_no 與 room_members.player_id 路徑正確
      When MSSQLSpecParser parses the last file
      Then the column "room_members.room_no" has target_part_path "data/domain.mssql.sql#room_members.room_no"
      And the column "room_members.player_id" has target_part_path "data/domain.mssql.sql#room_members.player_id"

  Rule: 後置（狀態）- PRIMARY KEY 欄位 nullable 應為 false
    Example: id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK PRIMARY KEY → nullable false
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_users PRIMARY KEY (id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "users.id" has nullable false
