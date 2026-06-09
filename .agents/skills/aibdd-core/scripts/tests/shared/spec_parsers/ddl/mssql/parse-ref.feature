Feature: MSSQLSpecParser collects FOREIGN KEY constraints as ref Parts

  Rule: 後置（狀態）- FOREIGN KEY ... REFERENCES 應產出 ref Part
    Example: orders.user_id → users.id（table constraint 形式）
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_users PRIMARY KEY (id)
        );

        CREATE TABLE orders (
          id INT IDENTITY(1,1) NOT NULL,
          user_id INT NOT NULL,
          CONSTRAINT PK_orders PRIMARY KEY (id),
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.mssql.sql#ref:orders.user_id>users.id"

  Rule: 後置（狀態）- 具名 CONSTRAINT FK 應產出 ref Part
    Example: CONSTRAINT FK_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_users PRIMARY KEY (id)
        );

        CREATE TABLE orders (
          id INT IDENTITY(1,1) NOT NULL,
          user_id INT NOT NULL,
          CONSTRAINT PK_orders PRIMARY KEY (id),
          CONSTRAINT FK_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.mssql.sql#ref:orders.user_id>users.id"

  Rule: 後置（狀態）- table parts 與 ref parts 應同時存在
    Example: 兩張 table 加一條 FK 得到 2 個 table parts 與 1 個 ref part
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE users (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_users PRIMARY KEY (id)
        );

        CREATE TABLE orders (
          id INT IDENTITY(1,1) NOT NULL,
          user_id INT NOT NULL,
          CONSTRAINT PK_orders PRIMARY KEY (id),
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned
