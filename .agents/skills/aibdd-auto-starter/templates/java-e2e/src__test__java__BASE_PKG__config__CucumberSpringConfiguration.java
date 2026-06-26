package ${BASE_PACKAGE}.config;

import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;

@CucumberContextConfiguration
@SpringBootTest${SPECFORMULA_SPRINGBOOTTEST_PROPS}
@AutoConfigureMockMvc
@Import(TestcontainersConfiguration.class)
public class CucumberSpringConfiguration {
}
