Feature: MSSQLSpecParser detects has_increment flag on IDENTITY columns

  Rule: 後置（狀態）- IDENTITY(1,1) 欄位 has_increment 應為 true
    Example: id INT IDENTITY(1,1) NOT NULL → has_increment true
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_users PRIMARY KEY (id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "users.id" has has_increment true

  Rule: 後置（狀態）- IDENTITY 無參數欄位 has_increment 應為 true
    Example: id INT IDENTITY NOT NULL → has_increment true
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE orders (
          id INT IDENTITY NOT NULL,
          PRIMARY KEY (id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "orders.id" has has_increment true

  Rule: 後置（狀態）- PRIMARY KEY 但無 IDENTITY 欄位 has_increment 應為 false
    Example: code NVARCHAR(50) NOT NULL PRIMARY KEY → has_increment false
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE products (
          code NVARCHAR(50) NOT NULL,
          CONSTRAINT PK_products PRIMARY KEY (code)
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "products.code" has has_increment false

  Rule: 後置（狀態）- 非 pk 欄位 has_increment 應為 false
    Example: nickname NVARCHAR NOT NULL → has_increment false
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          nickname NVARCHAR(255) NOT NULL
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "users.nickname" has has_increment false
