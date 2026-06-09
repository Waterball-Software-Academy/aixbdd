Feature: PostgresSpecParser collects FOREIGN KEY constraints as ref Parts

  Rule: 後置（狀態）- 獨立 FOREIGN KEY 宣告應產出 ref Part
    Example: orders.user_id → users.id（table constraint 形式）
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE users (
          id SERIAL PRIMARY KEY
        );

        CREATE TABLE orders (
          id SERIAL PRIMARY KEY,
          user_id INT NOT NULL,
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
      When PostgresSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.pg.sql#ref:orders.user_id>users.id"

  Rule: 後置（狀態）- inline REFERENCES 宣告應產出 ref Part
    Example: user_id INT NOT NULL REFERENCES users(id)（inline 形式）
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE users (
          id SERIAL PRIMARY KEY
        );

        CREATE TABLE memberships (
          id SERIAL PRIMARY KEY,
          user_id INT NOT NULL REFERENCES users(id)
        );
        """
      When PostgresSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "memberships.user_id > users.id" has target_part_path "data/domain.pg.sql#ref:memberships.user_id>users.id"

  Rule: 後置（狀態）- table parts 與 ref parts 應同時存在
    Example: 兩張 table 加一條 FK 得到 2 個 table parts 與 1 個 ref part
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE users (
          id SERIAL PRIMARY KEY
        );

        CREATE TABLE orders (
          id SERIAL PRIMARY KEY,
          user_id INT NOT NULL REFERENCES users(id)
        );
        """
      When PostgresSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned
