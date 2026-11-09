# Plugin conventions

These patterns come from two production plugins: a Cloudflare Enterprise cache-purge queue and a WordPress VIP dashboard bridge. Both had no settings screens, used hooks as their only API, and had to run on large multisite installs. Each pattern below gives its reason, so you can tell when it doesn't apply.

## Contents

- Anatomy
- Hooks as the API
- Configuration and secrets
- Classes: static services, memoized clients, value objects
- Errors and logging
- Database tables
- REST routes
- Admin UI
- Multisite and long-running processes
- Runtime dependencies
- Abilities API (exposing actions to AI agents)

## Anatomy

```
<slug>.php          header, license, PHP guard, require src/hooks.php. Keep it PHP 7.4-parseable
src/hooks.php       autoloader plus every add_action/add_filter: the full wiring in one file
src/<Feature>.php   one class per file; sub-namespaces map to subfolders
src/classmap.php    generated; `composer classmap`
resources/js/       TypeScript sources (with --with-js), built to build/
tests/              WP_UnitTestCase integration tests, run inside wp-env
bin/                dev scripts, never deployed
```

Keep all wiring in `hooks.php` so a reader sees the plugin's whole surface in one screen, and so lazy array callbacks stay the norm.

## Hooks as the API

Name hooks `vendor/plugin/verb_noun`. Other code drives the plugin through them:

```php
// hooks.php: the plugin wires its own entry points to its public hooks
register_activation_hook( ACME_CACHE_FILE, [ PurgeQueueTable::class, 'createTable' ] );
add_filter( 'acme/cache/create_table', [ PurgeQueueTable::class, 'createTable' ] );
add_filter( 'acme/cache/queue_many', [ PurgeQueueTable::class, 'insertMany' ] );
add_filter( 'acme/cache/process_queue', [ PurgeQueueService::class, 'processQueue' ] );
add_filter( 'acme/cache/purge_cache', [ ApiClient::class, 'purgeCacheStatic' ] );

// Site code: no class names, no fatals if the plugin is gone
do_action( 'acme/cache/queue_many', [ [ 'type' => 'tag', 'content' => 'post:1' ] ] );
$response = apply_filters( 'acme/cache/purge_cache', [ [ 'type' => 'host', 'content' => 'example.com' ] ] );
if ( ! wp_next_scheduled( 'acme/cache/process_queue' ) ) {
	wp_schedule_event( time(), 'every_minute', 'acme/cache/process_queue' );
}
```

- Use a filter when the caller needs a return value, and an action for fire-and-forget calls. Registering a callback with `add_filter` lets it serve both, because `do_action` ignores the return value.
- Make the cron event name the same string as the hook, so scheduling is just `wp_schedule_event( ..., 'vendor/plugin/process' )`.
- Document every hook in readme.md, with arguments and an example. The readme is the API reference.

## Configuration and secrets

Read settings from filters with safe defaults, and let the site supply them from env vars, constants, or its secrets manager:

```php
add_filter( 'acme/cache/api_credentials', static fn () => [ getenv( 'CF_ZONE' ), getenv( 'CF_EMAIL' ), getenv( 'CF_KEY' ) ] );
```

- Never store secrets in `wp_options` by default, and never print them to JS.
- Per-user secrets, such as an API bearer token, go in user meta. Sites can override them with the `get_user_metadata` filter, so the plugin never needs a settings field.
- Gate features with a capability filtered by the site (`apply_filters( 'vendor/plugin/capability', 'manage_options' )`), or with a custom capability the site grants. Never use a hard-coded role check.

## Classes: static services, memoized clients, value objects

- **Stateless logic** (validators, mappers, queue processing) goes in `final class` with static methods. Static methods have no construction cost and work directly as array callbacks.
- **Configured clients** (HTTP API wrappers) use `readonly class` with constructor promotion and a memoized factory, built from a filter on first use:
  ```php
  public static function getInstance(): self {
  	static $instance;
  	return $instance ??= new self( ...apply_filters( 'acme/cache/api_credentials', [ '', '', '' ] ) );
  }
  ```
  To expose a client method as a hook callback, add a thin static wrapper (`purgeCacheStatic()`) rather than registering `[$instance, 'method']`, which would build the client at boot.
- **Results** are `readonly` value objects with named constructors (`fromWpError()`, `fromException()`, `fromStdClass()`) that implement `JsonSerializable` when they cross REST.
- **Closed sets** are backed enums with a `fromName()` or `tryFrom()` mapper, never string constants.
- **Validation** returns `?WP_Error` from a `match ( true )` chain, so every rule reads as one line:
  ```php
  $message = match ( true ) {
  	! filter_var( $host, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME ) => 'Invalid hostname',
  	! preg_match( '#\.[a-z]{2,63}$#', $host )                         => 'Invalid hostname, missing TLD',
  	default                                                           => null,
  };
  return $message ? new WP_Error( 'invalid_host', $message, compact( 'host' ) ) : null;
  ```
  Batch validators return `[ $valid, $errors ]` and keep going past bad items.

## Errors and logging

- Hook-facing methods return `WP_Error` (or a result object). Exceptions from HTTP or SDK code get caught at that boundary and wrapped: `new WP_Error( 'purge_error', 'Failed to purge cache', [ 'exception' => $e ] )`.
- Log through `Logger::error()` and similar. The logger only emits `vendor/plugin/log` at or above the configured level. `Logger::logWpError()` logs one entry per error code.
- Don't call `error_log()` in plugin code. On VIP and other managed hosts, the site decides where logs go.

## Database tables

Add a custom table only when post meta or options can't handle the query pattern, such as a queue or high-volume rows.

- Create the table with `dbDelta()` in a static `createTable()`. Run it from `register_activation_hook` **and** expose it on a filter. Composer and mu-plugin installs never fire the activation hook, so sites and deploy scripts need another way to run it.
- `dbDelta` syntax is strict: two spaces after `PRIMARY KEY`, one column per line, `KEY` or `INDEX` with a name. It silently skips anything it can't parse.
- On multisite, use `$wpdb->base_prefix` for network-wide tables, and create them only when `get_current_blog_id() === 1` (or `is_main_site()`).
- Use `$wpdb->prepare()` with `%i` for identifiers (WordPress 6.2+) and `%s` or `%d` for values. For bulk inserts, prepare each `(%s, %s)` tuple, then `implode` them into one `INSERT`.
- Re-validate rows read back from the table before acting on them (`deleteInvalidItems()`), because bad data can get in through direct SQL.
- Store a schema version in a site option and run `createTable()` when it changes, so upgrades don't depend on reactivation.

## REST routes

```php
register_rest_route( 'acme-redirects/v1', '/items', [
	'methods'             => WP_REST_Server::CREATABLE,
	'callback'            => [ ItemsController::class, 'create' ],
	'permission_callback' => static fn (): bool => current_user_can( AdminPage::capability() ),
	'args'                => [ 'url' => [ 'type' => 'string', 'format' => 'uri', 'required' => true ] ],
] );
```

- `permission_callback` is mandatory. Use `__return_true` only for truly public data, and say why in a comment.
- Declare `args` schemas so core validates and sanitizes input before your callback runs.
- When proxying to an upstream API (the VIP GraphQL bridge pattern), allowlist operations through a filter (`apply_filters( 'vendor/plugin/graphql_operations', [ 'GetAppDeployments' ] )`), check the content type, attach the server-side token, and pass the upstream status code through. Never forward arbitrary queries.

## Admin UI

- Mount React into a server-rendered root `<div>` and boot it from JSON printed with `wp_add_inline_script( ..., 'before' )`.
- Use `@wordpress/components` and `@wordpress/api-fetch`. In wp-admin, apiFetch adds the REST nonce automatically.
- Enqueue only on your own screen: compare `$hook_suffix` with the value `add_*_page()` returned.
- To add to an existing core surface (the admin bar), create the root element in JS after `DOMContentLoaded` and render into it, rather than adding PHP markup to every page.
- Call `wp_set_script_translations()` for every handle that uses `@wordpress/i18n`.

## Multisite and long-running processes

Static memos (`Config::get()`, `getInstance()`) live for the whole PHP process. One process can span `switch_to_blog()` calls, many Action Scheduler actions, or a long WP-CLI loop. If a memo depends on the site, key it by blog ID, or clear it on `switch_blog`:

```php
add_action( 'switch_blog', [ Config::class, 'reset' ] );
```

Add `Network: true` (`--network`) when the plugin manages network-wide state, such as a shared queue table or a single CDN zone.

## Runtime dependencies

The default is none: `composer.json` has only dev tools, and the classmap autoloader covers `src/`. That keeps installs light, and avoids two plugins loading different versions of the same library into one process.

If a runtime library is truly needed, prefix it with **Strauss** (`brianhenryie/strauss`) into `vendor-prefixed/` under your namespace. Add its autoloader to `hooks.php` and remove `vendor-prefixed/` from `.deploy.gitignore`. Mozart and php-scoper are alternatives. Strauss is the current WordPress default.

## Abilities API (exposing actions to AI agents)

WordPress 6.9 added the Abilities API, and 7.0 added the JS side and the AI client. A plugin with actions an agent could use (purge a cache, look up a deployment) can register them as abilities. They become discoverable over REST at `wp-abilities/v1` and to MCP adapters:

```php
add_action( 'wp_abilities_api_init', [ Abilities::class, 'register' ] );

// In Abilities::register():
wp_register_ability( 'acme-cache/purge-url', [
	'label'               => __( 'Purge a URL from the CDN', 'acme-cache' ),
	'description'         => __( 'Queues one URL for cache purge.', 'acme-cache' ),
	'category'            => 'site',
	'input_schema'        => [ 'type' => 'object', 'properties' => [ 'url' => [ 'type' => 'string', 'format' => 'uri' ] ], 'required' => [ 'url' ] ],
	'execute_callback'    => [ Abilities::class, 'purgeUrl' ],
	'permission_callback' => static fn (): bool => current_user_can( 'manage_options' ),
] );
```

Register abilities only on `wp_abilities_api_init`; anywhere else triggers `_doing_it_wrong` and fails. Guard with `function_exists( 'wp_register_ability' )` if `Requires at least` is below 6.9. Check the current signature against developer.wordpress.org before relying on optional fields.
