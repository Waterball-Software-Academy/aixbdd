Feature: ActivityCodec — decode
  作為 Graph Facade
  我要 將 .activity 檔案內容解析為 ActivityAggregate
  以便 支援 Activity DSL 的載入與 Visual Editor 編輯

  # ─── 檔案頂層結構 ─────────────────────────────────────────────

  Rule: [ACTIVITY] 必為檔案首個非空 tag，否則 ParseError: "Expected '[ACTIVITY]' declaration"

    Example: 缺少 [ACTIVITY] header 回傳 ParseError
      Given 以下 activity 內容:
        """
        [ACTOR] 使用者
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                        |
        | 1    | Expected '[ACTIVITY]' declaration |

  Rule: [ACTIVITY] body 必須非空，否則 ParseError: "Activity missing name"

    Example: [ACTIVITY] 無 name 回傳 ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message             |
        | 1    | Activity missing name |

  Rule: [FINAL] 數量不限：0、1、多個都合法

    Example: Multiple FINAL decode（多個 [FINAL]）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 多終點
        [ACTOR] 使用者

        [STEP:1] @使用者 輸入
        [DECISION:2a] 是否成功
          [BRANCH:2a:成功]
            [FINAL]
          [BRANCH:2a:失敗]
            [FINAL]
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "多終點",
          "finalNodes": [
            { "id": ">finalNode1" },
            { "id": ">finalNode2" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "輸入",
              "next": "$decision2a"
            },
            {
              "id": ">decision2a",
              "displayId": "2a",
              "type": "decision",
              "condition": "是否成功",
              "paths": [
                { "guard": "成功", "firstNodeId": "$finalNode1" },
                { "guard": "失敗", "firstNodeId": "$finalNode2" }
              ]
            }
          ]
        }
        """

    Example: [FINAL] 可作為主線最後正常結尾
      Given 以下 activity 內容:
        """
        [ACTIVITY] 正常結尾
        [ACTOR] 使用者

        [STEP:1] @使用者 送出
        [FINAL]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "正常結尾",
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "送出",
              "next": "$final0"
            }
          ]
        }
        """

  # ─── [ACTOR] tag ──────────────────────────────────────────────

  Rule: [ACTOR] 有 name 就是合法 actor；binding 可省

    Example: 最小 Activity（只有 header + actor）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            { "name": "使用者" }
          ],
          "nodes": []
        }
        """

  Rule: [ACTOR] 後接 `-> {<path>}` → actor.binding

    Example: [ACTOR] 帶 binding
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者 -> {specs/actors/user.md}
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            {
              "name": "使用者",
              "binding": "specs/actors/user.md"
            }
          ],
          "nodes": []
        }
        """

  # ─── [STEP] body（actor 必填；description / binding 可省）─────

  Rule: [STEP:<N>] 的 N → node.displayId（位置編號）

    # 三合一 [STEP:n] @Actor description {binding}
    Example: [STEP] 同時有 actor、description、binding
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 業務

        [STEP:1] @業務 發起登入 {features/CRM登入.feature}
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            { "name": "業務" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:業務",
              "name": "發起登入",
              "bindsFeature": "features/CRM登入.feature"
            }
          ]
        }
        """

  Rule: [STEP] 開頭 `@<actor>` 必填；缺少 actor 則 ParseError

    Example: [STEP] 只有 description（沒有 actor / binding）→ ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] 系統自動驗證
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                    |
        | 4    | STEP missing actor reference |

    # [STEP] 只有 binding（無 actor、無 description）應 fail
    Example: [STEP] 只有 binding decode（無 actor、無 description）→ ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] {features/self-serve.feature}
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                    |
        | 4    | STEP missing actor reference |

  Rule: [STEP] 中間的描述文字 → node.name；省略時為空字串，保持 ActionBase.name: string

    Example: [STEP] 只有 actor + binding（沒有 description）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] @使用者 {specs/ui/login.md}
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            { "name": "使用者" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "",
              "bindsFeature": "specs/ui/login.md"
            }
          ]
        }
        """

  Rule: [STEP] 末尾 `{<path>}` → node.bindsFeature，可省

    Example: [STEP] 只有 actor + description（沒有 binding）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] @使用者 輸入帳號密碼
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            { "name": "使用者" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "輸入帳號密碼"
            }
          ]
        }
        """

  Rule: [STEP] binding 只允許 `{<path>}`，落進 node.bindsFeature

    Example: [STEP] 帶 binding decode（{...}）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] @使用者 登入 {api/auth/login.json}
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            { "name": "使用者" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "登入",
              "bindsFeature": "api/auth/login.json"
            }
          ]
        }
        """

  Rule: [STEP] binding 容許 `<path>#<fragment>` 形式，fragment 一併進 node.bindsFeature

    # [STEP] 帶 fragment（binding#fragment）
    Example: [STEP] 帶 fragment decode（{binding#fragment}）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] @使用者 查看登入 {specs/ui/login.md#section-1}
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "登入",
          "actors": [
            { "name": "使用者" }
          ],
          "nodes": [
            {
              "displayId": "1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "查看登入",
              "bindsFeature": "specs/ui/login.md#section-1"
            }
          ]
        }
        """

  
  # ─── Decision block ──────────────────────────────────────────

  Rule: [DECISION:N] 開啟一個判斷區塊；所有 [BRANCH:N:*] 都屬於它，且 BRANCH 只開 path 容器，工作內容必須寫在 body；[MERGE:N] 則是這個判斷區塊的收尾，lower 後會成為 merge node。

    Example: [DECISION] + [BRANCH] + [MERGE] decode 成 Decision node 帶 paths
      Given 以下 activity 內容:
        """
        [ACTIVITY] 驗證
        [ACTOR] 系統

        [DECISION:2a] 是否有效
          [BRANCH:2a:有效]
            [STEP:2a.1] @系統 {specs/ui/success.md}
          [BRANCH:2a:無效]
            [STEP:2a.2] @系統 {specs/ui/error.md}
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "驗證",
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "2a",
              "type": "decision",
              "condition": "是否有效",
              "paths": [
                {
                  "guard": "有效",
                  "firstNodeId": "$step2a1"
                },
                {
                  "guard": "無效",
                  "firstNodeId": "$step2a2"
                }
              ]
            },
            {
              "id": ">step2a1",
              "displayId": "2a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/ui/success.md",
              "next": "$merge2a"
            },
            {
              "id": ">step2a2",
              "displayId": "2a.2",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/ui/error.md",
              "next": "$merge2a"
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge",
              "next": "$final0"
            }
          ]
        }
        """

    Example: [BRANCH] 容器內 [STEP] 三合一 decode
      Given 以下 activity 內容:
        """
        [ACTIVITY] 驗證
        [ACTOR] 使用者
        [ACTOR] 系統

        [DECISION:2a] 是否有效
          [BRANCH:2a:有效]
            [STEP:2a.1] @系統 建立訂單 {features/create.feature}
          [BRANCH:2a:無效]
            [STEP:2a.2] @使用者 顯示錯誤 {specs/ui/error.md}
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "nodes": [
            {
              "displayId": "2a",
              "type": "decision",
              "paths": [
                {
                  "guard": "有效",
                  "firstNodeId": "$step2a1"
                },
                {
                  "guard": "無效",
                  "firstNodeId": "$step2a2"
                }
              ]
            },
            {
              "id": ">step2a1",
              "displayId": "2a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "建立訂單",
              "bindsFeature": "features/create.feature",
              "next": "$merge2a"
            },
            {
              "id": ">step2a2",
              "displayId": "2a.2",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "顯示錯誤",
              "bindsFeature": "specs/ui/error.md",
              "next": "$merge2a"
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge"
            }
          ]
        }
        """

    Example: [BRANCH] body 僅含 [FINAL] 時 path.firstNodeId 指向 embedded final
      Given 以下 activity 內容:
        """
        [ACTIVITY] 分支僅終點
        [ACTOR] 系統

        [DECISION:2a] 條件
          [BRANCH:2a:左]
            [FINAL]
          [BRANCH:2a:右]
            [FINAL]
        [MERGE:2a]
        [FINAL]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "分支僅終點",
          "finalNodes": [
            { "id": ">finalTop" },
            { "id": ">embLeft" },
            { "id": ">embRight" }
          ],
          "nodes": [
            {
              "displayId": "2a",
              "type": "decision",
              "condition": "條件",
              "paths": [
                { "guard": "左", "firstNodeId": "$embLeft" },
                { "guard": "右", "firstNodeId": "$embRight" }
              ]
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge",
              "next": "$finalTop"
            }
          ]
        }
        """

    Example: [BRANCH] 內連續多個 [STEP] 後以 [FINAL] 收尾時 next 鏈到 embedded final
      Given 以下 activity 內容:
        """
        [ACTIVITY] 分支多步後終點
        [ACTOR] 系統

        [DECISION:2a] 條件
          [BRANCH:2a:短]
            [FINAL]
          [BRANCH:2a:長]
            [STEP:2a.1] @系統 甲 {specs/ui/a.md}
            [STEP:2a.2] @系統 乙 {specs/ui/b.md}
            [FINAL]
        [MERGE:2a]
        [FINAL]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "name": "分支多步後終點",
          "finalNodes": [
            { "id": ">finalTop" },
            { "id": ">embShort" },
            { "id": ">embLong" }
          ],
          "nodes": [
            {
              "displayId": "2a",
              "type": "decision",
              "condition": "條件",
              "paths": [
                { "guard": "短", "firstNodeId": "$embShort" },
                { "guard": "長", "firstNodeId": "$step2a1" }
              ]
            },
            {
              "id": ">step2a1",
              "displayId": "2a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "甲",
              "bindsFeature": "specs/ui/a.md",
              "next": "$step2a2"
            },
            {
              "id": ">step2a2",
              "displayId": "2a.2",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "乙",
              "bindsFeature": "specs/ui/b.md",
              "next": "$embLong"
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge",
              "next": "$finalTop"
            }
          ]
        }
        """

  Rule: [BRANCH:<N>:<guard> -> <target>] 的 `-> <target>` → path.loopBackTarget，loop 回某個既有 node

    Example: [BRANCH] 支援 loop_back（-> target label）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 重試流程
        [ACTOR] 使用者

        [STEP:1] @使用者 輸入
        [DECISION:2a] 是否成功
          [BRANCH:2a:成功]
          [BRANCH:2a:失敗 -> 1]
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "id": ">step1",
              "displayId": "1",
              "type": "ui_step",
              "next": "$decision2a"
            },
            {
              "id": ">decision2a",
              "displayId": "2a",
              "type": "decision",
              "paths": [
                { "guard": "成功", "firstNodeId": "$merge2a" },
                {
                  "guard": "失敗",
                  "loopBackTarget": "$step1"
                }
              ]
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge",
              "next": "$final0"
            }
          ]
        }
        """

    Example: [BRANCH] loop_back 不可同時有 body → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 重試流程
        [ACTOR] 使用者

        [STEP:1] @使用者 輸入
        [DECISION:2a] 是否成功
          [BRANCH:2a:成功]
          [BRANCH:2a:失敗 -> 1]
            [STEP:2a.1] @使用者 顯示錯誤
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                               |
        | 7    | BRANCH loopBackTarget must not have body |

  Rule: Decision block 可巢狀於 BRANCH body 內，深度無限

    # 巢狀 DECISION（DECISION 在 BRANCH 內部）
    Example: 巢狀 DECISION decode（DECISION 在 BRANCH 內部）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 訂單檢查
        [ACTOR] 使用者

        [DECISION:2a] 訂單有效
          [BRANCH:2a:有效]
            [STEP:2a.1] @使用者 {specs/ui/確認.md}
            [DECISION:2a1] 使用優惠券
              [BRANCH:2a1:是]
                [STEP:2a1.1] @使用者 {specs/commands/套用.feature}
              [BRANCH:2a1:否]
                [STEP:2a1.2] @使用者 {specs/ui/原價.md}
            [MERGE:2a1]
          [BRANCH:2a:無效]
            [STEP:2a.2] @使用者 {specs/ui/錯誤.md}
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "2a",
              "type": "decision",
              "paths": [
                {
                  "guard": "有效",
                  "firstNodeId": "$step2a1"
                },
                {
                  "guard": "無效",
                  "firstNodeId": "$step2a2"
                }
              ]
            },
            {
              "id": ">step2a1",
              "displayId": "2a.1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "bindsFeature": "specs/ui/確認.md",
              "next": "$decision2a1"
            },
            {
              "id": ">decision2a1",
              "displayId": "2a1",
              "type": "decision",
              "paths": [
                {
                  "guard": "是",
                  "firstNodeId": "$step2a11"
                },
                {
                  "guard": "否",
                  "firstNodeId": "$step2a12"
                }
              ]
            },
            {
              "id": ">step2a11",
              "displayId": "2a1.1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "bindsFeature": "specs/commands/套用.feature",
              "next": "$merge2a1"
            },
            {
              "id": ">step2a12",
              "displayId": "2a1.2",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "bindsFeature": "specs/ui/原價.md",
              "next": "$merge2a1"
            },
            {
              "id": ">merge2a1",
              "displayId": "2a1",
              "type": "merge",
              "next": "$merge2a"
            },
            {
              "id": ">step2a2",
              "displayId": "2a.2",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "bindsFeature": "specs/ui/錯誤.md",
              "next": "$merge2a"
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge",
              "next": "$final0"
            }
          ]
        }
        """

    Example: [BRANCH] body 內連續多個 [STEP] decode（以 next 鏈接到 MERGE）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 多步分支
        [ACTOR] 使用者
        [ACTOR] 系統

        [DECISION:1a] 條件
          [BRANCH:1a:路徑甲]
            [STEP:1a.1] @使用者 第一步
            [STEP:1a.2] @系統 第二步 {specs/commands/b.feature}
          [BRANCH:1a:路徑乙]
            [STEP:1a.3] @使用者 單步
        [MERGE:1a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "1a",
              "type": "decision",
              "paths": [
                {
                  "guard": "路徑甲",
                  "firstNodeId": "$step1a1"
                },
                {
                  "guard": "路徑乙",
                  "firstNodeId": "$step1a3"
                }
              ]
            },
            {
              "id": ">step1a1",
              "displayId": "1a.1",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "第一步",
              "next": "$step1a2"
            },
            {
              "id": ">step1a2",
              "displayId": "1a.2",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "第二步",
              "bindsFeature": "specs/commands/b.feature",
              "next": "$merge1a"
            },
            {
              "id": ">step1a3",
              "displayId": "1a.3",
              "type": "ui_step",
              "actorId": "actor:使用者",
              "name": "單步",
              "next": "$merge1a"
            },
            {
              "id": ">merge1a",
              "displayId": "1a",
              "type": "merge",
              "next": "$final0"
            }
          ]
        }
        """

  # ─── Fork block ──────────────────────────────────────────────

  Rule: [FORK:N] 開啟一個平行區塊；所有 [PARALLEL:N] 都屬於它，且 PARALLEL 只開 path 容器，工作內容必須寫在 body；[JOIN:N] 則是這個平行區塊的收尾，lower 後會成為 join node。

    Example: [FORK] + [PARALLEL] + [JOIN] decode 成 Fork node 帶 paths
      Given 以下 activity 內容:
        """
        [ACTIVITY] 平行作業
        [ACTOR] 系統

        [FORK:3a]
          [PARALLEL:3a]
            [STEP:3a.1] @系統 {specs/commands/a.feature}
          [PARALLEL:3a]
            [STEP:3a.2] @系統 {specs/commands/b.feature}
        [JOIN:3a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "3a",
              "type": "fork",
              "paths": [
                {
                  "firstNodeId": "$step3a1"
                },
                {
                  "firstNodeId": "$step3a2"
                }
              ]
            },
            {
              "id": ">step3a1",
              "displayId": "3a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/commands/a.feature",
              "next": "$join3a"
            },
            {
              "id": ">step3a2",
              "displayId": "3a.2",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/commands/b.feature",
              "next": "$join3a"
            },
            {
              "id": ">join3a",
              "displayId": "3a",
              "type": "join",
              "next": "$final0"
            }
          ]
        }
        """

    Example: [PARALLEL] 同一 lane 內連續多個 [STEP] decode（以 next 鏈接到 JOIN）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 平行多步
        [ACTOR] 系統

        [FORK:3a]
          [PARALLEL:3a]
            [STEP:3a.1] @系統 先做
            [STEP:3a.2] @系統 {specs/commands/batch.feature}
          [PARALLEL:3a]
            [STEP:3a.3] @系統 {specs/commands/solo.feature}
        [JOIN:3a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "3a",
              "type": "fork",
              "paths": [
                {
                  "firstNodeId": "$step3a1"
                },
                {
                  "firstNodeId": "$step3a3"
                }
              ]
            },
            {
              "id": ">step3a1",
              "displayId": "3a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "先做",
              "next": "$step3a2"
            },
            {
              "id": ">step3a2",
              "displayId": "3a.2",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/commands/batch.feature",
              "next": "$join3a"
            },
            {
              "id": ">step3a3",
              "displayId": "3a.3",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/commands/solo.feature",
              "next": "$join3a"
            },
            {
              "id": ">join3a",
              "displayId": "3a",
              "type": "join",
              "next": "$final0"
            }
          ]
        }
        """

  Rule: Fork block 可巢狀於 BRANCH body 內

    # FORK inside BRANCH
    Example: FORK inside BRANCH decode（FORK 在 BRANCH 內部）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 訂單處理
        [ACTOR] 系統

        [DECISION:2a] 訂單有效
          [BRANCH:2a:有效]
            [FORK:3a]
              [PARALLEL:3a]
                [STEP:3a.1] @系統 平行分支一
              [PARALLEL:3a]
                [STEP:3a.2] @系統 平行分支二
            [JOIN:3a]
          [BRANCH:2a:無效]
            [STEP:2a.1] @系統 {specs/ui/錯誤.md}
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 成功，activity 至少包含:
        """
        {
          "finalNodes": [
            { "id": ">final0" }
          ],
          "nodes": [
            {
              "displayId": "2a",
              "type": "decision",
              "paths": [
                {
                  "guard": "有效",
                  "firstNodeId": "$fork3a"
                },
                {
                  "guard": "無效",
                  "firstNodeId": "$step2a1"
                }
              ]
            },
            {
              "id": ">fork3a",
              "displayId": "3a",
              "type": "fork",
              "paths": [
                {
                  "firstNodeId": "$step3a1"
                },
                {
                  "firstNodeId": "$step3a2"
                }
              ]
            },
            {
              "id": ">step3a1",
              "displayId": "3a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "平行分支一",
              "next": "$join3a"
            },
            {
              "id": ">step3a2",
              "displayId": "3a.2",
              "type": "ui_step",
              "actorId": "actor:系統",
              "name": "平行分支二",
              "next": "$join3a"
            },
            {
              "id": ">join3a",
              "displayId": "3a",
              "type": "join",
              "next": "$merge2a"
            },
            {
              "id": ">step2a1",
              "displayId": "2a.1",
              "type": "ui_step",
              "actorId": "actor:系統",
              "bindsFeature": "specs/ui/錯誤.md",
              "next": "$merge2a"
            },
            {
              "id": ">merge2a",
              "displayId": "2a",
              "type": "merge",
              "next": "$final0"
            }
          ]
        }
        """

  # ─── 已淘汰 / 禁用語法 ───

  Rule: 任何 tag 帶 `{id:<nanoid>}` 後綴 → ParseError（nanoid 由 GraphDriver 自動產生，不出現在 DSL string content）

    Example: [STEP] 帶 {id:<nanoid>} 後綴 → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 業務

        [STEP:1] @業務 發起登入 {id:sr1VjvTd}
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                     |
        | 4    | Inline {id:...} not allowed: ids are managed by GraphDriver |

  Rule: [BRANCH] header 只允許容器語法；inline payload 應改成巢狀 [STEP] / [FINAL]

    Example: [BRANCH] 帶 inline payload 後綴 → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 驗證
        [ACTOR] 使用者

        [DECISION:2a] 是否有效
          [BRANCH:2a:有效] @使用者 顯示結果 {specs/ui/result.md}
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                                  |
        | 5    | Legacy BRANCH inline payload not allowed: move work to nested STEP/FINAL |

  Rule: [PARALLEL] header 只允許容器語法；inline payload 應改成巢狀 [STEP] / nested gateway

    Example: [PARALLEL] 帶 inline payload 後綴 → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 平行作業
        [ACTOR] 系統

        [FORK:3a]
          [PARALLEL:3a] @系統 寫入紀錄
        [JOIN:3a]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                                    |
        | 5    | Legacy PARALLEL inline payload not allowed: move work to nested STEP/FINAL |

  Rule: [STEP] 的 `-> {<path>}` 為歷史語法，應改用 `{<path>}`

    Example: [STEP] 帶 `-> {<path>}` 後綴 → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 使用者

        [STEP:1] @使用者 登入 -> {api/auth/login.json}
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                |
        | 4    | Legacy STEP binding syntax not allowed: use {path} |

  # ─── 引用合法性（Cross-reference invariants）─────────────────
  # 用途：DSL 中的 [STEP] `@<actor>` 與 [BRANCH] `-> <target>` 等跨節點引用，
  # 必須對應到實際的 [ACTOR] 宣告 / 既有 node displayId；否則 decoder 應 fail-stop 阻止
  # dangling reference 進入 aggregate。

  Rule: [STEP] 的 `@<actor>` 引用名必須先被 [ACTOR] 宣告，否則 ParseError

    Example: [STEP] @<actor> 引用未宣告 actor → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 登入
        [ACTOR] 業務

        [STEP:1] @不存在的人 動作
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                |
        | 4    | Unknown actor reference: 不存在的人 |

  Rule: [BRANCH:N:guard -> <target>] 的 `<target>` 必須是某 node 的 displayId，否則 ParseError

    Example: [BRANCH] loopBackTarget 指向不存在 node → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] 重試流程
        [ACTOR] 使用者

        [STEP:1] @使用者 輸入
        [DECISION:2a] 是否成功
          [BRANCH:2a:成功]
          [BRANCH:2a:失敗 -> 99]
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                            |
        | 7    | BRANCH target does not exist: 99 |

  # ─── 唯一性（Uniqueness invariants）──────────────────────────
  # 用途：避免同一檔案內同一 namespace 的識別符（actor name、step/decision/fork displayId、
  # 同 decision 下的 guard）被重複宣告，否則下游 aggregate 會把不同 node 撞同一 stable id 或
  # 把 dangling reference 解到「最後一個 wins」上，造成 silent corruption。

  Rule: 同一檔案內 [ACTOR] 的 name 不可重複，否則 ParseError

    Example: 重複宣告 [ACTOR] → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] 客戶
        [ACTOR] 客戶
        [INITIAL]
        [STEP:1] @客戶 動作
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                       |
        | 3    | Duplicate actor name: '客戶' |

  Rule: [STEP:<id>] 的 displayId 不可重複，否則 ParseError

    Example: 重複 [STEP] displayId → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A 一
        [STEP:1] @A 二
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                  |
        | 5    | Duplicate STEP id: '1' |

  Rule: [DECISION:<id>] 的 displayId 不可重複，否則 ParseError

    Example: 重複 [DECISION] displayId → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [DECISION:2a] c1
          [BRANCH:2a:g]
        [MERGE:2a]
        [DECISION:2a] c2
          [BRANCH:2a:g]
        [MERGE:2a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                       |
        | 7    | Duplicate DECISION id: '2a' |

  Rule: [FORK:<id>] 的 displayId 不可重複，否則 ParseError

    Example: 重複 [FORK] displayId → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [FORK:3a]
          [PARALLEL:3a]
            [STEP:3a.1] @A x
        [JOIN:3a]
        [FORK:3a]
          [PARALLEL:3a]
            [STEP:3a.2] @A y
        [JOIN:3a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                   |
        | 8    | Duplicate FORK id: '3a' |

  Rule: 同一 [DECISION] 內 [BRANCH] 的 guard 不可重複，否則 ParseError

    Example: 同一 decision 內出現重複 guard → ParseError
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x
        [DECISION:2a] c
          [BRANCH:2a:g]
          [BRANCH:2a:g]
        [MERGE:2a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                     |
        | 7    | Duplicate guard 'g' in decision '2a'      |

  # ─── 結構平衡（Structural balance invariants）─────────────────
  # 用途：DECISION/FORK 必須有對應 closer ([MERGE]/[JOIN])；BRANCH/MERGE/PARALLEL/JOIN
  # 不得脫離 opener 出現在 top-level；top-level [FINAL] 為終止符，之後只能再接 [FINAL]。

  Rule: top-level 出現孤兒 closer ([BRANCH] / [MERGE] / [PARALLEL] / [JOIN]) → ParseError

    Example: 孤兒 [BRANCH] → Unmatched branch
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [BRANCH:2a:g]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                              |
        | 4    | Unmatched branch: no DECISION '2a' |

    Example: 孤兒 [MERGE] → Unmatched merge
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [MERGE:2a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                            |
        | 4    | Unmatched merge: no DECISION '2a' |

    Example: 孤兒 [PARALLEL] → Unmatched parallel
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [PARALLEL:3a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                              |
        | 4    | Unmatched parallel: no FORK '3a' |

    Example: 孤兒 [JOIN] → Unmatched join
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [JOIN:3a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                          |
        | 4    | Unmatched join: no FORK '3a'   |

  Rule: [DECISION] / [FORK] 必須有對應 closer ([MERGE] / [JOIN])，否則 ParseError

    Example: [DECISION] 無 [MERGE] 收尾 → Unclosed decision
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [DECISION:2a] c
          [BRANCH:2a:g]
            [STEP:2a.1] @A x
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                       |
        | 4    | Unclosed decision: '2a'    |

    Example: [FORK] 無 [JOIN] 收尾 → Unclosed fork
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [FORK:3a]
          [PARALLEL:3a]
            [STEP:3a.1] @A x
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                  |
        | 4    | Unclosed fork: '3a'    |

  Rule: top-level [FINAL] 為流程終止符；其後只能再出現 [FINAL]，否則 ParseError

    Example: top-level [FINAL] 後接非 FINAL tag → Content after [FINAL]
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A 一
        [FINAL]
        [STEP:2] @A 二
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                |
        | 6    | Content after [FINAL] |

  # ─── strict surface（禁止 STEP 尾端垃圾、禁止縮排裸字、tag 行不得夾帶尾段）──

  Rule: [STEP] 僅允許「@actor + 可選描述 + 可選單一尾端 {binding}」；`}` 後不得再有字元；不得出現第二組 `{...}`；
    不得殘留 `->`；禁止以縮排延續行夾帶裸字。
    根 flow 與巢狀區塊亦不得出現非 tag 的裸字根行。
    `[INITIAL]` / `[FINAL]` / `[MERGE]` / `[FORK]` / `[JOIN]` 整行必須精確匹配語法，不可在 tag 尾端加字。

    Example: [STEP] 於 {binding} 後同一行再帶尾字（codec 嚴格尾端）
      Given 以下 activity 內容:
        """
        [ACTIVITY] 刻意無效的活動圖範例
        [ACTOR] 測試 -> {specs/actors/系統.md}

        [INITIAL]
        [STEP:1] @測試 {specs/commands/提交訂單.feature} adsas
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                           |
        | 5    | Unexpected trailing content after binding: 'adsas' |

    Example: [STEP] 下一行為無縮排裸字（非 tag）→ Unexpected content
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A

        [INITIAL]
        [STEP:1] @A {specs/a.feature}
        orphan
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                          |
        | 6    | Unexpected content: 'orphan' |

    Example: [STEP] 下一行為縮排裸字（禁止延續行夾字）→ Unexpected indented free text
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A

        [INITIAL]
        [STEP:1] @A {specs/a.feature}
          junk
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                  |
        | 6    | Unexpected indented free text: 'junk' |

    Example: [ACTIVITY] 與 [INITIAL] 之間出現根層裸字行
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        stray-root
        [INITIAL]
        [STEP:1] @A x
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                              |
        | 3    | Unexpected content: 'stray-root' |

    Example: [INITIAL] 行尾不得夾帶額外字元
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL] extra
        [STEP:1] @A x
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                      |
        | 3    | Unexpected content: '[INITIAL] extra' |

    Example: [FINAL] 行尾不得夾帶額外字元
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x
        [FINAL] extra
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                    |
        | 5    | Unexpected content: '[FINAL] extra' |

    Example: [STEP] 含兩組尾端 {binding} → 僅允許一組
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A {specs/a.feature} {specs/b.feature}
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                   |
        | 4    | Only one trailing '{binding}' suffix allowed in STEP |

    Example: [STEP] binding 大括號未閉合
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A {broken
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                  |
        | 4    | Malformed or unclosed '{binding}' in STEP |

    Example: [STEP] 同一行 legacy `-> {path}` 後仍帶尾字
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x -> {api/x.json} tail
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                            |
        | 4    | Unexpected "->" in STEP content |

    Example: [ACTOR] 於 `-> {binding}` 後同一行再帶尾字 → Actor missing name
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] 測試 -> {specs/actors/系統.md} tail
        [INITIAL]
        [STEP:1] @測試 x
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message             |
        | 2    | Actor missing name |

    Example: [BRANCH] 行尾於 guard 後帶尾字（視為 legacy inline payload）
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x
        [DECISION:2a] c
          [BRANCH:2a:g] tail
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                                  |
        | 6    | Legacy BRANCH inline payload not allowed: move work to nested STEP/FINAL |

    Example: [BRANCH] loop_back 目標後仍帶尾字 → legacy inline payload
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x
        [DECISION:2a] c
          [BRANCH:2a:g -> 1] junk
        [MERGE:2a]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                                  |
        | 6    | Legacy BRANCH inline payload not allowed: move work to nested STEP/FINAL |

    Example: decision 區塊內僅縮排裸字（無巢狀 tag）→ Unexpected indented free text
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x
        [DECISION:2a] c
          [BRANCH:2a:g]
            only-text
        [MERGE:2a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                       |
        | 7    | Unexpected indented free text: 'only-text' |

    Example: [MERGE] 行尾夾帶額外字元
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [STEP:1] @A x
        [DECISION:2a] c
          [BRANCH:2a:g]
            [STEP:2a.1] @A y
        [MERGE:2a] bad
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                |
        | 8    | Unexpected content: '[MERGE:2a] bad' |

    Example: [FORK] 行尾夾帶額外字元
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [FORK:3a] bad
          [PARALLEL:3a]
            [STEP:3a.1] @A x
        [JOIN:3a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                              |
        | 4    | Unexpected content: '[FORK:3a] bad' |

    Example: [JOIN] 行尾夾帶額外字元
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [FORK:3a]
          [PARALLEL:3a]
            [STEP:3a.1] @A x
        [JOIN:3a] bad
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                              |
        | 7    | Unexpected content: '[JOIN:3a] bad' |

    Example: FORK 區塊內 PARALLEL 下僅縮排裸字 → Unexpected indented free text
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [FORK:3a]
          [PARALLEL:3a]
            stray-parallel-body
        [JOIN:3a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                |
        | 6    | Unexpected indented free text: 'stray-parallel-body' |

    Example: [PARALLEL] 行尾夾帶額外字元 → legacy inline payload
      Given 以下 activity 內容:
        """
        [ACTIVITY] X
        [ACTOR] A
        [INITIAL]
        [FORK:3a]
          [PARALLEL:3a] tail
            [STEP:3a.1] @A x
        [JOIN:3a]
        [FINAL]
        """
      When 執行 decode
      Then decode 失敗，ParseError 為:
        | line | message                                                                    |
        | 5    | Legacy PARALLEL inline payload not allowed: move work to nested STEP/FINAL |
