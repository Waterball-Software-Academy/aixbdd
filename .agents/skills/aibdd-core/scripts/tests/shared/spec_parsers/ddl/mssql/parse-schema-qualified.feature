Feature: MSSQLSpecParser strips schema qualifier from bracketed identifiers

  Rule: 後置（狀態）- [dbo].[orders] 的 table Part 應以裸 table 名為 identity
    Example: [dbo].[orders] → table name orders
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE [dbo].[orders] (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_orders PRIMARY KEY (id)
        );
        """
      When MSSQLSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "orders" has target_part_path "data/domain.mssql.sql#orders"
      And the column "orders.id" has has_increment true

  Rule: 後置（狀態）- schema-qualified bracketed FOREIGN KEY 應指向裸 table 名
    Example: REFERENCES [dbo].[users]([id]) → to_table users
      Given a temporary file at "data/domain.mssql.sql" with content:
        """
        CREATE TABLE [dbo].[users] (
          id INT IDENTITY(1,1) NOT NULL,
          CONSTRAINT PK_users PRIMARY KEY (id)
        );

        CREATE TABLE [dbo].[orders] (
          id INT IDENTITY(1,1) NOT NULL,
          user_id INT NOT NULL,
          CONSTRAINT PK_orders PRIMARY KEY (id),
          CONSTRAINT FK_orders_users FOREIGN KEY (user_id) REFERENCES [dbo].[users]([id])
        );
        """
      When MSSQLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.mssql.sql#ref:orders.user_id>users.id"
