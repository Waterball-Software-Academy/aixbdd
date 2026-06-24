### q6-install-spectrum
- prompt: 是否要安裝 aibdd-spectrum 測試框架？
- kind: CON
- options: yes | no
- recommendation: no
- answer.raw: {{Q6_ANSWER}}
- resolved_decision: { key: install_spectrum, value: {{INSTALL_SPECTRUM}} }
- status: {{Q6_STATUS}}

<!-- @guideline -->
決定是否在 starter 一併安裝 aibdd-spectrum（現名 specformula；ISA-based 測試框架，Cucumber + Spring Boot 參考實作）：
- `yes` — `install_spectrum = true`。auto-starter 會在 pom.xml 加入 specformula 依賴（`specformula-cucumber`、`specformula-testcontainer`、`specformula-dsl`，版本 0.0.5、test scope，從 Maven Central 取得）與 `specformula-dsl` preprocess plugin（`.dsl.feature` → `.isa.feature`）。
- `no` — `install_spectrum = false`，pom 保持乾淨。

僅 `java_e2e` stack 會實際安裝（specformula 目前只有 Java 參考實作）；其他 stack（`python_e2e`／`nextjs_playwright`）即使選 `yes`，pom 仍保持乾淨、不受影響。
reply token：`Q6: yes | no`
