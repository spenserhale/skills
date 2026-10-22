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
- Design queueable actions for safe retries with true idempotency: use idempotency keys, unique database constraints, or guarded state transitions. Treat queue uniqueness and overlap controls as complementary concurrency protection, not an idempotency guarantee.

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
