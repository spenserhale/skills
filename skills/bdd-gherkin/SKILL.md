---
name: bdd-gherkin
description: "Write executable behavior specs in Gherkin and link them to unit, integration, and E2E tests through stable behavior IDs. Use when the user wants BDD, Gherkin, .feature files, Given/When/Then scenarios, acceptance criteria that run as tests, Example Mapping, or Cucumber-JS, pytest-bdd, or Reqnroll step definitions, or asks how to trace a feature or requirement to the tests that cover it, even if they never say BDD. Not for ordinary unit tests with no behavior spec; use a TDD skill. Not for product vision or capability docs; keep those in plain docs."
license: MIT
metadata:
  author: spenserhale
  version: "1.0"
---

# BDD with Gherkin

Gherkin holds the acceptance behavior a stakeholder would recognize; lower-level tests stay in the project's existing framework; a stable behavior ID such as `GL-001` ties them together. The spec is executable through step definitions and traceable through IDs, and those are two separate links.

```gherkin
@game-launch
Feature: Launch installed games

  Rule: Successfully launched games appear in play activity

    @GL-001
    Scenario: Launch an installed game
      Given "Hades" is installed
      When I launch "Hades"
      Then "Hades" starts
      And my activity shows that I played "Hades"
```

## Steps

1. **Read the stack and what exists.** Find existing `.feature` files, step definitions, the test runner, and the ID scheme in use (grep for `@[A-Z]+-[0-9]+`). Extend what is there instead of adding a second BDD framework. Pick the framework from the stack: Cucumber-JS for JavaScript/TypeScript, pytest-bdd for pytest, Reqnroll for .NET. Done when the framework, feature folder, and ID prefix are named.
2. **Map examples before writing Gherkin.** For each story, list rules, one or more concrete examples per rule, and open questions. Questions go back to the user, not into scenarios as guesses. Read `references/writing-scenarios.md` for Example Mapping and scenario style. Done when every rule has an example and every question is answered or recorded as open.
3. **Write the feature.** One `Feature` per capability, one `Rule` per business rule, one `Scenario` per example. Steps describe behavior in domain words, never clicks or selectors. Give every scenario a new ID tag; never reuse a retired ID. Done when each scenario has exactly one ID and reads as a single behavior.
4. **Wire step definitions.** Steps call the app through its UI, API, or domain interface and assert outcomes, reusing the project's fixtures, factories, and assertion helpers. Read `references/frameworks.md` for setup, step-definition examples, and tag filtering per framework. Done when the scenario runs and fails for the right reason before the feature exists, then passes after.
5. **Tag lower-level tests with the same ID.** Integration and unit tests that support a behavior carry its ID as metadata or in the test name, in that framework's idiom. A shared unit test may carry several IDs. Read `references/traceability.md` for per-framework tagging and reporting. Done when `python3 scripts/trace_ids.py` shows the new ID with its supporting tests and no errors.

## Gotchas

- Scenarios written as UI scripts (`When I click "#launch-btn"`) break on every redesign and hide the rule. Put interaction detail in step definitions or page objects.
- A step with "and" inside it (`When I install and launch "Hades"`) is two steps; split it so each can be reused and fail on its own.
- `Background` is for setup every scenario in the file truly shares. When only some need it, it makes the others lie about their preconditions.
- A `Scenario Outline` is one behavior with data variations and takes one ID. If rows describe different rules, they are separate scenarios.
- Duplicate step text across features must bind to one definition. Cucumber-JS and Reqnroll fail on ambiguous matches; resolve by rewording the step, not by narrowing the regex until it stops matching.
- pytest-bdd turns tags into pytest markers. With `--strict-markers`, unregistered `@GL-001` tags error out; register them or handle `pytest_bdd_apply_tag`.
- IDs document relationships; they do not prove coverage. An ID on a unit test says someone believed it supports that behavior. Say so when reporting a trace.
- Too many scenarios per feature is a smell: 3 to 8 per `Rule` is typical. Edge-case matrices belong in unit tests, tagged with the ID.

## Resources

- Read `references/writing-scenarios.md` when running Example Mapping or reviewing scenario wording.
- Read `references/frameworks.md` when installing or configuring Cucumber-JS, pytest-bdd, or Reqnroll, or writing step definitions.
- Read `references/traceability.md` when tagging unit or integration tests, choosing an ID scheme, or building a cross-suite report.
- Run `python3 scripts/trace_ids.py --help` before reading its source; it scans feature files and test sources and prints the ID matrix, untagged scenarios, duplicate IDs, and orphan IDs found in tests but in no feature.
- For red-green discipline inside each step definition and unit test, hand off to a TDD skill if one is installed.
