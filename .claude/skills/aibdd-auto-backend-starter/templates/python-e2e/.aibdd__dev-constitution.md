# Dev Constitution — Python FastAPI Backend (Starter)


## §1 Layer Ownership（精簡）

| 層 | 慣例路徑 | 擁有 | 禁止 |
|---|---|---|---|
| API | `app/api` | Router、HTTP 狀態對應、DTO 進出轉譯 | 略過 service 直連 DB、業務分支 |
| Schemas | `app/schemas` | Pydantic／transport shape | ORM mapping |
| Services | `app/services` | 用例編排、交易意圖、領域決策 | FastAPI Request/Response、裸 SQL |
| Repositories | `app/repositories` | 查詢／寫入 | HTTP 外形、非儲存必需的業務分支 |
| Models | `app/models` | SQLAlchemy entity、`Base.metadata` | API policy |
| Core | `app/core` | Settings、DI、`deps`、共用基建 adapter | 功能專屬規則 |
| Entry | `app/main.py` | `create_app()` factory、掛載 router | 健康檢查以外的功能 endpoint 膨脹 |

### §1.1 App Factory Contract

- `app/main.py` **必須** 暴露 `create_app() -> FastAPI`，模組級 `app = create_app()` 屬 runtime 契約。
- `app/api/__init__.py` **必須** 匯出根 router 供 factory 掛載。
- **`GET /health`**：**僅**基建探活；回應 **必須** 為 `{"status": "ok"}`，**禁止**累積產品行為。

---

## §2 Dependency Direction

**允許**

```text
api -> schemas
api -> services
services -> repositories
services -> models
repositories -> models
core -> infrastructure libraries
```

**禁止**

```text
models -> api
models -> services
repositories -> api
services -> api
core -> feature-specific services
```

---

## §3 Configuration And Dependency Injection

- 設定來自 **環境／設定物件**，feature 層 **禁止** 硬編 URL／secret。
- DB session **必須** 經 `app/core/deps.py` 或 repository 建構邊界注入；**`set_session_factory()`** 為測試／runtime 置換的合法入口。
- **禁止** 在功能模組建立全域 Engine singleton。

---

## §4 Persistence And Migration

- ORM schema SSOT：**`app.models.Base.metadata`**。
- Migration：**`alembic/versions`**；**`alembic/env.py`** 的 `target_metadata` **必須** 綁定上述 metadata。
- 每一次持久化結構變更 **必須** 伴隨 Alembic revision；migration 檔為基建產物，service **禁止** 假設特定 revision 順序硬編在業務碼。
- **`alembic.ini`** 須保留 `fileConfig()` 所需的 `[loggers]`／`[handlers]`／`[formatters]` 等區段。

---

## §5 Project Overrides

架構例外 **必須** 明示且暫時。

| Rule ID | Status | Scope | Reason | Deadline (ISO) | Owner |
|---|---|---|---|---|---|
| _(無)_ | | | | | |
