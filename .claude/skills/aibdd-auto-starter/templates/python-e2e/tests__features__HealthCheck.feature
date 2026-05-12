Feature: Health check (walking skeleton smoke)
  Starter-only: verifies the FastAPI app exposes GET /health.
  Replace or extend with product scenarios from /aibdd-discovery.

  Scenario: Service reports healthy
    When I request the health endpoint
    Then the health check response is OK
