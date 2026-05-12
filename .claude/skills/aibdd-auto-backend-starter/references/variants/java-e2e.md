# Starter Variant: Java E2E (Spring Boot 4 + Cucumber + JdbcClient)

技術棧：Spring Boot 4.0.6 + Spring `JdbcClient` + Cucumber 7.34.3 + Testcontainers (PostgreSQL via `@ServiceConnection`) + Flyway + JJWT 0.12.6

> **本骨架定位**：以「最小可運轉」為目標的 walking skeleton——`Application.java` 只掛 `@SpringBootApplication`，唯一 endpoint 是 `GET /health`，acceptance 由 `RunCucumberTest`（JUnit Platform Suite）驅動，並已備好 `ScenarioContext`／`CommonThen`／`JwtHelper`／`DatabaseCleanupHook` 等共用 fixture。後續 `/aibdd-discovery` → `/aibdd-red` → `/aibdd-green` 會在此基礎上長出 controller / service / repository / step definitions。

---

## 目錄結構

```
${PROJECT_ROOT}/
├── .aibdd/
│   ├── arguments.yml                                   # kickoff project config；starter 只讀
│   ├── dev-constitution.md                             # 產品架構 bridge（層級、依賴、持久化；對齊 DEV_CONSTITUTION_PATH）
│   └── bdd-stack/
│       ├── project-bdd-axes.md                         # `${BDD_CONSTITUTION_PATH}`：§5.1 檔名軸、§5.2 Red Pre-Hook 軸
│       ├── acceptance-runner.md                        # `mvn test` + `RunCucumberTest` 入口慣例
│       ├── step-definitions.md                         # `steps/` package layout、matcher 規範
│       ├── fixtures.md                                 # `ScenarioContext`／`@ScenarioScope`／Testcontainers 生命週期
│       ├── feature-archive.md                          # specs `${FEATURE_SPECS_DIR}` ↔ `src/test/resources/features/<current_spec_package>/`
│       └── prehandling-before-red-phase.md             # `${RED_PREHANDLING_HOOK_REF}`：java-e2e = schema-analysis／flyway-migration
├── src/
│   ├── main/
│   │   ├── java/${BASE_PACKAGE_PATH}/                  # 例：com/example/demo/
│   │   │   ├── Application.java                        # Spring Boot 入口（@SpringBootApplication）
│   │   │   ├── controller/
│   │   │   │   └── HealthController.java               # starter smoke：GET /health
│   │   │   ├── security/
│   │   │   │   ├── JwtTokenFilter.java                 # OncePerRequestFilter；驗 JWT、塞 currentUserId 到 request attribute
│   │   │   │   └── CurrentUser.java                    # request → currentUserId（Long）；未認證即 401
│   │   │   ├── model/                                  # 空（Java record／DTO；由 automation skill 產生）
│   │   │   ├── repository/                             # 空（基於 Spring JdbcClient）
│   │   │   └── service/                                # 空（用例編排、領域決策）
│   │   └── resources/
│   │       ├── application.yaml                        # 主設定（注意：副檔名為 `.yaml`）
│   │       ├── db/migration/                           # 空（Flyway migrations：V{N}__xxx.sql）
│   │       ├── static/                                 # 空（Spring Boot 靜態資源預留）
│   │       └── templates/                              # 空（Spring Boot view template 預留；非 Cucumber）
│   └── test/
│       ├── java/${BASE_PACKAGE_PATH}/
│       │   ├── Application.java 同層
│       │   ├── RunCucumberTest.java                    # Cucumber 入口（@Suite + @IncludeEngines("cucumber")）
│       │   ├── config/
│       │   │   ├── CucumberSpringConfiguration.java    # @CucumberContextConfiguration + @SpringBootTest + @AutoConfigureMockMvc
│       │   │   └── TestcontainersConfiguration.java    # @ServiceConnection PostgreSQLContainer
│       │   ├── cucumber/
│       │   │   ├── DatabaseCleanupHook.java            # @Before(order = 0) DELETE + sequence reset
│       │   │   ├── JwtHelper.java                      # 測試用 JWT Token 產生器（JJWT 0.12.x API）
│       │   │   └── ScenarioContext.java                # @ScenarioScope 共用狀態（lastResponse／ids／memo）
│       │   └── steps/
│       │       ├── HealthSteps.java                    # starter smoke：MockMvc GET /health
│       │       ├── common_then/
│       │       │   └── CommonThen.java                 # 操作成功／失敗／錯誤訊息／原因 共用 Then
│       │       └── helpers/
│       │           └── ScenarioContextHelper.java      # getUserId(name) 等便利方法
│       └── resources/
│           └── features/                               # Cucumber `.feature` 根目錄
│               └── HealthCheck.feature                 # walking skeleton smoke
├── ${SPECS_ROOT_DIR}/                                  # 規格檔案（例：specs/）
│   ├── architecture/
│   │   ├── boundary.yml                                # kickoff：唯一 boundary id
│   │   └── component-diagram.class.mmd
│   ├── <NNN-slug>/                                     # plan package；Discovery 建立 / 更新
│   │   ├── spec.md
│   │   └── reports/
│   └── <boundary>/                                     # boundary truth root（例：backend）
│       ├── actors/
│       ├── contracts/                                  # operation contracts; web-service 由 /aibdd-form-api-spec 產出 OpenAPI
│       ├── data/                                       # boundary state truth; web-service 由 /aibdd-form-entity-spec 產出 DBML
│       ├── shared/
│       │   └── dsl.yml                                 # boundary shared DSL truth
│       ├── test-strategy.yml
│       └── packages/                                   # Discovery late-bind `NN-<功能模組描述>/`
├── docker-compose.yml                                  # local PostgreSQL（單一 service）
├── pom.xml                                             # Maven 設定
```

### 落檔慣例（與 Pre-Red hook 對齊）

Walking skeleton **僅**建立空的 `model/`、`repository/`、`service/` 目錄與 `db/migration/`，**不**預先放任何 entity／migration。後續若依 DBML 增量新增 aggregate：

- model：`src/main/java/${BASE_PACKAGE_PATH}/model/<aggregate>.java`（Java `record`，與 `JdbcClient.query(MyRecord.class)` 對接）
- repository：`src/main/java/${BASE_PACKAGE_PATH}/repository/<Aggregate>Repository.java`
- migration：`src/main/resources/db/migration/V{N}__add_<aggregate>.sql`

掃描範圍／規則細節以 `.aibdd/bdd-stack/prehandling-before-red-phase.md`（`${RED_PREHANDLING_HOOK_REF}`）為準。

---

## 依賴安裝（Maven）

### 完整依賴清單

| 分類 | groupId | artifactId | 版本 | scope | 用途 |
|------|---------|------------|------|-------|------|
| **Web** | `org.springframework.boot` | `spring-boot-starter-webmvc` | (parent) | compile | Spring Web MVC（Spring Boot 4 模組化命名，**取代** 舊 `spring-boot-starter-web`） |
| **Migration** | `org.springframework.boot` | `spring-boot-starter-flyway` | (parent) | compile | Flyway autoconfigure（啟動時自動套用 `db/migration/`） |
| **Migration** | `org.flywaydb` | `flyway-database-postgresql` | (parent) | compile | Flyway PostgreSQL 方言支援（10+ 必要） |
| **Database** | `org.postgresql` | `postgresql` | (parent) | runtime | PostgreSQL JDBC driver |
| **Util** | `org.projectlombok` | `lombok` | (parent) | optional | 編譯期 boilerplate 縮減（spring-boot-maven-plugin 已 exclude，runtime 不打包） |
| **API Docs** | `org.springdoc` | `springdoc-openapi-starter-webmvc-ui` | `${SPRINGDOC_VERSION}` | compile | Swagger UI + OpenAPI 3 文件（`/swagger-ui.html`） |
| **JWT** | `io.jsonwebtoken` | `jjwt-api` | `${JJWT_VERSION}` | compile | JJWT 介面 |
| **JWT** | `io.jsonwebtoken` | `jjwt-impl` | `${JJWT_VERSION}` | runtime | JJWT 簽章 / 解析實作 |
| **JWT** | `io.jsonwebtoken` | `jjwt-jackson` | `${JJWT_VERSION}` | runtime | JWT payload 的 Jackson 序列化 |
| **Test** | `org.springframework.boot` | `spring-boot-starter-webmvc-test` | (parent) | test | MockMvc + Web 測試工具（**取代** 舊 `spring-boot-starter-test`） |
| **Test** | `org.springframework.boot` | `spring-boot-starter-flyway-test` | (parent) | test | Flyway 測試輔助 |
| **Test** | `org.springframework.boot` | `spring-boot-starter-restdocs` | (parent) | test | Spring REST Docs |
| **Test** | `org.springframework.boot` | `spring-boot-testcontainers` | (parent) | test | `@ServiceConnection` 支援（Spring Boot 3.1+） |
| **Test** | `org.springframework.restdocs` | `spring-restdocs-mockmvc` | (parent) | test | REST Docs 與 MockMvc 整合 |
| **Test** | `org.testcontainers` | `testcontainers-junit-jupiter` | (parent) | test | Testcontainers JUnit 5 整合（Spring Boot 4 新命名） |
| **Test** | `org.testcontainers` | `testcontainers-postgresql` | (parent) | test | Testcontainers PostgreSQL module（Spring Boot 4 新命名） |
| **Test** | `org.junit.platform` | `junit-platform-suite` | (parent) | test | JUnit Platform Suite（驅動 Cucumber 與其他 engine） |
| **BDD** | `io.cucumber` | `cucumber-java` | `${CUCUMBER_VERSION}` | test | Cucumber Java step bindings |
| **BDD** | `io.cucumber` | `cucumber-spring` | `${CUCUMBER_VERSION}` | test | Cucumber 與 Spring DI 整合（含 `@ScenarioScope`） |
| **BDD** | `io.cucumber` | `cucumber-junit-platform-engine` | `${CUCUMBER_VERSION}` | test | 在 JUnit Platform 上執行 Cucumber |

> 標記為 **(parent)** 的依賴版本由 `spring-boot-starter-parent ${SPRING_BOOT_VERSION}` 統一管理，無需指定 `<version>`。

### Properties

| 名稱 | 值 |
|------|-----|
| `java.version` | `${JAVA_VERSION}`（預設 25） |
| `cucumber.version` | `${CUCUMBER_VERSION}`（預設 7.34.3） |
| `jjwt.version` | `${JJWT_VERSION}`（預設 0.12.6） |
| `springdoc.version` | `${SPRINGDOC_VERSION}`（預設 3.0.3） |
| `${SPRING_BOOT_VERSION}` (parent) | 預設 4.0.6 |

### Maven Plugins

- `spring-boot-maven-plugin`：排除 Lombok（runtime 不打包）。
- `maven-compiler-plugin`：在 `default-compile` 與 `default-testCompile` 兩階段都把 Lombok 加進 `annotationProcessorPaths`。
- `asciidoctor-maven-plugin 2.2.1`：`prepare-package` 階段產生 Spring REST Docs HTML（依賴 `spring-restdocs-asciidoctor`）。

> 備註：starter 沒有顯式宣告 `flyway-maven-plugin`。本機跑 migration 直接靠 `mvn spring-boot:run`（觸發 Flyway autoconfigure），acceptance 期間則由 `@SpringBootTest` + `@ServiceConnection` 在 Testcontainer 上自動套用 `V*__*.sql`。如需獨立的 `flyway:info` / `flyway:migrate` Maven goal，請另行加入 plugin 並在 `.aibdd/bdd-stack/prehandling-before-red-phase.md` §4.0 註記。

### pom.xml 結構摘要

```xml
<groupId>${GROUP_ID}</groupId>
<artifactId>${ARTIFACT_ID}</artifactId>
<version>0.0.1-SNAPSHOT</version>
<name>${PROJECT_NAME}</name>
<description>${PROJECT_DESCRIPTION}</description>

<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>${SPRING_BOOT_VERSION}</version>
</parent>

<properties>
    <java.version>${JAVA_VERSION}</java.version>
    <cucumber.version>${CUCUMBER_VERSION}</cucumber.version>
    <jjwt.version>${JJWT_VERSION}</jjwt.version>
</properties>
```

> 完整內容見 `templates/java-e2e/pom.xml`（template 中所有 Maven property reference 如 `${jjwt.version}` 都以 `$$` 在 Python `string.Template` 中跳脫，render 後會還原為 Maven 看得懂的 `${jjwt.version}`）。

安裝指令：`mvn clean compile`

---

## 設定檔說明

### application.yaml（注意：副檔名為 `.yaml`，非 `.yml`）

```yaml
spring:
  application:
    name: ${ARTIFACT_ID}
  datasource:
    url: jdbc:postgresql://localhost:${DB_PORT}/${DB_NAME}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    driver-class-name: org.postgresql.Driver
```

**設定檔特色**：

- **沒有** JPA 設定區段（`spring.jpa.*`）：本骨架使用 Spring `JdbcClient`，不需 `hibernate.dialect`、`ddl-auto`。
- **沒有** JWT 設定區段（`jwt.*`）：本骨架未啟用 Authentication／Authorization；`JwtHelper` 透過 `@Value("${jwt.secret-key:...}")` 提供 default fallback，新增 JWT 守門時再於 `application.yaml` 補設。
- **沒有** `spring.flyway.*` 設定：使用 Spring Boot Flyway autoconfigure 預設行為（`locations=classpath:db/migration`、`baseline-on-migrate=false`、`enabled=true`）。
- **沒有** `application-test.yml`：測試環境改採 `TestcontainersConfiguration` + `@ServiceConnection`（見下節），由 `@Import(TestcontainersConfiguration.class)` 注入連線；無需在 yaml 中改寫成 `jdbc:tc:` URL。

### docker-compose.yml（local PostgreSQL）

開發用 PostgreSQL 18 容器，container name `${PROJECT_SLUG}-postgres`，DB／帳密／port 由 `${DB_NAME}` / `${DB_USER}` / `${DB_PASSWORD}` / `${DB_PORT}` 占位。附帶 `pg_isready` healthcheck 與具名 volume `postgres-data`。

> 此 compose 服務**僅**為 local 開發／手動 migration 使用；acceptance 與 CI 的 DB 完全交給 Testcontainers 動態啟動，不依賴此 compose。

---

## 安全（JWT 認證 — production-side）

### JwtTokenFilter.java

`OncePerRequestFilter` Spring `@Component`：每個請求若帶 `Authorization: Bearer <token>` 就驗 JWT，並把 subject 以 `Long.parseLong(...)` 結果塞進 request attribute key `"currentUserId"`。Token 過期回 `401 {"detail":"Token 已過期"}`；其他驗證失敗回 `401 {"detail":"無效的 Token"}`；無 header 則直接 `chain.doFilter(...)` 放行（讓未受保護的端點如 `/health` 維持公開）。

Secret key 由 `@Value("${jwt.secret-key:chapter04-test-secret-key-do-not-use-in-production}")` 注入；預設值與 `cucumber/JwtHelper.java` 一致，acceptance 跑出來的 token 預設可被 production filter 驗證。**正式環境**請覆寫 `application.yaml` 的 `jwt.secret-key`。

### CurrentUser.java

純 utility（非 Spring bean）。`CurrentUser.getId(request)` → 強型別 `Long`，未認證即 `401 {"detail":"無效的認證憑證"}`；`CurrentUser.getIdOrNull(request)` 用於可匿名查詢的端點。

> **subject 型別約定**：starter 的 production filter 假設 JWT subject 是可被 `Long.parseLong` 解析的字串。若專案改用其他 user id 形態（UUID、業務字串），需同步調整 `JwtTokenFilter` 的 cast 與 `CurrentUser.getId` 回傳型別，或改用業務 service 在 controller 層手動解碼。

---

## 測試框架設定（Cucumber + Spring Boot Test）

### RunCucumberTest.java（Cucumber 入口）

```java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
public class RunCucumberTest {
}
```

> 採用 JUnit Platform Suite 自動掃描 `src/test/resources/features/**/*.feature`。
> Glue path 由 `cucumber-spring` 自動推導為 `RunCucumberTest` 所在 package（`${BASE_PACKAGE}`），故同層／子套件 `steps/`、`config/`、`cucumber/` 都會被掃到。

### CucumberSpringConfiguration.java

```java
@CucumberContextConfiguration
@SpringBootTest
@AutoConfigureMockMvc
@Import(TestcontainersConfiguration.class)
public class CucumberSpringConfiguration {
}
```

> 不指定 `webEnvironment = RANDOM_PORT`，改用 `MockMvc` 直接呼叫 Controller，毋須真實 HTTP server，速度較快。
> `@Import(TestcontainersConfiguration.class)` 把 `@ServiceConnection` PostgreSQLContainer 帶入，所以 acceptance 跑起來時，DataSource 自動指向 Testcontainer 而非本機 PostgreSQL。

### TestcontainersConfiguration.java（透過 `@ServiceConnection` 自動注入連線）

```java
@TestConfiguration(proxyBeanMethods = false)
public class TestcontainersConfiguration {

    @Bean
    @ServiceConnection
    PostgreSQLContainer postgresContainer() {
        return new PostgreSQLContainer(DockerImageName.parse("postgres:latest"));
    }
}
```

> Spring Boot 3.1+ 的 `@ServiceConnection` 機制會自動把容器連線資訊注入到 Spring `DataSource`，無需在 yaml 中改寫成 `jdbc:tc:` URL，也不必手動覆寫 `spring.datasource.*`。

> Spring context 啟動健康度由 `RunCucumberTest`（透過 `@CucumberContextConfiguration` + `@SpringBootTest`）覆蓋，starter 不再額外提供獨立的 `contextLoads` smoke。本地手動啟動 app 請走 `docker-compose.yml`（`docker compose up -d`）+ `mvn spring-boot:run`。

---

## ScenarioContext（@ScenarioScope 共用狀態）

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

    // getter / setter / putId / getId / hasId / putMemo / getMemo / clear()
}
```

| Field | 對應 Python `context.*` | 用途 |
|---|---|---|
| `lastResponse` | `context.last_response` | MockMvc／HTTP 回應 |
| `ids` | `context.ids` | 自然鍵 → DB id（如 `{"小明": 1}`） |
| `memo` | `context.memo` | scenario 暫存 |
| `jwtToken` | （Python `JwtHelper` 即時生成） | 跨 step 傳遞 token |
| `queryResult` | `context.query_result` | 查詢結果 |
| `lastError` | `context.last_error` | 最近一次錯誤敘述 |

`clear()` 會把上述所有欄位重置；由 `DatabaseCleanupHook.@Before(order = 0)` 呼叫。

### DatabaseCleanupHook.java

```java
public class DatabaseCleanupHook {
    @Autowired private JdbcTemplate jdbcTemplate;
    @Autowired private ScenarioContext scenarioContext;

    @Before(order = 0)
    public void cleanDatabase() {
        scenarioContext.clear();
        // TODO: 加入 DELETE 語句（注意外鍵順序，先刪子表）
        // jdbcTemplate.execute("DELETE FROM <child_table>");
        // jdbcTemplate.execute("DELETE FROM <parent_table>");
        // TODO: 重設 sequence
        // jdbcTemplate.execute("ALTER SEQUENCE <table>_id_seq RESTART WITH 1");
    }
}
```

> Starter 預設只放註解 TODO；加入 entity 後請於此補齊真實 DELETE／sequence reset，避免測試間互相污染。

### JwtHelper.java（測試用 JWT 產生器，JJWT 0.12.x API）

```java
@Component
public class JwtHelper {
    private final SecretKey secretKey;   // 從 jwt.secret-key（@Value）讀取
    private final int expireHours;       // 從 jwt.expire-hours（@Value）讀取，預設 1

    public String generateToken(String userId) {
        return Jwts.builder()
                .subject(userId)
                .issuedAt(Date.from(Instant.now()))
                .expiration(Date.from(Instant.now().plus(expireHours, ChronoUnit.HOURS)))
                .signWith(secretKey)
                .compact();
    }

    public String verifyToken(String token) { ... }
}
```

---

## 通用 Step Definitions

### CommonThen.java

| Step pattern (zh-Hant) | 行為 |
|---|---|
| `@Then("操作成功")` | `scenarioContext.getLastResponse()` 的 status code ∈ `[200, 299]` |
| `@Then("操作失敗")` | status code ∈ `[400, 499]` |
| `@Then("錯誤訊息應為 {string}")` | 從 response body（String 或 `Map`）依序找 `message`／`detail`／`error` 欄位後比對 |
| `@Then("操作失敗，原因為 {string}")` | 組合：先呼叫 `operationFailed()`，再呼叫 `errorMessageShouldBe(reason)` |

> 實作依賴 `scenarioContext.lastResponse` 必須先在 `@When`／前置 step 中被 set；HTTP 互動建議透過 MockMvc 後手動 `scenarioContext.setLastResponse(ResponseEntity.ok(body))` 包裝（或在新增 step package 時擴充封裝）。

### ScenarioContextHelper.java

```java
@Component
public class ScenarioContextHelper {
    public Long getUserId(String userName) {
        // 從 ScenarioContext.ids 取得用戶 ID（Given 步驟中建立的）；
        // 找不到就拋 IllegalStateException 提示 Given 缺失。
    }
    public String getUserIdAsString(String userName) { ... }
}
```

---

## arguments.yml 變數對照

| Placeholder | 來源 | 說明 | 範例 |
|-------------|------|------|------|
| `{{STARTER_VARIANT}}` | arguments.yml | starter variant，固定為 `java-e2e` | `java-e2e` |
| `{{PROJECT_NAME}}` | 詢問使用者 / arguments.yml | 專案顯示名稱（pom.xml `<name>`） | `Demo Service` |
| `{{PROJECT_DESCRIPTION}}` | derived | 專案描述（pom.xml `<description>`） | `Demo Service — BDD Workshop Java E2E` |
| `{{PROJECT_SLUG}}` | derived from PROJECT_NAME | URL-safe 識別碼（小寫、連字號） | `demo-service` |
| `{{GROUP_ID}}` | arguments.yml | Maven groupId | `com.example` |
| `{{ARTIFACT_ID}}` | arguments.yml | Maven artifactId | `demo` |
| `{{BASE_PACKAGE}}` | arguments.yml | Java base package（dot-separated） | `com.example.demo` |
| `{{BASE_PACKAGE_PATH}}` | derived from BASE_PACKAGE（`.` → `/`） | 檔案系統路徑 | `com/example/demo` |
| `{{JAVA_VERSION}}` | arguments.yml | Java 版本（`<java.version>`） | `25` |
| `{{SPRING_BOOT_VERSION}}` | arguments.yml | Spring Boot parent 版本 | `4.0.6` |
| `{{CUCUMBER_VERSION}}` | arguments.yml | Cucumber 版本 | `7.34.3` |
| `{{JJWT_VERSION}}` | arguments.yml | JJWT 版本 | `0.12.6` |
| `{{SPRINGDOC_VERSION}}` | arguments.yml | SpringDoc OpenAPI 版本 | `3.0.3` |
| `{{POSTGRES_IMAGE_VERSION}}` | arguments.yml | docker-compose `postgres:` 影像 tag | `18` |
| `{{DB_NAME}}` | arguments.yml | 本機 PostgreSQL DB 名稱 | `demo` |
| `{{DB_USER}}` | arguments.yml | 本機 PostgreSQL 帳號 | `postgres` |
| `{{DB_PASSWORD}}` | arguments.yml | 本機 PostgreSQL 密碼 | `postgres` |
| `{{DB_PORT}}` | arguments.yml | 本機 PostgreSQL host port | `5432` |
| `{{SPECS_ROOT_DIR}}` | arguments.yml | 規格檔案根目錄 | `specs` |
| `{{BOUNDARY_YML}}` | arguments.yml | boundary 清單（通常 `specs/architecture/boundary.yml`） | `specs/architecture/boundary.yml` |
| `{{CONTRACTS_DIR}}` | arguments.yml | boundary operation contract directory；Java `web-service` contract files 為 OpenAPI（由 `/aibdd-form-api-spec` 產出） | `specs/backend/contracts` |
| `{{FEATURE_SPECS_DIR}}` | arguments.yml（`/aibdd-discovery` bind 後展開） | Discovery accepted rule / behavior truth 根 | `specs/backend/packages/01-計費/features` |
| `{{ACTIVITIES_DIR}}` | arguments.yml（bind 後展開） | Discovery accepted `.activity` truth 根 | `specs/backend/packages/01-計費/activities` |
| `{{DATA_DIR}}` | arguments.yml | boundary state truth directory；Java `web-service` state files 為 DBML（由 `/aibdd-form-entity-spec` 產出） | `specs/backend/data` |
| `{{DEV_CONSTITUTION_PATH}}` | arguments.yml | 開發基礎建設 bridge guideline | `.aibdd/dev-constitution.md` |
| `{{BDD_CONSTITUTION_PATH}}` | arguments.yml | bdd-stack 憲法樹之 §5.1 檔名軸錨點 | `.aibdd/bdd-stack/project-bdd-axes.md` |
| （鍵）`RED_PREHANDLING_HOOK_REF` | arguments.yml §9 | Red 前 schema-analysis／flyway-migration gate；`/aibdd-red-execute` 進 Red 前必讀 | `.aibdd/bdd-stack/prehandling-before-red-phase.md` |

推導規則：

- `PROJECT_SLUG` = PROJECT_NAME 轉小寫、空格換連字號、移除特殊字元（與 python-e2e 同 `slugify` 演算法）。
- `BASE_PACKAGE_PATH` = `BASE_PACKAGE` 中 `.` 換成 `/`。
- `PROJECT_DESCRIPTION` 預設為 `"${PROJECT_NAME} — BDD Workshop Java E2E"`，若 arguments.yml 已提供則以該值為準。

Starter 安全邊界：

- `${PROJECT_ROOT}/.aibdd/arguments.yml` 必須已存在；starter 不建立、不改寫 `specs/`。
- `project_dir` 必須是已 kickoff 的 backend repo root；若 arguments path 不在同一 repo root，停止並要求重新指定。

---

## 與 Python E2E 的差異

| 項目 | Python E2E | Java E2E |
|------|------------|----------|
| Framework | FastAPI + SQLAlchemy 2.0 | Spring Boot 4.0.6 + Spring `JdbcClient`（**非** JPA） |
| Test Runner | Behave | Cucumber 7.34.3 + JUnit Platform Suite |
| Cucumber 入口 | `behave` CLI + `behave.ini` | `RunCucumberTest`（`@Suite + @IncludeEngines("cucumber")`），由 `mvn test` 觸發 |
| HTTP 測試 | `httpx.TestClient` | `MockMvc`（由 `@AutoConfigureMockMvc` 注入；非 `TestRestTemplate`） |
| DB Container | Testcontainers Python（`environment.py` 顯式 start／stop） | Testcontainers Java（`@ServiceConnection` 由 Spring Boot 自動掌管生命週期） |
| Migration | Alembic（`alembic/env.py` + `alembic.ini`） | Flyway（`src/main/resources/db/migration/V*__*.sql`，無獨立 ini） |
| Build Tool | pip + `requirements.txt` + `pyproject.toml` | Maven (`pom.xml`) |
| JWT | PyJWT | JJWT 0.12.x（`Jwts.builder().subject(...).signWith(key)`） |
| Package 結構 | 平坦目錄 + `__init__.py` | 分層 package（`${BASE_PACKAGE}` 可配置） |
| Scenario context | Behave context 直接掛屬性（`context.last_response`） | `@Component @ScenarioScope ScenarioContext`（Spring DI 注入） |
| DB Cleanup | `after_scenario` TRUNCATE CASCADE | `@Before(order = 0)` DELETE + RESET sequence |
| 共用 Then matcher 集 | `tests/features/steps/common_then/*.py` 拆檔 | `steps/common_then/CommonThen.java` 單檔多 method |
| Health smoke | `tests/features/HealthCheck.feature` + `steps/health_check.py` | `src/test/resources/features/HealthCheck.feature` + `steps/HealthSteps.java` |
| Pre-Red hook fill | `schema-analysis`（Alembic autogenerate） | `schema-analysis`（手寫 Flyway forward migration） |

---

## 環境需求

- **Java**: 25+（與 `pom.xml` `<java.version>` 對齊；維持與 Spring Boot 4 baseline 一致）。
- **Maven**: 需本機安裝 Maven（3.9+）；直接使用 `mvn` 指令。
- **Docker**: 需要執行中的 Docker daemon——
  - **Acceptance**：Testcontainers 動態啟動 `postgres:latest`（由 `TestcontainersConfiguration` 控制 image tag）。
  - **Local 開發**：`docker compose up -d` 啟動 `postgres:${POSTGRES_IMAGE_VERSION}`。
- **PostgreSQL**: 不需手動安裝；本機 `docker-compose` 與測試 Testcontainers 都自動拉取 image。
- **作業系統**: macOS / Linux / Windows（Windows 需 Docker Desktop + WSL2 backend）。

---

## Template 檔案對照表

template 檔名規則：`__` 表示路徑分隔符 `/`；filename 中的 `BASE_PKG` 會被 generator 替換為 `${BASE_PACKAGE_PATH}`。template 內容用 Python `string.Template` 的 `${VAR}` 語法做變數替換。

| Template 檔名（`__` = `/`，`BASE_PKG` = `${BASE_PACKAGE_PATH}`） | 輸出路徑 |
|-------------------------------------------------------------------|----------|
| `pom.xml` | `pom.xml` |
| `docker-compose.yml` | `docker-compose.yml` |
| `.gitattributes` | `.gitattributes` |
| `.aibdd__dev-constitution.md` | `.aibdd/dev-constitution.md` |
| `.aibdd__bdd-stack__project-bdd-axes.md` | `.aibdd/bdd-stack/project-bdd-axes.md` |
| `.aibdd__bdd-stack__acceptance-runner.md` | `.aibdd/bdd-stack/acceptance-runner.md` |
| `.aibdd__bdd-stack__step-definitions.md` | `.aibdd/bdd-stack/step-definitions.md` |
| `.aibdd__bdd-stack__fixtures.md` | `.aibdd/bdd-stack/fixtures.md` |
| `.aibdd__bdd-stack__feature-archive.md` | `.aibdd/bdd-stack/feature-archive.md` |
| `.aibdd__bdd-stack__prehandling-before-red-phase.md` | `.aibdd/bdd-stack/prehandling-before-red-phase.md` |
| `src__main__java__BASE_PKG__Application.java` | `src/main/java/${BASE_PACKAGE_PATH}/Application.java` |
| `src__main__java__BASE_PKG__controller__HealthController.java` | `src/main/java/${BASE_PACKAGE_PATH}/controller/HealthController.java` |
| `src__main__java__BASE_PKG__security__JwtTokenFilter.java` | `src/main/java/${BASE_PACKAGE_PATH}/security/JwtTokenFilter.java` |
| `src__main__java__BASE_PKG__security__CurrentUser.java` | `src/main/java/${BASE_PACKAGE_PATH}/security/CurrentUser.java` |
| `src__main__resources__application.yaml` | `src/main/resources/application.yaml` |
| `src__test__java__BASE_PKG__RunCucumberTest.java` | `src/test/java/${BASE_PACKAGE_PATH}/RunCucumberTest.java` |
| `src__test__java__BASE_PKG__config__CucumberSpringConfiguration.java` | `src/test/java/${BASE_PACKAGE_PATH}/config/CucumberSpringConfiguration.java` |
| `src__test__java__BASE_PKG__config__TestcontainersConfiguration.java` | `src/test/java/${BASE_PACKAGE_PATH}/config/TestcontainersConfiguration.java` |
| `src__test__java__BASE_PKG__cucumber__DatabaseCleanupHook.java` | `src/test/java/${BASE_PACKAGE_PATH}/cucumber/DatabaseCleanupHook.java` |
| `src__test__java__BASE_PKG__cucumber__JwtHelper.java` | `src/test/java/${BASE_PACKAGE_PATH}/cucumber/JwtHelper.java` |
| `src__test__java__BASE_PKG__cucumber__ScenarioContext.java` | `src/test/java/${BASE_PACKAGE_PATH}/cucumber/ScenarioContext.java` |
| `src__test__java__BASE_PKG__steps__HealthSteps.java` | `src/test/java/${BASE_PACKAGE_PATH}/steps/HealthSteps.java` |
| `src__test__java__BASE_PKG__steps__common_then__CommonThen.java` | `src/test/java/${BASE_PACKAGE_PATH}/steps/common_then/CommonThen.java` |
| `src__test__java__BASE_PKG__steps__helpers__ScenarioContextHelper.java` | `src/test/java/${BASE_PACKAGE_PATH}/steps/helpers/ScenarioContextHelper.java` |
| `src__test__resources__features__HealthCheck.feature` | `src/test/resources/features/HealthCheck.feature` |

額外建立的空目錄（無 template）：

- `src/main/java/${BASE_PACKAGE_PATH}/model/`
- `src/main/java/${BASE_PACKAGE_PATH}/repository/`
- `src/main/java/${BASE_PACKAGE_PATH}/service/`
- `src/main/resources/db/migration/`
- `src/main/resources/static/`
- `src/main/resources/templates/`

未由 starter 寫入、需另行產生的檔案：

- `.gitignore`：請自行建立或從既有 Spring Boot 專案複製過來。

---

## 驗證步驟

完成骨架建立後，確認以下事項：

1. **檔案完整性**：所有 template 對照表中的檔案都已寫入目標路徑（含 `.aibdd/dev-constitution.md`、`.aibdd/bdd-stack/project-bdd-axes.md`、`prehandling-before-red-phase.md` 與其餘 `bdd-stack/*.md`）；且 `arguments.yml` §9 含 `RED_PREHANDLING_HOOK_REF`。
2. **Placeholder 替換**：專案中不應殘留任何 `{{...}}` 或未替換的 `${PROJECT_NAME}` / `${BASE_PACKAGE}` / `${BASE_PACKAGE_PATH}` / `${ARTIFACT_ID}` 等變數。
3. **目錄結構**：`src/main/java/${BASE_PACKAGE_PATH}/{model,repository,service}/`、`src/main/resources/{db/migration,static,templates}/` 都已建立（即使是空目錄）。
4. **編譯測試**：`mvn clean compile` 能正常完成（首次執行會下載依賴，需網路）。
5. **Cucumber Dry Run**：`mvn test -Dcucumber.execution.dry-run=true` 不報 `UndefinedStepException` / `AmbiguousStepDefinitionException`；應收集到至少 `HealthCheck.feature` 的一個 scenario（dry-run 不啟動完整 Spring context，僅檢 step matcher）。
6. **執行測試**：`mvn test` 能完整跑 `RunCucumberTest`（需 Docker daemon）；至少包含 `HealthCheck.feature` 一個 scenario。
7. **本地開發啟動**：`docker compose up -d` 啟動 starter 內建的 PostgreSQL，再 `mvn spring-boot:run`（用 `Application.main`）即可手動 hit endpoint。
8. **Migration**：啟動時 Flyway 自動套用 `src/main/resources/db/migration/V*__*.sql`（starter 預設無 migration 檔，本步驟在 `/aibdd-discovery` → schema-analysis 後才有資料可驗證）。

---

## 安全規則

- 不覆蓋已存在的檔案（跳過並回報）。
- 不建立 feature-specific 程式碼（業務 Controllers／Services／Repositories／Models／Step Definitions／`.feature`）。
- 例外：`HealthCheck.feature` + `HealthController.java` + `HealthSteps.java` 為 **walking skeleton starter smoke**，僅驗證 `/health`，不屬於產品需求 BDD。
- 例外：`security/JwtTokenFilter.java` + `security/CurrentUser.java` 為 **starter cross-cutting infra**（JWT bearer 解析、未受保護端點放行），非 feature-specific 業務碼；可由功能模組 `request → CurrentUser.getId(request)` 直接取 user id。
- 例外：`.aibdd/dev-constitution.md`、`.aibdd/bdd-stack/*.md`（含 `project-bdd-axes.md`）為 **AIBDD bridge／runtime guideline**，非產品程式碼亦非業務 BDD。
- 不執行 `mvn install`、`mvn flyway:migrate`、`docker compose up`。
- `DatabaseCleanupHook` 中的 DELETE／RESET sequence 語句需使用者在加入 entity 後自行填入。

---

## 完成後引導

```
Walking skeleton 已建立完成。

下一步：
1. cd ${PROJECT_ROOT}
2. mvn clean test                                # 執行 RunCucumberTest（需 Docker）
3. docker compose up -d && mvn spring-boot:run   # 本地手動啟動 app（需 Docker）
5. /aibdd-discovery — 開始需求探索

新增功能：
- 在 src/test/resources/features/<current_spec_package>/ 下新增 .feature
- 在 src/test/java/${BASE_PACKAGE_PATH}/steps/<current_spec_package>/ 下新增對應 Steps
- 在 src/main/java/${BASE_PACKAGE_PATH}/{controller,service,repository,model}/ 下實作
- 如需新增資料表，建立 src/main/resources/db/migration/V{N}__xxx.sql
```
