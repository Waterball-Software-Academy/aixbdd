# SOP

本 sub-SOP 依 `$decisions`（由 `01-ask-config/` 推得）TRIGGER 純複製 script，再以 LLM Edit 後處理：append per-stack tail + 填入 `${KICKOFF_*}` placeholder + 對 user 改過預設的值做條件式 grep-replace。最後清理 `${PLAN_PATH}`。

## Stack 查表（step 7、step 8 依此填值）

| `$decisions.stack` | tail dir | `$role` | `$type` | `$preset_kind` | `$description_suffix`（接於 `<tlb_id> ` 之後） |
|---|---|---|---|---|---|
| `python_e2e` | `python-e2e` | `backend` | `web-service` | `web-service` | `Python FastAPI backend service` |
| `java_e2e` | `java-e2e` | `backend` | `web-service` | `web-service` | `Java Spring Boot backend service` |
| `nextjs_playwright` | `nextjs-playwright` | `frontend` | `web-app` | `web-frontend` | `Next.js + Playwright frontend application` |

## Steps

1. DERIVE `$decisions_json` ← JSON-serialize `$decisions` 加上 `project_root: ${PROJECT_ROOT}`、`boundary_codebase_subdir`（缺則 `""`）、`stack: $decisions.stack`。

2. WRITE `${PROJECT_ROOT}/.aibdd-kickoff-decisions.json` ← `$decisions_json`。**本步僅允許 WRITE 此暫存檔**。

3. TRIGGER `python3 ../assets/scripts/kickoff_layout.py --decisions-file ${PROJECT_ROOT}/.aibdd-kickoff-decisions.json` → `$result_json`。**ASSERT** `$result_json.ok == true`，否則向 user 轉述錯誤並 STOP。

4. DELETE `${PROJECT_ROOT}/.aibdd-kickoff-decisions.json`。

5. DERIVE `$dst` ← `$result_json.boundary_codebase_root`。
   DERIVE `$shared_dsl_path` ← `$result_json.shared_dsl_path`。

6. DERIVE `$tlb_id` ← `$decisions.tlb_id`（缺則 `"backend"`）。 從 Stack 查表取 `$role` / `$type` / `$description_suffix`，組 `$description = "${tlb_id} ${description_suffix}"`。

7. READ `../assets/templates/per-stack/<tail_dir>/arguments.tail.yml`（依查表取 `tail_dir`） → `$tail`。

8. APPEND `$tail` 至 `${dst}/.aibdd/arguments.yml` 末尾（Read + Write 整檔 = 原檔 + `"\n"` + `$tail`）。**本步僅允許 UPDATE `${dst}/.aibdd/arguments.yml`**。

9. **永遠執行** — 填 `${KICKOFF_TLB_ID}` placeholder。對下列 3 檔各做 Edit（`replace_all=true`，將 `${KICKOFF_TLB_ID}` 換成 `$tlb_id`）：
   - `${dst}/.aibdd/arguments.yml`（java/nextjs 的 tail 引用到）
   - `${dst}/specs/architecture/boundary.yml`
   - `${dst}/specs/architecture/component-diagram.class.mmd`

10. **永遠執行** — 填 boundary placeholder。Edit `${dst}/specs/architecture/boundary.yml`：
    - `${KICKOFF_BOUNDARY_ROLE}` → `$role`
    - `${KICKOFF_BOUNDARY_TYPE}` → `$type`
    - `${KICKOFF_BOUNDARY_DESCRIPTION}` → `$description`

11. **永遠執行** — 填 diagram placeholder。Edit `${dst}/specs/architecture/component-diagram.class.mmd`：
    - `${KICKOFF_BOUNDARY_TYPE}` → `$type` 並把 `-` 全部替換為 `_`（Mermaid `<<...>>` annotation 只接受 `[A-Za-z0-9_]+`，連字符會觸發 parse error；boundary.yml 端不受此規則影響，維持原 hyphen 寫法）。

12. IF `$decisions.stack == java_e2e`：
    DERIVE `$base_package`：
    - IF `$decisions.base_package` 已提供 → 用該值。
    - ELSE → `$base_package = "com.example.${tlb_id_without_hyphens}"`（例：`course-api` → `com.example.courseapi`）。
    Edit `${dst}/.aibdd/arguments.yml`：`${KICKOFF_BASE_PACKAGE}` → `$base_package`。

13. IF `$decisions.project_spec_language != "zh-hant"`：
    Edit `${dst}/.aibdd/arguments.yml`：`PROJECT_SPEC_LANGUAGE: zh-hant` → `PROJECT_SPEC_LANGUAGE: ${$decisions.project_spec_language}`。
    （兩個 `_LANGUAGE_REF` 路徑用 yaml-internal ref `${PROJECT_SPEC_LANGUAGE}` 自動跟著解析，**不需**另改。）

14. IF `$decisions.boundary_codebase_subdir != ""`：
    Edit `${dst}/.aibdd/arguments.yml`：`BOUNDARY_CODEBASE_SUBDIR: ''` → `BOUNDARY_CODEBASE_SUBDIR: '${$decisions.boundary_codebase_subdir}'`。

15. **ASSERT** `${dst}/.aibdd/arguments.yml`、`boundary.yml`、`component-diagram.class.mmd` 三檔**全部不含** `${KICKOFF_` 子字串（grep 結果為空）。若有殘留 → 向 user 告知殘留位置並 STOP。

16. **ASSERT** `$shared_dsl_path` 存在。

17. IF path_exists(`${PLAN_PATH}`) → DELETE `${PLAN_PATH}`（清理 File First 暫存檔）。

18. 向 user 說道（`{artifact_list}` = 列出 `${dst}` 下產出的 10 個 artifact 的 bullet 清單，含 `${shared_dsl_path}`）：

    ```text
    Kickoff 已完成。

    已建立：
    {artifact_list}

    下一步，來建立專案骨架吧，請直接使用 /aibdd-auto-starter，或是告訴我「繼續」。
    ```

    END Sub-SOP。
