@game-launch
Feature: Launch installed games

  Rule: Only installed games can be launched

    @GL-001
    Scenario: Launch an installed game
      Given "Hades" is installed
      When I launch "Hades"
      Then "Hades" starts

    @GL-002
    Scenario: Launch a game that is not installed
      Given "Celeste" is not installed
      When I launch "Celeste"
      Then I am offered to install "Celeste"
      And nothing starts

  Rule: Successfully launched games appear in play activity

    @GL-002
    Scenario: Activity records a launch
      Given "Hades" is installed
      When I launch "Hades"
      Then my activity shows that I played "Hades"

    Scenario: Failed launch is not recorded
      Given "Hades" is installed but its executable is missing
      When I launch "Hades"
      Then my activity does not show "Hades"
