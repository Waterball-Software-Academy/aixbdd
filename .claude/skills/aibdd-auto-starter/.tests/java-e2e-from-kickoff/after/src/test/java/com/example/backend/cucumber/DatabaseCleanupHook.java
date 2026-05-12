package com.example.backend.cucumber;

import io.cucumber.java.Before;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

public class DatabaseCleanupHook {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private ScenarioContext scenarioContext;

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
