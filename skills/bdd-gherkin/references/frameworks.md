# Frameworks

Check the installed version's `--help` and docs before relying on a flag below; configuration keys change between majors.

## Contents

- Choosing
- Cucumber-JS (JavaScript / TypeScript)
- pytest-bdd (Python)
- Reqnroll (.NET)
- Other stacks

## Choosing

| Stack | Framework | Runs through |
|-------|-----------|--------------|
| JavaScript / TypeScript | Cucumber-JS (`@cucumber/cucumber`) | Its own runner, `npx cucumber-js` |
| Python with pytest | pytest-bdd | pytest; scenarios become pytest tests and reuse fixtures |
| .NET | Reqnroll (successor to SpecFlow) | NUnit, xUnit, MSTest, or TUnit via `dotnet test` |
| JVM | Cucumber-JVM | JUnit Platform |

If the project already has one, use it. If a SpecFlow project exists, Reqnroll is the migration path, not a second framework.

Step definitions are thin. They translate step text into calls on a driver (page object, API client, or domain service) and assertions. Put waiting, retries, selectors, and setup data in the driver so the same driver serves E2E and integration tests.

## Cucumber-JS (JavaScript / TypeScript)

```sh
npm install --save-dev @cucumber/cucumber
```

`cucumber.mjs` (or `cucumber.js`, `.json`, `.yaml`):

```js
export default {
  paths: ['features/**/*.feature'],
  import: ['features/support/**/*.js', 'features/step_definitions/**/*.js'],
  format: ['progress', 'junit:reports/cucumber.xml', 'message:reports/cucumber.ndjson'],
};
```

Step definitions use Cucumber Expressions (`{string}`, `{int}`, `{float}`, `{word}`) by default; regex is the escape hatch.

```js
import { Given, When, Then } from '@cucumber/cucumber';
import assert from 'node:assert/strict';

Given('{string} is installed', async function (title) {
  await this.library.install(title);
});

When('I launch {string}', async function (title) {
  this.session = await this.launcher.launch(title);
});

Then('my activity shows that I played {string}', async function (title) {
  const activity = await this.activity.recent();
  assert.ok(activity.some((a) => a.title === title));
});
```

- Use `function`, not arrow functions: `this` is the per-scenario World. Set it up with `setWorldConstructor` in `features/support/world.js`.
- Hooks scope by tag: `Before({ tags: '@GL-001' }, async function () { ... })`.
- Run one behavior: `npx cucumber-js --tags "@GL-001"`. Expressions: `"@game-launch and not @wip"`.
- TypeScript needs a loader: `requireModule: ['ts-node/register']` with `require:` for CommonJS, or `loader: ['ts-node/esm']` with `import:` for ESM. Follow the project's existing TS runner if it has one.
- Ambiguous step matches fail the run. Reword one of the steps.
- Browser E2E: drive Playwright from the World, or skip Cucumber and use Playwright test tags (see `traceability.md`) if the team prefers Playwright's runner.

## pytest-bdd (Python)

```sh
pip install pytest-bdd   # or add to the project's dependency file
```

`tests/features/game_launch.feature` holds the Gherkin. Bind it from a test module:

```python
# tests/e2e/test_game_launch.py
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/game_launch.feature")  # every scenario in the file

@given(parsers.parse('"{title}" is installed'))
def installed(game_library, title):
    game_library.install(title)

@when(parsers.parse('I launch "{title}"'), target_fixture="session")
def launch(launcher, title):
    return launcher.launch(title)

@then(parsers.parse('my activity shows that I played "{title}"'))
def activity_shows(activity, title):
    assert any(a.title == title for a in activity.recent())
```

- `game_library`, `launcher`, `activity` are ordinary pytest fixtures from `conftest.py`; reuse the ones unit and integration tests already use.
- `target_fixture` hands a step's return value to later steps as a fixture.
- Set `bdd_features_base_dir` in `pytest.ini`/`pyproject.toml` to resolve feature paths from one place.
- Steps shared across modules go in `conftest.py`.
- Tags become pytest markers. To map ID tags to the same `behavior` marker unit tests use, implement `pytest_bdd_apply_tag` (see `traceability.md`); otherwise register each tag or drop `--strict-markers`.
- Scenario test names derive from the scenario title; renaming a scenario renames the test.

## Reqnroll (.NET)

```sh
dotnet add package Reqnroll.xUnit     # or Reqnroll.NUnit, Reqnroll.MSTest, Reqnroll.TUnit
```

Feature files live in the test project; Reqnroll generates test classes at build time for the chosen runner.

```csharp
using Reqnroll;

[Binding]
public class GameLaunchSteps(GameLibraryDriver library, LauncherDriver launcher, ActivityDriver activity)
{
    private LaunchSession? _session;

    [Given("{string} is installed")]
    public void GivenInstalled(string title) => library.Install(title);

    [When("I launch {string}")]
    public async Task WhenLaunch(string title) => _session = await launcher.LaunchAsync(title);

    [Then("my activity shows that I played {string}")]
    public async Task ThenActivityShows(string title) =>
        Assert.Contains(await activity.RecentAsync(), a => a.Title == title);
}
```

- Constructor parameters are resolved per scenario by Reqnroll's context injection; share state between binding classes through injected objects, not statics.
- Tags become test categories (NUnit `Category`, xUnit trait `Category`, MSTest `TestCategory`). Run one behavior: `dotnet test --filter "Category=GL-001"`.
- Hooks scope by tag: `[BeforeScenario("GL-001")]`.
- Settings live in `reqnroll.json`. Test results: `dotnet test --logger trx` or the runner's JUnit logger.
- Migrating from SpecFlow: swap packages and namespaces; Reqnroll ships a compatibility package for gradual moves.

## Other stacks

- JVM: Cucumber-JVM with `cucumber-junit-platform-engine`; tags filter through `cucumber.filter.tags`.
- Go: godog. Ruby: cucumber-ruby. PHP: Behat. Same rules apply: thin steps, a driver layer, ID tags.
