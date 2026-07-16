# Test-double (java-e2e): WireMock（in-process）

外部 API 依賴（kind=api）的替身配置。以 **in-process WireMock server**（測試 JVM 內嵌，免 Docker）
攔截 SUT 的 outbound HTTP，並把替身 base URL 覆寫進 SUT 設定鍵（entry.wiring.sut_property_overrides）。
是 kind-constants `api.yml` `red_execute` 的 java-e2e 具體實現 SSOT，由 RED_PREHANDLING_HOOK 佈建。

## 需要的測試套件（Maven；scope=test）

red-execute 用此替身／其 handler（external-stub／interaction-verifier）前，須確認專案 pom.xml
`<dependencies>` 已含下列；缺者由 red-execute 自動補進（scope=test）：

- `org.wiremock:wiremock` — in-process `WireMockServer` 與 client DSL；**需顯式 version**（如 `3.9.1`，非 spring-boot BOM 管理）。
- `org.awaitility:awaitility` — interaction-verifier 的 bounded-wait；由 spring-boot-dependencies BOM 管理，**version 可省**。

（其他 variant 的等效套件管理處與座標，見各 variant 的 test-double 檔。）

## 何時需要

isa.yml 內有 kind=api 的外部依賴 custom（handler `external-stub` 或 `interaction-verifier`）時，
per registry entry 一個 in-process WireMockServer（同 entry 的 B 佈樁與 E 查驗共用同一 server）。

## @TestConfiguration（每個 api 依賴一個 server bean）

放 `src/test/java/${BASE_PACKAGE}/config/{{Dep}}StubConfiguration.java`（`{{Dep}}` 由 entry.name 轉 PascalCase）：

```java
package ${BASE_PACKAGE}.config;

import com.github.tomakehurst.wiremock.WireMockServer;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.options;

@TestConfiguration(proxyBeanMethods = false)
public class {{Dep}}StubConfiguration {

    // in-process server，隨機 port（免 Docker）；整個 test JVM 共用一個
    static final WireMockServer SERVER = new WireMockServer(options().dynamicPort());
    static { SERVER.start(); }

    /** 覆寫 SUT 設定鍵（entry.wiring.sut_property_overrides 各鍵）指向替身 baseUrl()。 */
    @DynamicPropertySource
    static void overrideSutProperties(DynamicPropertyRegistry registry) {
        // 每個 sut_property_override 一行；鍵取自 registry entry.wiring.sut_property_overrides
        registry.add("{{sut_property}}", SERVER::baseUrl);
    }

    /** 供 handler step def 以 Java DSL 佈樁／查驗。 */
    @Bean
    WireMockServer {{dep}}WireMock() { return SERVER; }
}
```

於 `CucumberSpringConfiguration` 掛上：`@Import({{Dep}}StubConfiguration.class)`。

## 每情境重置（必做）

WireMockServer 跨情境共用，須每情境清樁與請求記錄，否則前一情境的樁／journal 汙染下一情境。
於 `DatabaseCleanupHook.@Before`（或等效 hook）加：`{{dep}}WireMock.resetAll();`。

## 填空 slot

- `{{Dep}}`／`{{dep}}`：registry entry.name 轉 PascalCase／camelCase。
- `{{sut_property}}`：entry.wiring.sut_property_overrides 每一鍵各一行 `registry.add(...)`。

## Forbidden

- 不得連真實外部服務——只用本地 in-process WireMock 替身。
- 不得硬編 port（`dynamicPort()`，base URL 一律 `SERVER.baseUrl()`）。
- 一個 entry 的 B／E 共用同一 `WireMockServer` bean，不另起第二個。
- 忘記 `resetAll()` → 情境間互相汙染，屬測試設計缺陷。
