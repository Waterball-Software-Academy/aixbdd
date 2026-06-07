Feature: MSSQLSpecParser collects one table Part per CREATE TABLE statement

  Background:
    Given a temporary file at "data/domain.mssql.sql" with content:
      """
      CREATE TABLE users (
        id INT IDENTITY(1,1) NOT NULL,
        nickname NVARCHAR(255) NOT NULL,
        email NVARCHAR(255),
        bio NVARCHAR(MAX),
        created_at DATETIME2 DEFAULT GETDATE(),
        CONSTRAINT PK_users PRIMARY KEY (id)
      );

      CREATE TABLE room_members (
        room_no NVARCHAR(50) NOT NULL,
        player_id NVARCHAR(50) NOT NULL
      );
      """

  Rule: 後置（狀態）- 每張 CREATE TABLE 應產出單一 table Part
    Example: domain.mssql.sql 內兩張 table → 兩個 part
      When MSSQLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned

  Rule: 後置（狀態）- table Part 的 table_name 與 target_part_path 應對應原文
    Example: users / room_members table 各自具備正確 identity
      When MSSQLSpecParser parses the last file
      Then the part named "users" has target_part_path "data/domain.mssql.sql#users"
      And the part named "room_members" has target_part_path "data/domain.mssql.sql#room_members"

  Rule: 後置（狀態）- 每張 table 之 columns 應包含全部欄位與其旗標
    Example: users 表 5 欄位、id 為 pk、created_at 帶 default
      When MSSQLSpecParser parses the last file
      Then the part named "users" has columns:
        | name       | type      | nullable | is_pk | has_default |
        | id         | INT       | false    | true  | false       |
        | nickname   | NVARCHAR  | false    | false | false       |
        | email      | NVARCHAR  | true     | false | false       |
        | bio        | NVARCHAR  | true     | false | false       |
        | created_at | DATETIME2 | true     | false | true        |
