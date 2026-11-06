# Writing scenarios

## Contents

- Where Gherkin sits
- Example Mapping
- Scenario style
- Review checklist

## Where Gherkin sits

```text
Product vision, capabilities      plain docs (README, docs/, specs)
  Feature                         one capability a user recognizes
    Rule                          one business rule
      Scenario  @ID               one concrete example of the rule
        Given / When / Then       context, action, observable outcome
```

Keep vision, personas, and rationale out of `.feature` files. The free-text description under `Feature:` may hold a short user story or a link to the spec; longer prose rots there because no test fails when it goes stale.

`Rule` needs Gherkin 6 or later. All three recommended frameworks parse it in current versions. If an older parser rejects it, upgrade before falling back to comments.

## Example Mapping

A 25-minute conversation per story, run by the agent with the user or by the agent alone from a spec, then confirmed. Four card colors:

| Card | Holds | Becomes |
|------|-------|---------|
| Story (yellow) | The capability under discussion | `Feature` |
| Rule (blue) | One business rule or acceptance criterion | `Rule` |
| Example (green) | A concrete case that illustrates a rule, with real values | `Scenario` |
| Question (red) | Something nobody present can answer | A question to the user; not a scenario |

Read the map before writing any Gherkin:

- Many red cards: the story is not ready. Ask, do not guess.
- Many blue cards: the story is too big. Split it.
- A rule with many green cards: the rule is probably several rules, or the examples are unit-level edge cases.
- A rule with no green card: nobody understands it well enough yet.

Present the map to the user as a compact list:

```text
Story: Launch installed games
  Rule: Only installed games can be launched
    Example: Launch "Hades" when installed -> it starts
    Example: Launch "Celeste" when not installed -> offered install, nothing starts
  Rule: Successfully launched games appear in play activity
    Example: Launch "Hades" -> activity shows "Hades" played today
  Question: Does a launch that crashes within 5 seconds count as played?
```

## Scenario style

- **Declarative, not imperative.** `When I launch "Hades"` describes intent. `When I click the Play button on the Hades tile` describes today's UI. The first survives redesigns and reads as a rule.
- **One behavior per scenario.** One `When`. A second `When` usually means a second scenario.
- **Then asserts outcomes the user can observe** (state, message, record), not internal calls.
- **Real values, few of them.** `"Hades"` beats `a game`; include only data that matters to the rule. Hide incidental setup in step definitions.
- **Name the scenario after the example**, not the test technique: `Launch an uninstalled game`, not `Negative test 2`.
- **First person or a named persona, consistently** across the project.
- **Step text is the step-definition API.** Reuse existing phrasings before inventing new ones; grep the step definitions first.
- **Scenario Outline** only when rows differ in data, not in rule. Keep tables small; large matrices go to unit tests carrying the same ID.

Before and after:

```gherkin
# Imperative, two behaviors, incidental data
Scenario: Test launch
  Given I am on "/library"
  And I click "#game-42"
  When I click "#play"
  And I go to "/activity"
  Then I see ".row" containing "Hades" and "2026-11-05"

# Declarative, one behavior
@GL-001
Scenario: Launch an installed game
  Given "Hades" is installed
  When I launch "Hades"
  Then "Hades" starts
  And my activity shows that I played "Hades"
```

## Review checklist

- Every scenario has exactly one ID tag, and no ID appears twice.
- Each `Rule` has at least one scenario; each scenario sits under the rule it illustrates.
- No selectors, URLs, CSS classes, or HTTP verbs in step text unless the API is the product.
- No step joins two actions with "and".
- `Background` holds only setup every scenario in the file needs.
- Open questions are listed for the user, not encoded as assumptions.
