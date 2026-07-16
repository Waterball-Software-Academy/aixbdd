# Handler template (java-e2e): interaction-verifier

kind-constants `api.yml` `red_execute` E 面（互動驗證）的具體 Java 填空模版：驗證 SUT 對外部
operation 的呼叫（次數／送出 payload／未呼叫），用 **in-process WireMock 的 Java DSL `verify(...)`**。
需 [`../test-doubles/wiremock.md`](../test-doubles/wiremock.md) 佈建的替身 server bean。

step def 放 `steps/<function-package-slug>/external_stub/{{Dep}}InteractionSteps.java`，
`@Autowired` 注入 wiremock.md 的 `WireMockServer` bean。

## 對應句式（api；matcher 取 kind-constants api.yml 的 format 主幹）

- payload：`外部服務 "…" 的 … 應被呼叫並送出, with table:`（data_table）— 主模版，見下。
- 次數：`外部服務 "…" 的 … 應被呼叫 {int} 次` — 變體 A。
- 反面：`外部服務 "…" 的 … 不應被呼叫` — 變體 B。

## 模版（payload-bearing 主變體）

```java
package ${BASE_PACKAGE}.steps.{{package_slug}}.external_stub;

import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.http.RequestMethod;
import com.github.tomakehurst.wiremock.matching.RequestPatternBuilder;
import io.cucumber.datatable.DataTable;
import io.cucumber.java.en.Then;
import org.springframework.beans.factory.annotation.Autowired;

import java.time.Duration;
import java.util.Map;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;

public class {{Dep}}InteractionSteps {

    // openapi truth：operation → 對外 method + path（如 submitSignoff → POST /signoff-requests）
    private static final RequestMethod METHOD = RequestMethod.fromString("{{http_method}}");
    private static final String PATH = "{{request_path}}";

    // DataTable 中文表頭 → request schema 屬性（僅 truth 宣告欄位；不得發明）
    private static final Map<String, String> FIELD_TO_PROPERTY = Map.of(
        {{field_header}}, "{{schema_property}}"   // 每欄一筆
    );

    @Autowired WireMockServer wireMock;

    @Then("外部服務 {string} 的 {{operation}} 應被呼叫並送出, with table:")
    public void 應被呼叫並送出(String boundary, DataTable table) {
        Map<String, String> expected = table.asMaps().get(0);
        RequestPatternBuilder pattern = new RequestPatternBuilder(METHOD, urlPathEqualTo(PATH));
        expected.forEach((header, value) -> {
            String prop = FIELD_TO_PROPERTY.get(header);
            assertThat(prop).as("欄位「%s」未在 request schema truth 宣告", header).isNotNull();
            pattern.withRequestBody(matchingJsonPath("$." + prop, equalTo(value)));
        });
        // E 正面：bounded-wait（同步外呼立即滿足；非同步則等到 timeout）；DSL verify 失敗擲 AssertionError
        await().atMost(Duration.ofSeconds(5)).pollInterval(Duration.ofMillis(200))
            .untilAsserted(() -> wireMock.verify(pattern));
    }
}
```

## 變體 A（次數：`… 應被呼叫 {int} 次`）

```java
@Then("外部服務 {string} 的 {{operation}} 應被呼叫 {int} 次")
public void 應被呼叫次數(String boundary, int times) {
    await().atMost(Duration.ofSeconds(5)).pollInterval(Duration.ofMillis(200))
        .untilAsserted(() -> wireMock.verify(exactly(times),
            new RequestPatternBuilder(METHOD, urlPathEqualTo(PATH))));
}
```

## 變體 B（反面：`… 不應被呼叫`）

反面**不無界等待**：以觀察窗（kind-constants red_execute 的 window 預設，如 2s）等滿後斷言 0 次。
```java
@Then("外部服務 {string} 的 {{operation}} 不應被呼叫")
public void 不應被呼叫(String boundary) {
    RequestPatternBuilder pattern = new RequestPatternBuilder(METHOD, urlPathEqualTo(PATH));
    // 觀察窗滿之前若曾出現即失敗；滿窗後仍為 0 才通過（不無界輪詢）
    await().during(Duration.ofSeconds(2)).atMost(Duration.ofSeconds(3))
        .until(() -> wireMock.countRequestsMatching(pattern.build()).getCount() == 0);
}
```

## 填空 slot

- `{{Dep}}`／`{{dep}}`：entry.name → PascalCase／camelCase；`{{package_slug}}`：function package slug（snake_case）。
- `{{operation}}`：kind-constants format 的 operation 具名參數字面（保留為 Cucumber 表達式常量或 regex 群組）。
- `{{http_method}}`／`{{request_path}}`：openapi truth 該 operation 的 method 與 path。
- `FIELD_TO_PROPERTY`：DataTable 各中文表頭 → request schema 屬性；只列 truth 宣告欄位。

## Forbidden（承 kind-constants api.yml `red_execute.forbidden`）

- 不真連外部平台——只查本地 in-process 替身 server（`wireMock.verify` / `countRequestsMatching`）。
- 只斷言 request schema truth 宣告過的欄位；DataTable 出現未宣告欄位 → 停下回報，不硬斷。
- E 正面 timeout 必填（bounded-wait）；反面以觀察窗判定，不無界等待。
- 不得在此 handler 內發 MockMvc／打 SUT 自身端點；本 handler 只查替身收到的 outbound。
