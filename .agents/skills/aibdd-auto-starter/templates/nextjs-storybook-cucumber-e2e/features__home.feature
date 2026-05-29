Feature: Home page

  Background:
    Given I am on the home page

  Scenario: Page metadata
    Then the page title should be "${PROJECT_NAME} — Next.js starter kit"

  Scenario: "It works" message is visible
    Then I should see the heading "It works!"

  Scenario: Get started button renders
    Then I should see the button "Get started"

  Scenario: Responsive layout on mobile viewport
    When I resize the viewport to 375 x 812
    Then I should see the heading "It works!"
    And I should see the button "Get started"
