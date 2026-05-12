# Test Command Format — Phase 6 PREPARE_TEST_COMMAND → verify_goal `command` 字串

> Defines the shell-command string passed as the `command` parameter to `mcp__sf__verify_goal`. Pure declarative.
>
> Evaluator chat seat 會接收這個 command、用 bash tool 執行、觀察 raw stdout/stderr、據此呼叫 `submit_verdict` 給 worker。Worker 端不再需要組裝 markdown evidence。

---

## §通用骨架

```
{test runner CLI} {flags} {當前 goal feature 路徑} {所有 DONE features 路徑}
```

`{test runner CLI}` 由 worker project 自己決定 — 用 project 既有的測試入口（package.json script、Makefile target、直接呼叫 runner binary 等等都可以），本 skill 不預設任何 runner 名稱或 monorepo 慣例。

**完整命令、無 placeholder**：worker 直接把所有要跑的 `.feature` 路徑明列在指令中（evaluator 端會直接從命令文字抓 `.feature` token 比對 scope 與內容；不做任何字面替換）。本輪 scope = 當前 goal feature + 所有已 DONE features，一個不能少、不能多。Done features 一併列入是為了讓 raw output 反映 regression（之前綠的 feature 被新改動弄紅）。

長度上限：**4000 字元**（命令而非 prose，超過幾乎一定是組裝錯誤）。

---

## §每個 phase 的觀察點

command 一次同時跑「當前 goal 的 feature file」+「所有已 DONE 的 feature files」；evaluator 從 raw output 推斷各檔是 pass 還是 fail，再依 phase 決定當前 goal 的 verdict：

- **RED phase** — 當前 goal 預期 fail（含 failed step / non-zero exit code）即視為 RED 達成。同時跑的 done features 應仍是 pass；若它們紅了，是 regression，整體 verdict 仍會 fail（evaluator 端 grade）。
- **GREEN phase** — 當前 goal 預期 pass。同時跑的 done features 也必須 pass；任何一檔紅了（regression 或新改動弄壞舊行為）都會使 verdict 變 fail。
- **REFACTOR phase** — 當前 goal + done features 全部 pass 才視為達成；regression 是 REFACTOR 想抓到的主要訊號。

---

## §sub-skill 失敗時的 command

若 SKILL.md Phase 5 DELEGATE 結果是 error 物件（sub-skill 內部失敗），Phase 6 仍須產出可執行的 command — 用同一個 phase command 即可，evaluator 跑出來會看到測試 fail，自然回 verdict=`failed`。evaluator 端從 raw output 推斷失敗原因；worker 不需要在 command 內傳 sub-skill 的 error message（它走不通常規 channel，evaluator 也不會解析它）。

---

## §禁止事項

- ❌ 不要使用 placeholder（`{feature_file}` / `{feature_files}` / glob 萬用字元）代替明確路徑 — evaluator 不做替換、會直接掃 `.feature` token；缺路徑或多路徑都會被視為 scope 違反並回 'failed'。
- ❌ 不要篡改 worker 端 `.feature` 副本的 scenario / step 內容（語意改寫、刪 step、加 scenario、scenario 順序大幅打亂）— evaluator 用 aggregate 做語意比對，發現大幅篡改直接 'failed'。為了讓 runner 跑得起來而做的符號 / 格式微調（空白、註解、Background）OK。
- ❌ 不要在 command 內塞 worker 的 markdown 摘要（舊 `result` 參數的格式已淘汰）。
- ❌ 不要呼叫多個 test runner（除非用 `&&` 串）；evaluator 只看 bash 的 final exit code 與 stdout。
- ❌ 不要在 command 內塞 `cd <subdir> && ...` 之類的目錄切換。evaluator 的 system prompt 已明令禁止 `cd` / `pushd` / `chdir`，即使是 `bash -c "cd ..."` 包起來也不行 — 它會直接 reject 並回 `env_error`。需要 runner 在子目錄跑時，請用 runner 自帶的 `--cwd` / `-C` / workspace filter / 絕對路徑表達。

---

## §環境準備（PRE-VERIFY）

evaluator 跑命令的 CWD 等於 worker session 的 CWD（一樣的 project root），但 evaluator 系統角色被明令禁止：

- 不會做 `pnpm install` / `pip install` / `uv sync` / `make setup`
- 不會 `cd` 進子目錄
- 不會修任何專案檔
- 看到 `command not found` / `pnpm: No projects found` / `ModuleNotFoundError` / `Cannot find package` 之類的環境錯誤就直接走 env_error，verdict 自動 fail

所以**準備環境是 worker 端責任**。SKILL.md Phase 6.5 ENV_PREFLIGHT 強制 worker 在 verify_goal dispatch 之前，先在自己的 bash session 用同一份 command 做一次 dry-run，確認：

- runner CLI 找得到（`which <runner>` 或 dry-run 不會 `command not found`）
- workspace / package manifest 找得到（pnpm/npm/uv/poetry 都 happy）
- 所有 import / fixture 模組都裝好（runner 至少要能跑到 step 階段，哪怕 step 本身 fail 也算 launch_ok）

dry-run 看到 env-level 失敗時，worker 自己跑必要的 `pnpm install` 等 prep 命令、清完之後再進 Phase 7。若兩輪 prep 後仍 launch 不起來，把實況交給 evaluator（evaluator 會回 env_error，verdict fail，但至少留下可診斷的痕跡）— 別在 worker 端死循環裝相依。

### Docker runtime（非預設 socket）

SKILL.md Phase 1.5 DOCKER_ENV_PREP 會偵測當前 docker context endpoint，若非預設 `/var/run/docker.sock`（Colima / OrbStack / Rancher Desktop / Podman 等情境），就把 `DOCKER_HOST=<endpoint>` 寫進 `$$cwd/.env`。test runner 透過自身 dotenv loader 讀取這份檔案，docker SDK / testcontainers / docker-compose 即可拿到正確 endpoint — **test command 內不需要也不應該再帶 docker 相關 prefix**。
