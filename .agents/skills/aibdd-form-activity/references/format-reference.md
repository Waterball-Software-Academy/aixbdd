# Activity Element → `.activity` Syntax (Compact)

> SSOT: `packages/core/src/services/activity/{DslTokenizerService,DslParserService,DslSerializerService,AstValidatorService}.ts`。本文只負責 mapping；顆粒度 / Actor 合法性 / reuse / partition 不在本 skill 判斷。

## Grammar (EBNF)

`?` = 0 或 1，`*` = 0 或 N，`+` = 1 或 N。每條 production 一行對應一個檔案中的單行 token。

```ebnf
file          = activity actor* initial body final+

activity      = "[ACTIVITY]" name
actor         = "[ACTOR]" name ( "->" "{" binding "}" )?
initial       = "[INITIAL]"
final         = "[FINAL]"

body          = node*
node          = step | decisionBlock | forkBlock

step          = "[STEP:" id "]" actorRef description? ( "{" binding "}" )?

decisionBlock = decision branch+ merge
decision      = "[DECISION:" id "]" condition
branch        = "[BRANCH:" id ":" guard ( "->" loopTargetId )? "]"
                body                          (* nested — 可再巢狀 decisionBlock / forkBlock *)
merge         = "[MERGE:" id "]"

forkBlock     = fork parallel+ join
fork          = "[FORK:" id "]"
parallel      = "[PARALLEL:" id "]"
                body                          (* nested *)
join          = "[JOIN:" id "]"

actorRef      = "@" ( bareName | "\"" quotedName "\"" )
guard         = "else" | text                 (* "else" 保留字；text 不得含 " -> " *)
id            = ( letter | digit ) ( letter | digit | "." | "-" )*
```

**Context-sensitive side-conditions**（CFG 表達不到，必須額外滿足）：

1. `decisionBlock` 中的 `decision` / `branch+` / `merge` **共用同一 `id`**（例：`DECISION:2a` 配 `BRANCH:2a:*` 配 `MERGE:2a`）。
2. `forkBlock` 中的 `fork` / `parallel+` / `join` **共用同一 `id`**。
3. `branch.body` / `parallel.body` 可再內含 `decisionBlock` / `forkBlock`，**巢狀深度無限**；nested gateway 用獨立 `id` 區分（例：外層 `2a` 內可開 `2a1`、`2a1a`…）。
4. `branch.loopTargetId` 必須指向 file 內某個已存在 node 的 `id`。
5. 若 `branch.loopTargetId` 存在，則 `branch.body` 必須為空；此 branch 不再有 `firstNodeId`。
6. `actor` 的 `bareName` 必須對應某個 `[ACTOR]` 宣告的 `name`。
7. `step` 的 `actorRef` 必填；`branch` / `parallel` header 不可帶 inline payload。

**強制必有**：`[ACTIVITY]`（恰 1）、`[INITIAL]`（恰 1）、`[FINAL]`（≥1）。`[ACTOR]` 為 0..N。行首縮排純視覺、無語意。

## Element Mapping

| Element | `.activity` line | 必填 / 省略規則 |
|---|---|---|
| Activity | `[ACTIVITY] <name>` | **必填、僅一次** |
| Actor | `[ACTOR] <name> -> {<binding>}` | `binding` 空 → 省略 ` -> {…}` |
| Initial | `[INITIAL]` | **必填、僅一次** |
| Action (`ui_step` / `command` / `query`) | `[STEP:<id>] @<actor> <description> {<binds_feature>}` | `actor` **必填**；`description` / `binding` 空 → 對應片段省略；`action_type` 不輸出 |
| Decision | `[DECISION:<id>] <condition>` | — |
| Decision path | `[BRANCH:<decision-id>:<guard>]` | 純容器；若有工作內容，必須在下一行縮排寫 `[STEP]` / `[FINAL]` / nested gateway；`loop_back_target` 存在時 → `[BRANCH:id:<guard> -> <target-display-id>]`，且 body 必須為空 |
| Merge | `[MERGE:<id>]` | — |
| Fork | `[FORK:<id>]` | — |
| Fork path | `[PARALLEL:<id>]` | 純容器；若有工作內容，必須在下一行縮排寫 `[STEP]` / nested gateway |
| Join | `[JOIN:<id>]` | — |
| Final | `[FINAL]` | **必填、至少一次** |

`actor` 必須 resolve 成 `Activity.actors[].id`；含空白或 `"` → quoted form `@"姓 名"`（escape `\"` `\\`），純文字 → `@Actor1` 直接寫。

## Syntax Constraints

- 違反上方 Grammar 任一 production 或 side-condition → syntax error。
- 不輸出 Mermaid / flowchart 描述、不輸出任何註解。

## Example

```text
[ACTIVITY] 訂單處理
[ACTOR] 客戶 -> {actors/客戶.md}
[ACTOR] "客服 主管"

[INITIAL]
[STEP:1] @客戶 提交訂單 {commands/submit.feature}
[DECISION:2a] 訂單是否有效
  [BRANCH:2a:有效]
    [STEP:2] @客戶 {ui/confirm.md}
    [STEP:3] @系統 驗證
  [BRANCH:2a:無效 -> 1]
    [STEP:4] @"客服 主管" {ui/error.md}
  [BRANCH:2a:else]
    [FINAL]
[MERGE:2a]

[FORK:3a]
  [PARALLEL:3a]
    [STEP:5] @金流 {commands/charge.feature}
  [PARALLEL:3a]
    [STEP:6] @系統 {commands/notify.feature}
[JOIN:3a]
[FINAL]
```
