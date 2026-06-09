Feature: MySQLSpecParser detects has_increment flag on AUTO_INCREMENT column

  Rule: 後置（狀態）- AUTO_INCREMENT 欄位 has_increment 應為 true
    Example: id INT NOT NULL AUTO_INCREMENT → has_increment true
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE users (
          id INT NOT NULL AUTO_INCREMENT,
          PRIMARY KEY (id)
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "users.id" has has_increment true

  Rule: 後置（狀態）- PRIMARY KEY 但無 AUTO_INCREMENT 欄位 has_increment 應為 false
    Example: code VARCHAR NOT NULL PRIMARY KEY → has_increment false
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE products (
          code VARCHAR(50) NOT NULL,
          PRIMARY KEY (code)
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "products.code" has has_increment false

  Rule: 後置（狀態）- 非 pk 欄位 has_increment 應為 false
    Example: nickname VARCHAR NOT NULL → has_increment false
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE users (
          nickname VARCHAR(255) NOT NULL
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "users.nickname" has has_increment false
