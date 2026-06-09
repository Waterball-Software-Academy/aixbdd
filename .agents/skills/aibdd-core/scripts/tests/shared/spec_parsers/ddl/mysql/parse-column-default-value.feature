Feature: MySQLSpecParser extracts column default_value from DDL DEFAULT clauses

  Rule: 後置（狀態）- DEFAULT '<literal>' 欄位應帶出 default_value 字串（不含引號）
    Example: status VARCHAR(20) NOT NULL DEFAULT 'lobby' → default_value "lobby"
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE rooms (
          id INT NOT NULL AUTO_INCREMENT,
          status VARCHAR(20) NOT NULL DEFAULT 'lobby',
          PRIMARY KEY (id)
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "rooms.status" has has_default true
      And the column "rooms.status" has default_value "lobby"

  Rule: 後置（狀態）- DEFAULT <integer> 欄位應帶出 default_value 字串
    Example: score INT NOT NULL DEFAULT 0 → default_value "0"
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE players (
          score INT NOT NULL DEFAULT 0
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "players.score" has has_default true
      And the column "players.score" has default_value "0"

  Rule: 後置（狀態）- DEFAULT CURRENT_TIMESTAMP 欄位應帶出 default_value 字串
    Example: created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP → default_value "CURRENT_TIMESTAMP"
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE events (
          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "events.created_at" has has_default true
      And the column "events.created_at" has default_value "CURRENT_TIMESTAMP"

  Rule: 後置（狀態）- 無 DEFAULT 子句的欄位 default_value 應為 null
    Example: nickname VARCHAR(255) NOT NULL → default_value null
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE users (
          nickname VARCHAR(255) NOT NULL
        );
        """
      When MySQLSpecParser parses the last file
      Then the column "users.nickname" has has_default false
      And the column "users.nickname" has default_value null
