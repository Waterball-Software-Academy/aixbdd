Feature: PostgresSpecParser detects has_increment on SERIAL and GENERATED IDENTITY columns

  Rule: 後置（狀態）- SERIAL 欄位 has_increment 應為 true
    Example: id SERIAL PRIMARY KEY → has_increment true
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE users (
          id SERIAL PRIMARY KEY
        );
        """
      When PostgresSpecParser parses the last file
      Then the column "users.id" has has_increment true

  Rule: 後置（狀態）- BIGSERIAL 欄位 has_increment 應為 true
    Example: id BIGSERIAL PRIMARY KEY → has_increment true
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE events (
          id BIGSERIAL PRIMARY KEY
        );
        """
      When PostgresSpecParser parses the last file
      Then the column "events.id" has has_increment true

  Rule: 後置（狀態）- GENERATED ALWAYS AS IDENTITY 欄位 has_increment 應為 true
    Example: id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY → has_increment true
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE products (
          id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY
        );
        """
      When PostgresSpecParser parses the last file
      Then the column "products.id" has has_increment true

  Rule: 後置（狀態）- 非自增欄位 has_increment 應為 false
    Example: code VARCHAR PRIMARY KEY → has_increment false
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE categories (
          code VARCHAR(50) PRIMARY KEY
        );
        """
      When PostgresSpecParser parses the last file
      Then the column "categories.code" has has_increment false
