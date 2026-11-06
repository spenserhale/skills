# Traceability

Executable linking (step definitions) proves a scenario runs. Traceability (IDs) records which lower-level tests a team believes support that behavior. Keep both; they answer different questions.

```text
GL-001: Launch installed game and record activity
  E2E:          user launches game; activity appears        (the scenario itself)
  Integration:  successful launch persists an activity row
  Unit:         session timing; launch validation rules
```

## Contents

- ID scheme
- Tagging tests per framework
- Running everything for one ID
- Reporting
- Limits

## ID scheme

- Format `<PREFIX>-<NNN>`: prefix per feature area (`GL` for game launch), zero-padded number. The bundled script's default pattern is `[A-Z][A-Z0-9]{1,9}-\d{2,}`; pass `--pattern` for anything else.
- If the project already links tests to tracker keys (`PROJ-123`), decide with the user whether behavior IDs reuse them. Tracker tickets close; behaviors persist, so separate IDs usually age better.
- One ID per scenario. Never renumber, never reuse a retired ID; mark retired IDs in a comment or changelog so old reports still resolve.
- The feature-level tag (`@game-launch`) groups; the scenario-level tag (`@GL-001`) identifies.

## Tagging tests per framework

Use the framework's metadata mechanism where one exists, so the ID is filterable, not only greppable. A test supporting several behaviors lists every ID.

| Framework | Tag | Run one ID |
|-----------|-----|-----------|
| pytest | `@pytest.mark.behavior("GL-001", "GL-004")` | `pytest --behavior GL-001` (conftest below) |
| Jest / Vitest | ID in the name: `test('GL-001: persists activity after launch', ...)` | `npx vitest -t GL-001`, `npx jest -t GL-001` |
| Playwright Test | `test('...', { tag: '@GL-001' }, async ...)` | `npx playwright test --grep @GL-001` |
| xUnit | `[Trait("Category", "GL-001")]` | `dotnet test --filter "Category=GL-001"` |
| NUnit | `[Category("GL-001")]` | same filter |
| MSTest | `[TestCategory("GL-001")]` | same filter |
| JUnit 5 | `@Tag("GL-001")` | `mvn test -Dgroups=GL-001` / Gradle `includeTags` |
| Go | ID in the test or subtest name: `t.Run("GL-001 persists activity", ...)` | `go test -run 'GL-001'` |

Using `Category` in .NET matches what Reqnroll generates from scenario tags, so one filter selects scenarios and lower-level tests together.

### pytest conftest

Registers the marker, maps pytest-bdd ID tags onto it, and adds `--behavior`:

```python
# conftest.py
import re
import pytest

ID_RE = re.compile(r"[A-Z][A-Z0-9]{1,9}-\d{2,}")

def pytest_configure(config):
    config.addinivalue_line("markers", "behavior(*ids): behavior IDs this test supports")

def pytest_addoption(parser):
    parser.addoption("--behavior", action="append", default=[], help="run tests for this behavior ID")

def pytest_bdd_apply_tag(tag, function):
    if ID_RE.fullmatch(tag):
        pytest.mark.behavior(tag)(function)
        return True
    return None  # default handling for other tags

def pytest_collection_modifyitems(config, items):
    wanted = set(config.getoption("behavior"))
    if not wanted:
        return
    keep, drop = [], []
    for item in items:
        ids = {i for m in item.iter_markers("behavior") for i in m.args}
        (keep if ids & wanted else drop).append(item)
    config.hook.pytest_deselected(items=drop)
    items[:] = keep
```

Other pytest-bdd tags (like `@game-launch`) still need registering if `--strict-markers` is on.

## Running everything for one ID

Write the per-suite commands into the project's test docs or a script so "run GL-001" is one command. Example for a TypeScript app with Cucumber and Vitest:

```sh
npx cucumber-js --tags "@GL-001" && npx vitest run -t GL-001
```

## Reporting

Two levels, cheapest first:

1. **Static trace.** `python3 scripts/trace_ids.py` (from the skill folder, pointed at the repo) lists each ID, its scenario, and the files referencing it by level, plus duplicate IDs, orphan IDs in tests, and untagged scenarios. Run it after adding a scenario and in CI with `--strict` once the backlog is clean. `--format json` feeds other tools.
2. **Result trace.** Have each suite emit JUnit XML (Cucumber-JS `junit:` formatter, `pytest --junitxml`, `vitest --reporter=junit`, `dotnet test --logger junit` via the JunitXml logger package). A small aggregation step maps each testcase to IDs (from properties, categories, or the name) and reports pass/fail per ID. Build this only when someone will read the report; the static trace covers most needs.

Cucumber also emits Cucumber Messages (`message:` formatter, NDJSON), which carry tags per scenario and are the richest source for scenario results.

## Limits

- IDs document relationships. They do not discover dependencies, and they do not prove complete coverage.
- A unit test tagged with an ID can drift from the behavior. Review tags when the behavior changes, the same way you review step text.
- "Unsupported" in the trace output is informational: plenty of behaviors are fine with only the E2E scenario.
