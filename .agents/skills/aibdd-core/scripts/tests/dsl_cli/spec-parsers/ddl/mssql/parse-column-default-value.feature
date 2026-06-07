Feature: MSSQLSpecParser extracts column default_value from DDL DEFAULT clauses

  Rule: 後置（狀態）- DEFAULT '<literal>' 欄位應帶出 default_value 字串（不含引號）
    Example: status NVARCHAR(20) NOT NULL DEFAULT 'lobby' → default_value "lobby"
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE rooms (
          id INT IDENTITY(1,1) NOT NULL,
          status NVARCHAR(20) NOT NULL DEFAULT 'lobby',
          CONSTRAINT PK_rooms PRIMARY KEY (id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "rooms.status" has has_default true
      And the column "rooms.status" has default_value "lobby"

  Rule: 後置（狀態）- DEFAULT <integer> 欄位應帶出 default_value 字串
    Example: score INT NOT NULL DEFAULT 0 → default_value "0"
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE players (
          score INT NOT NULL DEFAULT 0
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "players.score" has has_default true
      And the column "players.score" has default_value "0"

  Rule: 後置（狀態）- DEFAULT GETDATE() 欄位應帶出 default_value 字串
    Example: created_at DATETIME2 NOT NULL DEFAULT GETDATE() → default_value "GETDATE()"
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE events (
          created_at DATETIME2 NOT NULL DEFAULT GETDATE()
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "events.created_at" has has_default true
      And the column "events.created_at" has default_value "GETDATE()"

  Rule: 後置（狀態）- 無 DEFAULT 子句的欄位 default_value 應為 null
    Example: nickname NVARCHAR(255) NOT NULL → default_value null
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          nickname NVARCHAR(255) NOT NULL
        );
        """
      When MSSQLSpecParser parses the last file
      Then the column "users.nickname" has has_default false
      And the column "users.nickname" has default_value null
