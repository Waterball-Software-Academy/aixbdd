# Variant: java-e2e

## Role

`java-e2e` renders web-backend preset handlers into Java Cucumber step definitions for API-level end-to-end tests using Spring Boot + MockMvc + Testcontainers.

This variant only defines rendering mechanics. It does not classify sentence parts and does not select handlers.

## Runtime Contract

- Language: Java 25+
- BDD framework: Cucumber 7.34.3 + JUnit Platform Suite
- HTTP client: Spring MockMvc (via `@AutoConfigureMockMvc`)
- Persistence access: Spring `JdbcClient` and repositories
- App access: Spring Boot application context loaded by `@SpringBootTest`
- Context object: `@ScenarioScope ScenarioContext` (Spring DI)
- Time control: project-owned runtime instruction configured clock adapter
- External resources: project-owned runtime instruction configured stub registry
- DB container: Testcontainers `PostgreSQLContainer` via `@ServiceConnection` (Spring Boot 3.1+)
- Migration: Flyway autoconfigure on `src/main/resources/db/migration/V*__*.sql`
- JWT: JJWT 0.12.x (`JwtHelper.generateToken(userId)`)

## Required Context Fields

`ScenarioContext` is a `@Component @ScenarioScope` Spring bean, initialized per scenario by `DatabaseCleanupHook.@Before(order = 0)`:

```java
@Component
@ScenarioScope
public class ScenarioContext {
    private ResponseEntity<?> lastResponse;
    private final Map<String, Object> ids = new HashMap<>();
    private final Map<String, Object> memo = new HashMap<>();
    private String jwtToken;
    private Object queryResult;
    private String lastError;
}
```

| Field | Purpose |
|---|---|
| `lastResponse` | MockMvc result; set by http-operation step |
| `ids` | natural key → DB id map (e.g. `{"小明": 1}`) |
| `memo` | scenario-scoped temporary storage |
| `jwtToken` | JWT token; set by auth Given steps |
| `queryResult` | last query result body |
| `lastError` | last error message string |

## Step File Layout

Directories under `steps/<function-package-slug>/` map to handlers in [`handler-routing.yml`](../handler-routing.yml) (hyphen in handler name → snake_case folder):

```text
src/test/java/${BASE_PACKAGE}/
  steps/
    <function-package-slug>/
      aggregate_given/
      http_operation/
      success_failure/
      readmodel_then/
      aggregate_then/
      time_control/
      external_stub/
    common_then/
      CommonThen.java
    helpers/
      ScenarioContextHelper.java
```

One generated step pattern should map to one `.java` file per step class unless a reusable shared step already owns the exact matcher.

## Cucumber Matcher Contract

- Annotate with `@Given`, `@When`, or `@Then` according to the Gherkin keyword.
- First injected field is `ScenarioContext` (Spring DI, `@Autowired`).
- Additional parameters are derived from `L1` placeholders; order matches appearance in L1 pattern.
- String placeholders: `{string}` (quoted).
- Integer placeholders: `{int}`.
- Long/decimal placeholders: `{double}` or `{long}` as appropriate.
- Use `@Autowired` to inject repositories and `JdbcClient` beans.

## MockMvc Usage Pattern

```java
MvcResult result = mockMvc.perform(
    post("/api/v1/orders")
        .header("Authorization", "Bearer " + scenarioContext.getJwtToken())
        .contentType(MediaType.APPLICATION_JSON)
        .content(objectMapper.writeValueAsString(requestBody)))
    .andReturn();
scenarioContext.setLastResponse(
    ResponseEntity.status(result.getResponse().getStatus())
        .body(result.getResponse().getContentAsString()));
```

## Database Cleanup

`DatabaseCleanupHook.@Before(order = 0)` calls `scenarioContext.clear()` and executes DELETE statements (child tables before parent tables) and resets sequences:

```java
@Before(order = 0)
public void cleanDatabase() {
    scenarioContext.clear();
    jdbcTemplate.execute("DELETE FROM order_approval_steps");
    jdbcTemplate.execute("DELETE FROM order_promotion_caps");
    jdbcTemplate.execute("DELETE FROM orders");
    jdbcTemplate.execute("ALTER SEQUENCE orders_id_seq RESTART WITH 1");
    jdbcTemplate.execute("ALTER SEQUENCE order_approval_steps_id_seq RESTART WITH 1");
    jdbcTemplate.execute("ALTER SEQUENCE order_promotion_caps_id_seq RESTART WITH 1");
}
```

## Feature Archive Layout

Cucumber feature files are placed under `src/test/resources/features/<spec-package-slug>/`:

```text
src/test/resources/features/
  <spec-package-slug>/
    01-新會員建立首筆訂單.feature
    02-送出大額訂單審核.feature
    ...
```

The spec package slug is the directory name from `FEATURE_SPECS_DIR` (e.g., `01-訂單結帳`).

## Forbidden

- Do not infer endpoint path outside operation contracts.
- Do not infer request or response field names outside L4 bindings.
- Do not call application service internals from E2E steps.
- Do not make a second MockMvc call in Then handlers.
- Do not assert response payload in `http-operation`.
- Do not use repository access in `readmodel-then`.
- Do not use MockMvc access in `aggregate-given` or `aggregate-then`.
- Do not sleep or read wall-clock time in `time-control`.
- Do not make real external calls in `external-stub`.
- Do not use `context.*` dict-style access; use typed `ScenarioContext` getter/setter.

## Legal Red Expectation

A generated step definition is a valid red step only when:

- the matcher is generated from exact `L1`;
- all request/assertion values come from L4 bindings;
- the preset tuple resolves to this variant;
- the code can run far enough to expose missing product implementation or behavioral mismatch.

Missing truth is not a legal red; it must stop before rendering.
