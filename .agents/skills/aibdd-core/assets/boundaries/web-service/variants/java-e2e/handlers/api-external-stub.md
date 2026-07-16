# Handler template (java-e2e): external-stub

kind-constants `api.yml` `red_execute` B 面（樁）的具體 Java 填空模版：佈建 in-process WireMock
讓外部 operation 對指定請求回傳指定回應。用 **WireMock 的 Java DSL `stubFor(...)`**。
需 [`../test-doubles/wiremock.md`](../test-doubles/wiremock.md) 佈建的替身 server bean。

step def 放 `steps/<function-package-slug>/external_stub/{{Dep}}StubSteps.java`，
`@Autowired` 注入 wiremock.md 的 `WireMockServer` bean。

## 對應句式（api；matcher 取 kind-constants api.yml format 主幹）

- 成功／業務結果體：`外部服務 "…" 對 … 回應, with JSON:`（Given，json；狀態 200，body 由 JSON 帶入）— 主模版，見下。
- HTTP 錯誤狀態：`外部服務 "…" 對 … 回應狀態 {int}`（Given，無 body）— 變體，見下。

**兩維度別混淆**：「外部業務否決」（如簽核 rejected）是**同 200 換 body**，用主模版填否決 payload 即可；
「外部服務故障」（5xx/4xx）才用錯誤狀態變體。前者測 SUT 對否決結果的處理，後者測 SUT 對外部失敗的韌性。

## 模版

```java
package ${BASE_PACKAGE}.steps.{{package_slug}}.external_stub;

import com.github.tomakehurst.wiremock.WireMockServer;
import io.cucumber.java.en.Given;
import org.springframework.beans.factory.annotation.Autowired;

import static com.github.tomakehurst.wiremock.client.WireMock.*;

public class {{Dep}}StubSteps {

    // openapi truth：operation → 對外 method + path
    private static final String METHOD = "{{http_method}}";
    private static final String PATH   = "{{request_path}}";

    @Autowired WireMockServer wireMock;

    @Given("外部服務 {string} 對 {{operation}} 回應")
    public void 對operation回應(String boundary, String responseJson) {
        // responseJson 依 response schema truth 填空（不得發明 truth 外欄位）
        wireMock.stubFor(request(METHOD, urlPathEqualTo(PATH))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody(responseJson)));
    }
}
```

## 變體（HTTP 錯誤狀態：`… 回應狀態 {int}`）

模擬外部服務故障（5xx/4xx），測 SUT 韌性；同一 step class 內另加：

```java
@Given("外部服務 {string} 對 {{operation}} 回應狀態 {int}")
public void 對operation回應狀態(String boundary, int status) {
    wireMock.stubFor(request(METHOD, urlPathEqualTo(PATH))
        .willReturn(aResponse().withStatus(status)));
}
```

## 填空 slot

- `{{Dep}}`／`{{dep}}`／`{{package_slug}}`：同 interaction-verifier.md。
- `{{operation}}`：kind-constants format 的 operation 具名參數字面。
- `{{http_method}}`／`{{request_path}}`：openapi truth 該 operation 的 method 與 path。
- status／headers：預設 200＋json；truth 有宣告特定 response 狀態/型態時依 truth 調整。

## Forbidden（承 kind-constants api.yml `red_execute.forbidden`）

- 不真連外——只對本地 in-process 替身 `stubFor` 佈樁。
- response payload 只填 response schema truth 宣告過的欄位，不發明。
- 一個 entry 的 B／E 共用 wiremock.md 的同一 `WireMockServer` bean。
