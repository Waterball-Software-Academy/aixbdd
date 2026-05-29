Feature: compute_unresolved treats a part as resolved iff some entry's target is part-or-descendant

  Background:
    Given the following parts:
      | target_part_path                                                |
      | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post      |
      | contracts/room.api.yml#/paths/~1posts/post                      |
      | data/data.dbml#users                                            |
      | data/data.dbml#room                                             |

  Rule: 後置（狀態）- entry target 是 part path 之子路徑時，該 part 應視為 resolved
    Example: OpenAPI operation 的 200 response entry 視作 operation part 已 resolved
      Given the following resolved targets:
        | target_part_path                                                                                    |
        | contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/responses/200                            |
      When compute_unresolved is called
      Then unresolved parts do not include "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post"

  Rule: 後置（狀態）- entry target 在不同分支時，該 part 不應被誤判 resolved
    Example: 兄弟 path 的 entry 不能 resolve 不同 part
      Given the following resolved targets:
        | target_part_path                                                |
        | contracts/room.api.yml#/paths/~1other~1path/post                |
      When compute_unresolved is called
      Then unresolved parts include "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post"

  Rule: 後置（狀態）- 字串前綴陷阱：路徑分段不可被字串 prefix 誤匹
    Example: `/posts` 的 entry 不應 resolve `/rooms` 的 part
      Given the following resolved targets:
        | target_part_path                                                |
        | contracts/room.api.yml#/paths/~1posts/post/responses/200        |
      When compute_unresolved is called
      Then unresolved parts include "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post"
      And unresolved parts do not include "contracts/room.api.yml#/paths/~1posts/post"

  Rule: 後置（狀態）- DBML 分段前綴亦不可被字串 prefix 誤匹
    Example: `room_members.*` entry 不應 resolve `room` 部位（不同 table 名）
      Given the following resolved targets:
        | target_part_path                |
        | data/data.dbml#room_members.id  |
      When compute_unresolved is called
      Then unresolved parts include "data/data.dbml#room"
      And unresolved parts include "data/data.dbml#users"

  Rule: 後置（狀態）- DBML column entry 視作 table part 已 resolved
    Example: users.id entry 視作 users table 已 resolved
      Given the following resolved targets:
        | target_part_path        |
        | data/data.dbml#users.id |
      When compute_unresolved is called
      Then unresolved parts do not include "data/data.dbml#users"

  Rule: 後置（狀態）- relationship anchor 只有完全相等時才視為 resolved
    Example: 同一條 ref entry 應 resolve 同一條 relationship part
      Given the following parts:
        | target_part_path                             |
        | data/data.dbml#ref:room_members.player_id>users.id |
      And the following resolved targets:
        | target_part_path                             |
        | data/data.dbml#ref:room_members.player_id>users.id |
      When compute_unresolved is called
      Then unresolved parts do not include "data/data.dbml#ref:room_members.player_id>users.id"

  Rule: 後置（狀態）- 不同 relationship anchor 不可互相誤判 resolved
    Example: 另一條 ref entry 不能 resolve 當前 relationship part
      Given the following parts:
        | target_part_path                             |
        | data/data.dbml#ref:room_members.player_id>users.id |
      And the following resolved targets:
        | target_part_path                             |
        | data/data.dbml#ref:room_members.room_id>rooms.id |
      When compute_unresolved is called
      Then unresolved parts include "data/data.dbml#ref:room_members.player_id>users.id"

  Rule: 後置（狀態）- 跨 spec_file 不應 cross-resolve
    Example: data.dbml 的 entry 不能 resolve room.api.yml 的 part（即使 pointer 字面類似）
      Given the following resolved targets:
        | target_part_path                                                |
        | data/data.dbml#/paths/~1rooms~1{roomNo}~1join/post              |
      When compute_unresolved is called
      Then unresolved parts include "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post"
