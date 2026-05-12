# Fixtures Runtime

## fixture shape

Java E2E fixtures 由 Spring DI + Cucumber `@ScenarioScope` 提供；不採 Behave 風格的 free-form `context` 物件。

## data source

- PostgreSQL Testcontainer，由 `TestcontainersConfiguration`（`@ServiceConnection`）動態啟動，並透過 Spring Boot 3.1+ 的 `@ServiceConnection` 機制自動注入到 `DataSource`。
- 資料存取：`JdbcClient`（Spring 6+ 提供，`spring-boot-starter-jdbc` 依賴自動配置）；查詢結果以 Java `record` 接收。
- 共用 scenario 狀態經 `ScenarioContext`（`@Component @ScenarioScope`）暴露：`getLastResponse()`、`putId(key, value)`／`getId(key)`、`putMemo(key, value)`／`getMemo(key)`、`getJwtToken()` 等。
- 共用便利方法經 `ScenarioContextHelper`（`@Component`）封裝，例：`getUserId(String userName)`。

## reset policy

- 每個 scenario 開始時，`DatabaseCleanupHook`（`@Before(order = 0)`）會：
  1. 呼叫 `scenarioContext.clear()` 清空所有 scenario-local 狀態。
  2. 透過 `JdbcTemplate.execute("DELETE FROM ...")` 清空業務 table（**注意外鍵順序，先刪子表**；starter 預設只列 TODO，請在加入 entity 後補齊）。
  3. 透過 `JdbcTemplate.execute("ALTER SEQUENCE <table>_id_seq RESTART WITH 1")` 重設 sequence。
- `ScenarioContext` 因 `@ScenarioScope` 每個 scenario 自動建立新 instance；scenario 結束後 Spring 自動釋放。
- Cross-scenario state sharing 是 forbidden：**禁止**用 static field／JVM-wide singleton 跨 scenario 傳資料。

## fallback instruction

If a required fixture source is missing, stop before red generation and report the missing fixture/testability gap. Do not replace missing fixture truth with permissive mocks（例：把 `JdbcClient` 換成 `Mockito.mock(...)`）。

## known limitations

- File upload fixtures 未預載；如需測 `multipart/form-data`，應在新增功能時於 `cucumber/` 下加入 `MultipartHelper` 並在本檔記錄。
- 外部資源 fixture（外部 HTTP API、訊息佇列）必須先在 test strategy 或 provider contract truth 宣告，再以 `@MockBean`／WireMock 等手段隔離；**禁止**直接打 production endpoint。
- `@ServiceConnection` 對 Spring Boot 4 的 `spring-boot-testcontainers` starter 為必要依賴；移除或降級此 dependency 會導致 Testcontainer 無法注入連線。
