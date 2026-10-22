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
composer require lorisleiva/laravel-actions:^2.0
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

    public function handle(User $author, Article $article, bool $notifySubscribers): Article
    {
        $article->publishFor($author, notifySubscribers: $notifySubscribers);

        return $article->refresh();
    }
}
```

Run it through the container-aware helpers:

```php
$action = PublishArticle::make(); // app(PublishArticle::class)
$article = $action->handle($author, $article, true);

$article = PublishArticle::run($author, $article, true);
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
    return $this->handle(
        $request->user(),
        $article,
        (bool) $request->validated('notify_subscribers'),
    );
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
use Illuminate\Support\Facades\Bus;

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

Dispatch/PendingDispatch configuration or `configureJob()` covers connection, queue, delay, middleware/chain, and decorator settings. Retry properties/hooks cover tries, exceptions, backoff, timeout, and retry-until. `getJobMiddleware()` returns middleware. Implementing Laravel's `ShouldBeUnique` contract enables uniqueness; the package's `$jobUniqueId` / `getJobUniqueId()` and `$jobUniqueFor` / `getJobUniqueFor()` hooks optionally customize the unique identifier and duration. Horizon tags/display use `getJobTags()` and `getJobDisplayName()`. Verify these APIs against the installed version before adding advanced configuration.

Queue dispatch from inside a database transaction must follow Laravel's after-commit behavior when the job reads committed state. Make retryable work idempotent; uniqueness and overlap middleware control concurrency but do not replace business idempotency.

## Listener adapter

Register the action as a listener and map event data only when its signature differs from `handle()`:

```php
use Illuminate\Support\Facades\Event;

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

`WithAttributes` is available since package version 2.1, is optional, and is not included in `AsAction`. Prefer ordinary typed parameters/DTOs unless unified attributes solve a demonstrated cross-context validation or migration need already present in the project.

## Testing

Test `handle()` as real application behavior. Use package fakes at caller boundaries:

```php
PublishArticle::shouldRun()
    ->once()
    ->with($author, $article, true)
    ->andReturn($article);
```

Use `shouldNotRun()`, `partialMock()`, `spy()`, or `allowToRun()` when that interaction style makes the caller test clearer. Call `clearFake()` when a custom test lifecycle could leak long-lived fake state.

For queued actions, use the package assertion helpers because Laravel queues a decorator rather than the action class directly:

```php
use Illuminate\Support\Facades\Queue;

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
