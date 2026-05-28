# Stack Detection Cheatsheet

Phase 1 用此表把檔案訊號 → stack 標籤。偵測不到時必須 ASK user。

## Backend

| Signal in `${backend_dir}/` | → `$$backend_stack` | Default port | Default health path | Default app module |
|---|---|---|---|---|
| `pyproject.toml` 含 `fastapi` 或 `requirements.txt` 含 `fastapi` | `python-fastapi` | 8000 | `/health` | `app.main:app` |
| `pyproject.toml` 含 `django` 或 `manage.py` 存在 | `python-django` | 8000 | `/healthz` | `config.wsgi:application` |
| `package.json` 含 `"express"` | `node-express` | 8000 | `/health` | `dist/index.js` |
| 找不到 | `unknown` | — | — | — |

### Backend persistence signals → `$$db_kind`

| Signal | → |
|---|---|
| `alembic.ini` 存在 或 `requirements.txt` 含 `psycopg` 或 `sqlalchemy.url` 含 `postgresql` | `postgres` |
| `requirements.txt` 含 `pymysql` 或 `mysqlclient` | `mysql` |
| 程式碼或設定指向 sqlite 檔案 | `sqlite` |
| 任何訊號都沒有 | `none` |

### Backend launch command 推測

- `python-fastapi`：
  - 有 `alembic.ini`：`alembic upgrade head && uvicorn ${app_module} --host 0.0.0.0 --port ${backend_port}`
  - 無：`uvicorn ${app_module} --host 0.0.0.0 --port ${backend_port}`
- `python-django`：`python manage.py migrate && gunicorn ${app_module} -b 0.0.0.0:${backend_port}`
- `node-express`：`node ${app_module}`

## Frontend

| Signal in `${frontend_dir}/` | → `$$frontend_stack` | Default port | Build cmd | Run cmd |
|---|---|---|---|---|
| `package.json` 有 `next` 且 `next.config.{mjs,js,ts}` 含 `output: 'standalone'` | `next-standalone` | 3001 | `npm run build` | `node server.js` |
| `package.json` 有 `next` 但**無** `output: 'standalone'` | `next-default` | 3001 | `npm run build` | `npm run start` |
| `package.json` 有 `vite` | `vite-react` | 3001 | `npm run build` | `npm run preview -- --host 0.0.0.0 --port ${frontend_port}` |
| 找不到 | `unknown` | — | — | — |

### Frontend optional folders to detect

| Folder | If exists, action |
|---|---|
| `${frontend_dir}/messages/` | next-intl detected → COPY messages into runtime image |
| `${frontend_dir}/public/` | COPY public/ into runtime image；不存在則 `mkdir -p public` 在 builder stage |
| `${frontend_dir}/.env.production` | optional ENV layer |

### Frontend node version

- 預設 Node 20-alpine。
- 若 `package.json.engines.node` 有指定主版本，取用該主版本。

## API base path 推測（frontend → backend）

- 偵測 `next.config.mjs` rewrites 對 `/api/:path*` → 採 `/api`。
- 否則預設 `/api`。

## Backend health endpoint 推測

按以下順序 grep backend source：

1. `app/main.py` 內 `@app.get("/health")` → `/health`
2. `app/main.py` 內 `@app.get("/healthz")` → `/healthz`
3. fallback `/`

## DB credentials 預設

POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB 都用 `postgres / postgres / aixbdd_dev`，
若 backend 已有 `alembic.ini` 或 `.env` 指定不同名，採該值。
