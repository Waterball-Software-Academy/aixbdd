---
name: mono-repo-docker-compose-setup
description: Mono-repo Docker compose setup. 偵測 frontend / backend 子資料夾與 stack 特徵後生成 root docker-compose.yml + 兩份 Dockerfile + .dockerignore；接著並行 spawn 兩條 subagent (backend / frontend) 各自 build/up + curl 驗證直到 HTTP 200，否則由 subagent 自行修補（Dockerfile / compose / 程式碼），每條最多 5 次迭代。TRIGGER when user 下 /mono-repo-docker-compose-setup、要把 monorepo 容器化並冒煙、或請求一鍵生成 fullstack docker compose。SKIP when 不是 monorepo（沒有 frontend/backend 子資料夾）、user 只要 single-service Dockerfile、或要做 production deploy spec 而非 dev compose。
metadata:
  user-invocable: true
  source: project-level
---

# mono-repo-docker-compose-setup

把一個含 `frontend/` + `backend/` 雙 boundary 的 monorepo 自動容器化：偵測 stack → 生成
docker-compose.yml + 兩份 Dockerfile + .dockerignore → 並行兩條 subagent 各自 build / up /
curl 驗證直到 HTTP 200。

> **Program-like SKILL.md — self-contained notation**
>
> **3 verb classes**:
> - **D** = Deterministic — no LLM judgment required
> - **S** = Semantic — LLM reasoning required
> - **I** = Interactive — yields turn to user
>
> **SSA bindings**: `$x = VERB args`（單 phase）；`$$x` 跨 phase（在 phase header `> produces:` 宣告）。
>
> **Side effect**: `VERB target ← $payload` — `←` 表示 write into target。
>
> **Control flow**: `BRANCH $check ? then : else`（binary）或縮排多臂；`GOTO #N.M` 跳 Phase N step M。
>
> **常用 verbs**: READ / WRITE / CREATE / DELETE / COMPUTE / DERIVE / PARSE / RENDER / ASSERT / MATCH /
> TRIGGER / DELEGATE / MARK / BRANCH / GOTO / IF / LOOP / RETURN / STOP / EMIT / WAIT / THINK /
> CLASSIFY / JUDGE / DECIDE / DRAFT / EDIT / ASK（Interactive）。

## §1 REFERENCES

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `references/stack-detection-cheatsheet.md` | Phase 1 | 從 pyproject.toml / package.json / alembic.ini / next.config.mjs 推 stack 與運行命令 |
| R2 | `references/subagent-prompt-templates.md` | Phase 4 | 兩條 subagent 的 prompt 樣板（backend / frontend）含迭代規則與通過條件 |
| R3 | `references/iteration-budget.md` | Phase 4 | 每條 subagent 最多 5 次迭代、總時長軟上限與 fail-stop 條件 |
| R4 | `assets/templates/docker-compose.yml.tmpl` | Phase 3 | root compose 樣板（postgres + backend + frontend）|
| R5 | `assets/templates/Dockerfile.python-fastapi.tmpl` | Phase 3 | Python multi-stage Dockerfile |
| R6 | `assets/templates/Dockerfile.next-standalone.tmpl` | Phase 3 | Next.js standalone multi-stage Dockerfile |
| R7 | `assets/templates/.dockerignore.python.tmpl` | Phase 3 | backend .dockerignore |
| R8 | `assets/templates/.dockerignore.node.tmpl` | Phase 3 | frontend .dockerignore |

## §2 SOP

### Phase 1 — DETECT mono-repo + stack
> produces: `$$repo_root`, `$$backend_dir`, `$$frontend_dir`, `$$backend_stack`, `$$frontend_stack`, `$$db_kind`, `$$backend_port`, `$$frontend_port`, `$$health_path`

1. `$$repo_root` = COMPUTE current workspace git toplevel（`git rev-parse --show-toplevel`）
2. ASSERT `$$repo_root` 為 git repository
   1.1 IF assertion fails: EMIT "需要在 git repository 內執行" to user; STOP
3. `$$backend_dir` = MATCH 子資料夾 `${$$repo_root}/backend`
4. `$$frontend_dir` = MATCH 子資料夾 `${$$repo_root}/frontend`
5. ASSERT 兩個資料夾皆存在
   1.2 IF assertion fails: EMIT "需要 monorepo 結構（同時擁有 backend/ 與 frontend/ 子資料夾）" to user; STOP
6. `$be_signals` = READ `${$$backend_dir}/{pyproject.toml,requirements.txt,alembic.ini,package.json,go.mod,Cargo.toml}`（best-effort，缺少視為 null）
7. `$fe_signals` = READ `${$$frontend_dir}/{package.json,next.config.mjs,next.config.js,vite.config.ts,vite.config.js}`（best-effort）
8. `$$backend_stack` = CLASSIFY `$be_signals` 依 R1 → 一個值 `python-fastapi | python-django | node-express | unknown`
9. `$$frontend_stack` = CLASSIFY `$fe_signals` 依 R1 → 一個值 `next-standalone | next-default | vite-react | unknown`
10. `$$db_kind` = CLASSIFY backend persistence signals 依 R1 → 一個值 `postgres | mysql | sqlite | none`
11. `$$backend_port` = DERIVE 依 R1（python-fastapi 預設 8000；fallback 由 user 補）
12. `$$frontend_port` = DERIVE 依 R1（Next.js 預設 3001；fallback 由 user 補）
13. `$$health_path` = DERIVE backend health endpoint（FastAPI 預設 `/health`；fallback `/`）
14. BRANCH `$$backend_stack == "unknown" || $$frontend_stack == "unknown" || $$db_kind == "none"`?
    14.1 ASK user via AskUserQuestion 補齊未知欄位（stack / db_kind / port / health_path）
    14.2 BIND user answers into the corresponding `$$` slots
    14.3 GOTO #2.1
    14.4 ELSE: GOTO #2.1

### Phase 2 — GUARD existing artifacts
> produces: `$$compose_action`, `$$be_dockerfile_action`, `$$fe_dockerfile_action`, `$$be_dockerignore_action`, `$$fe_dockerignore_action`

1. `$compose_path` = COMPUTE `${$$repo_root}/docker-compose.yml`
2. `$be_dockerfile_path` = COMPUTE `${$$backend_dir}/Dockerfile`
3. `$fe_dockerfile_path` = COMPUTE `${$$frontend_dir}/Dockerfile`
4. `$be_dockerignore_path` = COMPUTE `${$$backend_dir}/.dockerignore`
5. `$fe_dockerignore_path` = COMPUTE `${$$frontend_dir}/.dockerignore`
6. FOR each path in [$compose_path, $be_dockerfile_path, $fe_dockerfile_path, $be_dockerignore_path, $fe_dockerignore_path]:
   6.1 IF path exists: ASK user via AskUserQuestion `[overwrite | skip | backup-then-rewrite]`
   6.2 BIND answer to corresponding `$$<x>_action`
   6.3 IF action == "backup-then-rewrite": COPY path → `${path}.bak.<timestamp>` then mark for rewrite
   6.4 ELSE IF action == "skip": mark file as untouched in this run
   6.5 ELSE: mark file as overwrite
7. BRANCH 全部都選 skip?
   7.1 EMIT "所有目標檔皆 skip，沒有要產出的檔案" to user; STOP
   7.2 ELSE: GOTO #3.1

### Phase 3 — RENDER artifacts
> produces: `$$rendered_paths`

1. IF `$$compose_action != "skip"`:
   1.1 `$compose_body` = RENDER R4 with vars { backend_dir, frontend_dir, db_kind, backend_port, frontend_port, health_path, db_user, db_pass, db_name }
   1.2 WRITE `$compose_path` ← `$compose_body`
2. IF `$$be_dockerfile_action != "skip"`:
   2.1 `$be_dockerfile_body` = RENDER R5 with vars { python_version, has_alembic, app_module, health_path, backend_port }
   2.2 WRITE `$be_dockerfile_path` ← `$be_dockerfile_body`
3. IF `$$be_dockerignore_action != "skip"`:
   3.1 WRITE `$be_dockerignore_path` ← R7（無 vars）
4. IF `$$fe_dockerfile_action != "skip"`:
   4.1 `$fe_dockerfile_body` = RENDER R6 with vars { node_version, frontend_port, has_messages_dir, has_public_dir, api_base_path }
   4.2 WRITE `$fe_dockerfile_path` ← `$fe_dockerfile_body`
5. IF `$$fe_dockerignore_action != "skip"`:
   5.1 WRITE `$fe_dockerignore_path` ← R8（無 vars）
6. `$$rendered_paths` = list of all paths written
7. EMIT to user: 「已產出/更新檔案清單：$$rendered_paths」

### Phase 4 — PARALLEL subagent verify
> produces: `$$be_result`, `$$fe_result`

1. `$be_prompt` = RENDER R2.backend_template with vars { repo_root: $$repo_root, backend_dir: $$backend_dir, backend_port: $$backend_port, health_path: $$health_path, max_iterations: 5 }
2. `$fe_prompt` = RENDER R2.frontend_template with vars { repo_root: $$repo_root, frontend_dir: $$frontend_dir, frontend_port: $$frontend_port, backend_port: $$backend_port, max_iterations: 5 }
3. SPAWN two Agent tool calls in **a single tool-use message**（並行，非 sequential）：
   3.1 Agent A: `subagent_type=general-purpose`, `description="docker backend smoke"`, `prompt=$be_prompt`
   3.2 Agent B: `subagent_type=general-purpose`, `description="docker frontend smoke"`, `prompt=$fe_prompt`
4. WAIT both agents complete
5. `$$be_result` = PARSE Agent A 最終回報（`{ status: pass|fail, iterations, last_curl, summary, fail_reason? }`）
6. `$$fe_result` = PARSE Agent B 最終回報（同 schema）
7. GOTO #5.1

### Phase 5 — REPORT
1. BRANCH `$$be_result.status == "pass" && $$fe_result.status == "pass"`?
   1.1 EMIT to user 成功摘要：
       - backend: `curl http://localhost:${$$backend_port}${$$health_path}` 通過於第 N 次迭代
       - frontend: `curl http://localhost:${$$frontend_port}/` 通過於第 M 次迭代
       - rendered files (`$$rendered_paths`)
       - 啟動指令：`docker compose up -d`
   1.2 STOP success
   1.3 ELSE: GOTO #5.2
2. EMIT to user 失敗摘要：
   2.1 哪一條（or 兩條）fail
   2.2 各自 `last_curl` 與 `fail_reason`
   2.3 建議的下一步（`docker compose logs <service>`、檢查 port 是否被佔用、檢查 Dockerfile 對應 stage）
   2.4 STOP fail-stop（不再迭代；交給 user 接手）

## §3 INVARIANTS

- 不可在 Phase 4 之前修改 `$$rendered_paths` 以外的檔案。
- Phase 4 必須 **單一訊息內並行 spawn** 兩條 Agent；禁止 sequential await。
- Subagent 各自的迭代預算受 R3 約束；超預算必須以 fail-stop 形式回報，不准無限迴圈。
- Skill 自身**不**呼叫 `docker compose up`；那是 subagent 的職責。Skill 只生成檔案 + 派送 subagent + 收結果。
