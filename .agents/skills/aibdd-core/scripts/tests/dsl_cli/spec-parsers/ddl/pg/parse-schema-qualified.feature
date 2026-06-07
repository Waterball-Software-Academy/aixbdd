Feature: PostgresSpecParser strips schema qualifier from table identifiers

  Rule: 後置（狀態）- schema.table 的 table Part 應以裸 table 名為 identity
    Example: public.users → table name users
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE public.users (
          id SERIAL PRIMARY KEY,
          email VARCHAR(255) NOT NULL
        );
        """
      When PostgresSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "users" has target_part_path "data/domain.pg.sql#users"

  Rule: 後置（狀態）- schema-qualified table-level FOREIGN KEY 應指向裸 table 名
    Example: REFERENCES public.users(id) → to_table users
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE public.users (
          id SERIAL PRIMARY KEY
        );

        CREATE TABLE public.orders (
          id SERIAL PRIMARY KEY,
          user_id INTEGER NOT NULL,
          FOREIGN KEY (user_id) REFERENCES public.users(id)
        );
        """
      When PostgresSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned
      And exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.pg.sql#ref:orders.user_id>users.id"

  Rule: 後置（狀態）- schema-qualified inline REFERENCES 應指向裸 table 名
    Example: user_id INTEGER NOT NULL REFERENCES public.users(id) → to_table users
      Given a temporary file at "data/domain.pg.sql" with content:
        """
        CREATE TABLE public.users (
          id SERIAL PRIMARY KEY
        );

        CREATE TABLE public.orders (
          id SERIAL PRIMARY KEY,
          user_id INTEGER NOT NULL REFERENCES public.users(id)
        );
        """
      When PostgresSpecParser parses the last file
      Then exactly 1 part of kind "ref" is returned
      And the ref part "orders.user_id > users.id" has target_part_path "data/domain.pg.sql#ref:orders.user_id>users.id"
