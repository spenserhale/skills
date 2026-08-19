# Actions Pattern Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use add-subagent-driven-development (recommended) or add-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable project skill that guides Laravel Action-pattern design and conditionally teaches the `lorisleiva/laravel-actions` package.

**Architecture:** Keep universal action-boundary guidance in `SKILL.md` and route package-specific multi-context behavior to one reference file. Index the skill as a Laravel project skill without adding scripts, assets, or a mandatory package dependency.

**Tech Stack:** Codex/Claude skills (`SKILL.md`), Markdown, Laravel/PHP conventions, Laravel Actions 2.x documentation, bundled skill validator.

---

## File Structure

- Create `skills/actions-pattern/SKILL.md`: activation boundary, plain Action-pattern workflow, implementation rules, example, review checklist, and conditional reference routing.
- Create `skills/actions-pattern/references/laravel-actions.md`: package detection, `AsAction`, adapters, validation, jobs, listeners, commands, traits, and package test helpers.
- Modify `readme.md`: add the skill to the project-skills index.

### Task 1: Core Action-pattern skill

**Files:**
- Create: `skills/actions-pattern/SKILL.md`

- [ ] **Step 1: Create the skill directory**

Run:

```bash
mkdir -p skills/actions-pattern/references
```

Expected: `skills/actions-pattern/references/` exists and is empty.

- [ ] **Step 2: Write the core skill**

Create `skills/actions-pattern/SKILL.md` with exactly this content:

````markdown
---
name: actions-pattern
description: Design, implement, refactor, or review Laravel application logic using focused Action classes, with optional lorisleiva/laravel-actions integration. Use for the Action pattern, app/Actions, one-class-one-task architecture, slim controllers, or Laravel Actions; do not use for GitHub Actions workflows.
---

# Laravel Actions Pattern

Organize application behavior around explicit tasks such as `CreateOrder`, `ApproveInvoice`, or `SendResetPasswordEmail`. An action is a focused application boundary, not merely a class with an `Action` suffix.

## Start with the project

Before changing code:

1. Read project instructions and inspect `composer.json`, `composer.lock`, existing action classes, adjacent controllers/jobs/listeners/commands, and tests.
2. Preserve a coherent local convention for action location, suffixes, method name, inputs, and tests. If none exists, use the defaults below.
3. Determine whether `lorisleiva/laravel-actions` is installed or explicitly requested. If so, read [references/laravel-actions.md](references/laravel-actions.md). Otherwise use plain PHP action classes; the pattern does not require the package.
4. Do not add the package unless dependency installation is part of the user's request.

## Choose an action boundary

Use an action for one meaningful application task that benefits from reuse, isolation, orchestration, or a named business boundary. The task may require several queries or writes; “one task” does not mean “one statement.”

Prefer an action when logic:

- Represents a business verb or application use case.
- Is called from, or likely to be called from, more than one delivery context.
- Makes a controller, command, listener, or job responsible for business orchestration.
- Needs a focused transaction, authorization-independent test, or explicit result.

Keep trivial, local delegation inline when extraction would only add navigation. Do not replace cohesive domain services, value objects, model behavior, query objects, policies, or integration clients with actions merely for uniformity.

## Default shape

- Put actions in `app/Actions/<Domain>` or `<Module>/Actions`.
- Name them as verb-first task sentences: `CreateOrder`, `UpdateUserProfile`, `MarkLeadAsLost`.
- Do not require an `Action` suffix. Follow one if the project consistently uses it.
- Use one primary public method, normally `handle()`. Preserve a coherent project-wide `execute()` or `run()` convention instead of mixing names.
- Accept typed business inputs: models, scalars, enums, value objects, or DTOs. Use an array only when it is already a clear, validated local convention.
- Return the useful business result (`Order`, `Money`, a result DTO, or `void`) with an explicit type.
- Constructor-inject only collaborators this task needs. Resolve actions through Laravel's container when they have dependencies.

```php
<?php

namespace App\Actions\Users;

use App\Models\User;

class ChangeUserEmail
{
    public function handle(User $user, string $email): User
    {
        $user->update(['email' => $email]);

        return $user->refresh();
    }
}
```

## Keep delivery concerns at the edges

`handle()` should express the reusable application task. Do not pass `Request`, return `Response`, print console output, or depend on queue/listener wrappers unless the action is intentionally limited to that single delivery context.

Controllers, jobs, listeners, and commands are adapters:

1. Authorize and validate their incoming data.
2. Translate it into typed `handle()` arguments.
3. Invoke the action through dependency injection or the package's container-aware helpers.
4. Translate the result into an HTTP response, console message, event outcome, or queued completion.

Keep policies and transport validation outside a plain action unless they are genuine business invariants. Enforce invariants inside the action or domain model so every entry point receives the same protection.

## Compose deliberately

An orchestration action may inject smaller actions or domain services. Keep the call graph shallow and make the orchestrator's name describe the full outcome. If many actions only forward to one another, revisit the boundaries.

- Put `DB::transaction()` around the complete set of writes that must succeed or fail together, usually in the outer orchestration action. Do not wrap every action automatically.
- Do not catch an exception only to return `false` or `null`. Let meaningful domain/framework exceptions propagate unless this action can actually recover.
- Defer mail, broadcasts, webhooks, and queued follow-up work until a transaction commits when consumers must not observe rolled-back state.
- Design actions that can run on a queue for safe retries: use idempotency keys, unique constraints, state checks, or queue uniqueness as the task requires.

## Refactor into an action

1. Describe the existing behavior as a verb-first task and identify its inputs, output, invariants, and side effects.
2. Write or preserve a behavior-level test before moving logic.
3. Extract the business operation into `handle()` without changing behavior.
4. Replace the original controller/job/listener/command logic with a thin call to the action.
5. Add direct action tests and keep transport tests for authorization, validation, serialization, routing, or dispatch behavior.
6. Remove superseded private helpers and dependencies only after callers and tests prove they are unused.

## Test the boundary

- Test the real action's result, database state, emitted domain events, and failure behavior.
- Use Laravel integration tests when Eloquent, transactions, events, or the container are part of the behavior; a “unit” label is less important than realistic confidence.
- Test each exposed transport adapter only for mapping and transport behavior.
- Mock an action in a caller's test when the caller's collaboration is the subject. Do not mock the action in the action's own behavior test.
- For retryable actions, test the idempotency mechanism and duplicate-delivery behavior.

## Review checklist

- The class name is a precise verb phrase and the class owns one cohesive outcome.
- `handle()` can be understood and invoked without an HTTP, console, event, or queue context.
- Inputs and return values are explicit; array shapes are documented or avoided.
- Dependencies are task-specific, and framework adapters contain no duplicated business logic.
- Transaction scope covers the invariant without holding locks during avoidable external I/O.
- Queued/retryable execution cannot silently duplicate irreversible effects.
- Exceptions retain useful meaning and are translated only at the appropriate boundary.
- Tests cover observable behavior plus each adapter the action actually exposes.

## Sources

- [Action Pattern in Laravel: Concept, Benefits, Best Practices](https://nabilhassen.com/action-pattern-in-laravel-concept-benefits-best-practices)
- [Understanding the Action Pattern in Laravel](https://medium.com/@harryespant/understanding-the-action-pattern-in-laravel-a-cleaner-way-to-organize-your-code-3c7f04666c23)
- [Laravel Actions: One class, one task](https://www.laravelactions.com/2.x/one-class-one-task.html)
````

- [ ] **Step 3: Validate the core skill**

Run:

```bash
python /Users/spenser/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/actions-pattern
```

Expected: `Skill is valid!`

- [ ] **Step 4: Check activation and content invariants**

Run:

```bash
rg -n "GitHub Actions|lorisleiva/laravel-actions|references/laravel-actions.md|handle\(\)|DB::transaction|idempoten" skills/actions-pattern/SKILL.md
```

Expected: matches show the GitHub Actions exclusion, conditional package route, reusable method guidance, transaction boundary, and idempotency guidance.

- [ ] **Step 5: Commit the core skill**

```bash
git add skills/actions-pattern/SKILL.md
git commit -m "Add core actions-pattern skill"
```

### Task 2: Laravel Actions package reference

**Files:**
- Create: `skills/actions-pattern/references/laravel-actions.md`

- [ ] **Step 1: Write the package reference**

Create `skills/actions-pattern/references/laravel-actions.md` with exactly this content:

````markdown
# Laravel Actions package

Use this reference when `lorisleiva/laravel-actions` is present in the project or the user explicitly requests it. The package lets one container-resolvable action run as an object, controller, job, listener, command, or test fake. It does not change the core design rule: keep one context-independent task in `handle()` and adapt delivery contexts around it.

## Verify the local version

Inspect `composer.json` and `composer.lock`. When dependencies are installed, confirm the resolved version and local command surface before relying on an API:

```bash
composer show lorisleiva/laravel-actions
php artisan list --raw | rg '^make:action\b'
php artisan help make:action
```

Install only when requested:

```bash
composer require lorisleiva/laravel-actions
```

Prefer the installed package's source/help and the matching official documentation over remembered flags. The durable concepts below target the 2.x line.

## Base action

`AsAction` combines object, controller, listener, job, command, and fake capabilities. The class must resolve from Laravel's container, so constructor injection is supported.

```php
<?php

namespace App\Actions\Articles;

use App\Models\Article;
use App\Models\User;
use Lorisleiva\Actions\Concerns\AsAction;

class PublishArticle
{
    use AsAction;

    public function handle(User $author, Article $article): Article
    {
        $article->publishFor($author);

        return $article->refresh();
    }
}
```

Run it through the container-aware helpers:

```php
$action = PublishArticle::make(); // app(PublishArticle::class)
$article = $action->handle($author, $article);

$article = PublishArticle::run($author, $article);
```

Dependency injection is preferable when the caller already resolves through the container. Avoid `new PublishArticle(...)` in application code when doing so would bypass injected dependencies or package fakes.

## Controller adapter

Register the action like an invokable controller. Use `asController()` to map HTTP input to `handle()` and keep the business method reusable.

```php
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Gate;
use Illuminate\Support\Facades\Route;
use Lorisleiva\Actions\ActionRequest;

Route::post('/articles/{article}/publish', PublishArticle::class);

public function authorize(ActionRequest $request): bool
{
    return Gate::check('publish', $request->route('article'));
}

public function rules(): array
{
    return ['notify_subscribers' => ['required', 'boolean']];
}

public function asController(ActionRequest $request, Article $article): Article
{
    return $this->handle($request->user(), $article);
}

public function htmlResponse(Article $article): RedirectResponse
{
    return redirect()->route('articles.show', $article);
}
```

`ActionRequest` delegates authorization and validation to methods on the action and exposes validated input. A dedicated `FormRequest` remains valid when that is the project's convention. `jsonResponse()` and `htmlResponse()` may translate the value returned by `asController()` for separate API/web responses.

The package can call `handle()` directly as the controller when there is no `asController()`, but a `Request`/`Response` signature sacrifices reuse. Use that shortcut only for an intentionally HTTP-only action.

## Job adapter

Dispatch the action with its business arguments:

```php
SendTeamReportEmail::dispatch($team);
SendTeamReportEmail::dispatchSync($team);
SendTeamReportEmail::dispatchAfterResponse($team);
```

Do not call `dispatch(SendTeamReportEmail::make())`; the package needs its job decorator. Use `makeJob()` inside Laravel chains and batches:

```php
Bus::chain([
    BuildTeamReport::makeJob($team),
    SendTeamReportEmail::makeJob($team),
])->dispatch();
```

Add `asJob()` only when queued invocation must translate arguments or behavior before delegating to `handle()`:

```php
public function asJob(Team $team): void
{
    $this->handle($team, includePrivateMetrics: true);
}
```

Use the package's documented job properties or `configureJob()` for queue, connection, retries, backoff, timeout, middleware, uniqueness, tags, and display name. Confirm the installed version's API before adding advanced configuration.

Queue dispatch from inside a database transaction must follow Laravel's after-commit behavior when the job reads committed state. Make retryable work idempotent; uniqueness and overlap middleware control concurrency but do not replace business idempotency.

## Listener adapter

Register the action as a listener and map event data only when its signature differs from `handle()`:

```php
Event::listen(TaxiRequested::class, SendOfferToNearbyDrivers::class);

public function asListener(TaxiRequested $event): void
{
    $this->handle($event->source, $event->destination);
}
```

If the event arguments already match `handle()`, `asListener()` can be omitted. Implement Laravel's `ShouldQueue` contract when the listener itself must be queued, following the project's queue conventions.

## Command adapter

Define the command metadata and translate terminal input in `asCommand()`:

```php
use Illuminate\Console\Command;

public string $commandSignature = 'users:update-role {user_id} {role}';
public string $commandDescription = 'Update a user role.';

public function asCommand(Command $command): void
{
    $user = User::findOrFail($command->argument('user_id'));

    $this->handle($user, $command->argument('role'));

    $command->info('Role updated.');
}
```

Register it the same way the local Laravel version registers commands, or use the package's documented command discovery. Keep prompts and terminal output out of `handle()`.

## Traits and attributes

Use `AsAction` by default. Cherry-pick `AsObject`, `AsController`, `AsListener`, `AsJob`, `AsCommand`, or `AsFake` only when the class needs one slice or the combined trait introduces a real method conflict.

`WithAttributes` is optional and is not included in `AsAction`. Prefer ordinary typed parameters/DTOs unless unified attributes solve a demonstrated cross-context validation or migration need already present in the project.

## Testing

Test `handle()` as real application behavior. Use package fakes at caller boundaries:

```php
PublishArticle::shouldRun()
    ->once()
    ->with($author, $article)
    ->andReturn($article);
```

Use `shouldNotRun()`, `partialMock()`, `spy()`, or `allowToRun()` when that interaction style makes the caller test clearer. Clear long-lived fake state when a custom test lifecycle can leak it.

For queued actions, use the package assertion helpers because Laravel queues a decorator rather than the action class directly:

```php
Queue::fake();

SendTeamReportEmail::dispatch($team);

SendTeamReportEmail::assertPushed(
    fn ($action, array $arguments): bool => $arguments[0]->is($team),
);
```

Exercise controller actions through HTTP feature tests so middleware, route binding, authorization, validation, and response conversion are covered. Exercise listener and command adapters only when their mapping contains behavior worth protecting.

## Official documentation

- [Basic usage](https://www.laravelactions.com/2.x/basic-usage.html)
- [One class, one task](https://www.laravelactions.com/2.x/one-class-one-task.html)
- [Controllers](https://www.laravelactions.com/2.x/register-as-controller.html)
- [Authorization and validation](https://www.laravelactions.com/2.x/add-validation-to-controllers.html)
- [Jobs](https://www.laravelactions.com/2.x/dispatch-jobs.html)
- [Listeners](https://www.laravelactions.com/2.x/listen-for-events.html)
- [Commands](https://www.laravelactions.com/2.x/execute-as-commands.html)
- [Mocking and testing](https://www.laravelactions.com/2.x/mock-and-test.html)
- [Granular traits](https://www.laravelactions.com/2.x/granular-traits.html)
- [Unified attributes](https://www.laravelactions.com/2.x/use-unified-attributes.html)
````

- [ ] **Step 2: Check the reference for transport separation and package-specific pitfalls**

Run:

```bash
rg -n "asController|ActionRequest|makeJob|asListener|asCommand|WithAttributes|assertPushed|after-commit" skills/actions-pattern/references/laravel-actions.md
```

Expected: every listed package concept appears in a focused section.

- [ ] **Step 3: Validate links are routed from the entrypoint**

Run:

```bash
test -f skills/actions-pattern/references/laravel-actions.md
test "$(rg -c 'references/laravel-actions.md' skills/actions-pattern/SKILL.md)" -eq 1
```

Expected: both commands exit `0`.

- [ ] **Step 4: Commit the package reference**

```bash
git add skills/actions-pattern/references/laravel-actions.md
git commit -m "Document Laravel Actions package conventions"
```

### Task 3: Repository index and final validation

**Files:**
- Modify: `readme.md`

- [ ] **Step 1: Add the project-skill index row**

In the `## Project skills` table, add this row after Vite+:

```markdown
| [Actions Pattern](skills/actions-pattern/SKILL.md) | Design, implement, refactor, and review focused Laravel action classes, with conditional guidance for the `lorisleiva/laravel-actions` package |
```

- [ ] **Step 2: Run the bundled validator**

Run:

```bash
python /Users/spenser/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/actions-pattern
```

Expected: `Skill is valid!`

- [ ] **Step 3: Run repository-level checks**

Run:

```bash
git diff --check
test "$(rg -c '^name: actions-pattern$' skills/actions-pattern/SKILL.md)" -eq 1
test "$(rg -c 'skills/actions-pattern/SKILL.md' readme.md)" -eq 1
test "$(find skills/actions-pattern -type f | wc -l | tr -d ' ')" -eq 2
```

Expected: all commands exit `0`; the skill contains only its entrypoint and one reference.

- [ ] **Step 4: Manually verify source distillation**

Confirm:

- The general pattern works without the package.
- `handle()` stays transport-independent by default.
- Naming, inputs, transaction scope, side effects, idempotency, and tests are covered.
- The package reference covers object, controller, validation, job, listener, command, traits, attributes, and test modes.
- No upstream article or manual is copied wholesale; uncommon APIs link to official documentation.

Expected: all five statements are true.

- [ ] **Step 5: Commit the index**

```bash
git add readme.md
git commit -m "Index the actions-pattern skill"
```

## Assumptions & Decisions

- The skill belongs under `public/skills` as a project-level Laravel skill.
- Implicit activation remains enabled; the description excludes GitHub Actions.
- The Action pattern does not imply installing `lorisleiva/laravel-actions`.
- `handle()` and verb-first names are defaults, not overrides for coherent local conventions.
- Typed inputs are preferred, while arrays remain valid when locally established and clear.
- One conditional package reference gives enough progressive disclosure without fragmenting the docs.
- Package version numbers are discovered locally rather than hard-coded.
- No scripts, assets, generated agent UI metadata, or README inside the skill directory are needed.
