# java-e2e × spectrum：custom StepDefinition 可用的框架 library

適用前提（雙重 gate）：`STARTER_VARIANT=java-e2e` 且 `INSTALL_SPECTRUM=true`（已安裝 specformula）。
未安裝框架或其他 variant 不讀本檔。本檔只規範「手寫 custom step def 時該用哪些框架介面」，
不改變 custom 的判定與契約（那在 dsl-refine 的 custom-isa-placement）。

以下介面皆為 Spring Bean，於 step def 建構子或欄位 `@Autowired` 注入即可。

## 1. `ScenarioContextAccessor` — VAR 讀寫

`ai.specformula.core.context.ScenarioContextAccessor`

```java
void   putObject(String key, Object value);  // 存任意物件（export_vars 寫回走這）
Object get(String key);                      // 取物件；不存在回 null
```

用法（alias 慣例 `alias + ".id"`）：

```java
Object userId = scenarioContext.get(alias + ".id");     // 讀前面 entity_setup 捕獲的 id
if (userId == null) throw new IllegalStateException("找不到 '" + alias + "'，請先建立並匯出 " + alias + ".id");
scenarioContext.putObject(alias + ".autoRoleId", roleId); // export_vars 寫回，供後續 step 引用
```

取 last response（斷言型 custom）：注入的是 core 的 `ScenarioContext`（實作了 Accessor）時可用
`getLastResponse()` → `ai.specformula.core.http.TestResponse`：

```java
int    getStatus();                        // HTTP 狀態碼
String getBody();                          // 回應 body（raw string）
Map<String, List<String>> getHeaders();    // 回應 headers
```

## 2. `FeatureArgumentResolver` — VAR／CAS／TIME 三系統解析

`ai.specformula.core.helper.FeatureArgumentResolver`

```java
// 解析 $var / ${var} 插值 / @time("now-1d") / @date("2025-12-16") / @localtime("09:00:00")
// 回傳：原字串、Context 內任意物件、或 java.time 型別
Object resolveVariable(String value);

// 期望值解析＋比對驗證（驗證入口）：依序處理 &constraint CAS（如 &gt(5)&lt(10)，過→回 null）、
// 時間戳比對（秒精度）、數值比對（double）；皆不適用時回傳解析後期望值由呼叫端自行比對。
// 驗證失敗擲 AssertionError（fieldName/entityName 用於錯誤訊息定位）
Object resolveAndValidate(String expectedValue, Object actualValue, String fieldName, String entityName);

// 型別感知相等比對：自動做 $var 解析、JDBC 型別正規化（Timestamp→java.time）、
// BigDecimal compareTo、時間秒精度、"0"/"1"↔Boolean、跨型別字串比對
boolean valuesEqual(Object expected, Object actual);
```

用法（custom 收到 DataTable 逐格解）：

```java
Object v = resolver.resolveVariable(cell);                       // "$王業務.id" → context 內實際值
Object r = resolver.resolveAndValidate(expected, actual, col, "tb_credit_review");
if (r != null && !resolver.valuesEqual(r, actual)) { /* 不相等 → 斷言失敗 */ }
```

## 3. `MockTime` — 受控時間

`ai.specformula.spring.time.MockTime`（@FunctionalInterface）

```java
ZonedDateTime now();   // time_control 設定的模擬時間（UTC）；未設定時為實際 UTC
```

custom 需要「現在」一律 `mockTime.now()`。

## 4. builtin instruction beans — 委派 builtin 行為

`ai.specformula.spring.instruction.*`；javadoc 明示「提供 custom step 開發者…的能力，不依賴 Cucumber DataTable」。
DataTable 形狀皆為 `List<Map<String, String>>`（欄位名 → 值；值可含 `$var`／`&CAS`／`@time` 符號，由框架解析）。

```java
// 準備測試資料（INSERT INTO）
void EntitySetupInstruction.setup(String entityName, List<Map<String,String>> dataTable) throws Exception;

// 驗證資料存在／欄位正確
void EntityValidateInstruction.assertExists(String entityName, List<Map<String,String>> dataTable) throws Exception;

// 驗證資料不存在
void EntityNonExistenceValidateInstruction.assertNotExists(String entityName, List<Map<String,String>> dataTable) throws Exception;

// 呼叫 API（summary 對應 OpenAPI operation；token 帶 actor 認證）
void ApiCallInstruction.invokeWithActor(String summary, String token, List<Map<String,String>> dataTable) throws Exception;
void ApiCallInstruction.invokeWithoutActor(String summary, List<Map<String,String>> dataTable) throws Exception;

// 驗證前一次呼叫的回應（statusCode 字面值，如 "201"）
void ResponseValidateInstruction.validate(String summary, String statusCode, List<Map<String,String>> dataTable) throws Exception;

// 設定模擬時間（等同 time_control 指令）
void TimeControlInstruction.setTime(String timeString);
```

用法（複合前置 custom 委派 builtin，勿重寫 DB 邏輯）：

```java
entitySetup.setup("tb_user", List.of(Map.of(
    ">" + alias + ".id", "<user_id",       // VAR 捕獲照 ISA 符號寫，框架會處理
    "user_name", alias,
    "updated_by", "0", "updated_at", "@time(\"now\")")));
entitySetup.setup("tb_employee_profile", List.of(Map.of("user_id", "$" + alias + ".id", ...)));
```

## 5. Spring 原生

`JdbcTemplate`／`DataSource`（builtin 委派不合用時的直接 DB 存取，寫入須冪等）、`MockMvc`。

## 使用規則

- **符號一律交給框架解**：`$…`／`${…}`／`&…`／`@time/@date` 用 `FeatureArgumentResolver` 或直接把含符號的
  值交給 instruction beans，【嚴禁】自己寫 regex parse 符號。
- **時間一律 `MockTime.now()`**，【嚴禁】`ZonedDateTime.now()`／`LocalDateTime.now()`（脫離 time_control）。
- **VAR 讀寫一律 `ScenarioContextAccessor`**，【嚴禁】static field／ThreadLocal 私存跨步驟狀態。
- 能委派 builtin instruction bean 就委派；只有 builtin 表達不了的部分才手寫。
- 【嚴禁】為 builtin 句型另註冊 matcher（框架已註冊，重複註冊衝突）。

## 受測產品側的相依（不在 step def 內做，但 RED 可能踩到）

- `Authenticator`（`ai.specformula.spring.auth.Authenticator`）：`String getToken(Object actorId)` → Bearer token。
  專案須實作為 Spring Bean，api_call 的 `UID="$…"` 認證靠它；未實作時框架用 DefaultAuthenticator 於呼叫時
  拋錯——屬產品缺口，紅燈訊息會指向它。
- `MockTime`：產品程式取「現在時間」須注入它，時間才受 ISA 控制。
