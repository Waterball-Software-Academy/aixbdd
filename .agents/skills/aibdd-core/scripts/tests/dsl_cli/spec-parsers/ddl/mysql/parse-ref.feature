Feature: MySQLSpecParser collects FOREIGN KEY constraints as ref Parts

  Rule: 後置（狀態）- FOREIGN KEY ... REFERENCES 應產出 ref Part
    Example: orders.user_id → users.id
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE users (
          id INT NOT NULL AUTO_INCREMENT,
          PRIMARY KEY (id)
        );

        CREATE TABLE orders (
          id INT NOT NULL AUTO_INCREMENT,
          user_id INT NOT NULL,
          PRIMARY KEY (id),
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
      When MySQLSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.mysql.sql#ref:orders.user_id>users.id"

  Rule: 後置（狀態）- table parts 與 ref parts 應同時存在
    Example: 兩張 table 加一條 FK 會得到 2 個 table parts 與 1 個 ref part
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE users (
          id INT NOT NULL AUTO_INCREMENT,
          PRIMARY KEY (id)
        );

        CREATE TABLE orders (
          id INT NOT NULL AUTO_INCREMENT,
          user_id INT NOT NULL,
          PRIMARY KEY (id),
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
      When MySQLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned
