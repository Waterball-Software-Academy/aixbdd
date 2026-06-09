Feature: PostgresSpecParser collects one table Part per CREATE TABLE statement

  Background:
    Given a temporary file at "data/domain.pg.sql" with content:
      """
      CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        nickname VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        bio TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE room_members (
        room_no VARCHAR(50) NOT NULL,
        player_id VARCHAR(50) NOT NULL
      );
      """

  Rule: 後置（狀態）- 每張 CREATE TABLE 應產出單一 table Part
    Example: domain.pg.sql 內兩張 table → 兩個 part
      When PostgresSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned

  Rule: 後置（狀態）- table Part 的 table_name 與 target_part_path 應對應原文
    Example: users / room_members table 各自具備正確 identity
      When PostgresSpecParser parses the last file
      Then the part named "users" has target_part_path "data/domain.pg.sql#users"
      And the part named "room_members" has target_part_path "data/domain.pg.sql#room_members"

  Rule: 後置（狀態）- 每張 table 之 columns 應包含全部欄位與其旗標
    Example: users 表 5 欄位、id 為 pk、created_at 帶 default
      When PostgresSpecParser parses the last file
      Then the part named "users" has columns:
        | name       | type      | nullable | is_pk | has_default |
        | id         | SERIAL    | false    | true  | false       |
        | nickname   | VARCHAR   | false    | false | false       |
        | email      | VARCHAR   | true     | false | false       |
        | bio        | TEXT      | true     | false | false       |
        | created_at | TIMESTAMP | true     | false | true        |
