package com.example.backend.steps;

import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

public class HealthSteps {

    @Autowired
    private MockMvc mockMvc;

    private MvcResult lastResponse;

    @When("I request the health endpoint")
    public void iRequestTheHealthEndpoint() throws Exception {
        lastResponse = mockMvc.perform(get("/health")).andReturn();
    }

    @Then("the health check response is OK")
    public void theHealthCheckResponseIsOk() throws Exception {
        assertNotNull(lastResponse, "No response received");
        assertEquals(200, lastResponse.getResponse().getStatus(),
                "Expected HTTP 200, got " + lastResponse.getResponse().getStatus());
        String body = lastResponse.getResponse().getContentAsString();
        assertEquals("{\"status\":\"ok\"}", body,
                "Expected {\"status\":\"ok\"}, got " + body);
    }
}
