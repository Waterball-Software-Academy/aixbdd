# 角色 + 入口契約

> 純 declarative reference。定義 caller payload schema 與角色邊界。
>
> 來源：原 SKILL.md `## §1 角色` + `## §2 入口契約`。

## §1 角色定位

Formulation skill。綁定 DSL = `.activity`（扁平事件流）。被 `aibdd-discovery` DELEGATE；只把上游 `activity_analysis.activity` 中的 modeling elements 翻譯成 artifact，不自行重新分析需求、不檢查顆粒度、不新增 Actor / Action / Decision / Fork。

## §2 入口契約 — 推理包 schema

| 項目 | 內容 |
|---|---|
| `activity_analysis.activity.name` | Activity 名稱 |
| `activity_analysis.activity.id` | Activity stable id |
| `activity_analysis.activity.initial` | Initial element |
| `activity_analysis.activity.finals[]` | Final elements |
| `activity_analysis.activity.actors[]` | Actor elements |
| `activity_analysis.activity.nodes[]` | Action / Decision / Fork / Merge / Join elements |
| `activity_analysis.graph_gaps[]` | 上游記錄的建模 gap；本 skill 不補 gap |
| `activity_analysis.exit_status` | `complete` 或 `blocked` |
| `target_path` | Planner 指定的輸出路徑（**必須**為 kickoff 展開後之 `${ACTIVITIES_DIR}/<name>.activity` 的絕對或專案相對路徑）|
| `format` | `.activity`（扁平事件流）|
| `mode` | 可選；`overwrite` 時允許覆蓋既有 `target_path` |

## §3 缺項處理

推理包不完整、`activity_analysis.activity` 缺失、或 `target_path` 未指定時，skill 只回傳 caller misuse 訊號；不得自行補 Activity flow、Actor、Action、Decision、Fork、或 target path。

## §4 上游責任邊界

- `self-contained`、phase-slice merge、feature-index anti-pattern、以及 branch terminal 完整性屬於上游 `/aibdd-discovery` 的建模責任。
- 本 skill **不得**因為看起來流程不完整就自行補 STEP、補 branch target、補 terminal feature。
- 若 caller payload 顯示此 Activity 尚未建模完成（例如 `exit_status != complete` 或 `graph_gaps[]` 非空），本 skill 必須拒絕落檔，而不是把半成品翻譯成 `.activity` artifact。
