Feature: MySQLSpecParser handles backtick-quoted identifiers (mysqldump style)

  Rule: 後置（狀態）- backtick 包裹的 table / column 名稱應正確去引號
    Example: `users` 表含 backtick 欄位 → table 與欄位名稱皆去除 backtick
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE `users` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `nickname` VARCHAR(255) NOT NULL,
          `email` VARCHAR(255),
          PRIMARY KEY (`id`)
        );
        """
      When MySQLSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "users" has target_part_path "data/domain.mysql.sql#users"
      And the part named "users" has columns:
        | name     | type    | nullable | is_pk | has_default |
        | id       | INT     | false    | true  | false       |
        | nickname | VARCHAR | false    | false | false       |
        | email    | VARCHAR | true     | false | false       |

  Rule: 後置（狀態）- backtick 包裹的 CREATE TABLE IF NOT EXISTS 仍應被解析
    Example: CREATE TABLE IF NOT EXISTS `rooms` → 一個 table part
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE IF NOT EXISTS `rooms` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `status` VARCHAR(20) NOT NULL DEFAULT 'lobby',
          PRIMARY KEY (`id`)
        );
        """
      When MySQLSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "rooms" has target_part_path "data/domain.mysql.sql#rooms"
      And the column "rooms.status" has has_default true
      And the column "rooms.status" has default_value "lobby"

  Rule: 後置（狀態）- backtick 包裹的 FOREIGN KEY 應產出去引號的 ref Part
    Example: `orders`.`user_id` → `users`.`id`
      Given a temporary file at "data/domain.mysql.sql" with content:
        """
        CREATE TABLE `users` (
          `id` INT NOT NULL AUTO_INCREMENT,
          PRIMARY KEY (`id`)
        );

        CREATE TABLE `orders` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `user_id` INT NOT NULL,
          PRIMARY KEY (`id`),
          FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
        );
        """
      When MySQLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.mysql.sql#ref:orders.user_id>users.id"
