Feature: App smoke
  Validates the Walking Skeleton shell: root redirect and a visible landing heading.
  MSW is optional for this scenario (no API calls).

  Scenario: Root URL redirects to the default landing page
    Given I open the app root
    Then I see the default landing page
