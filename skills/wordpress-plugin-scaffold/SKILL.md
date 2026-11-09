---
name: wordpress-plugin-scaffold
description: "Scaffold a new WordPress plugin, or modernize an old one, using a 2026 toolchain: wp-env, PHPUnit integration tests, PHPStan at max, Rector, a classmap autoloader with no runtime vendor/, hooks as the public API, an optional React/TypeScript admin screen, and CI that publishes a built branch for Composer installs. Use when the user wants to start a plugin, asks for a plugin skeleton, boilerplate, or starter, wants to add tests, wp-env, PHPStan, or CI to a plugin repo, or says composer test or tests-cli broke after a wp-env upgrade. Not for block-only plugins (use npx @wordpress/create-block), themes, or tuning existing hook wiring (use wordpress-performance)."
license: MIT
compatibility: Needs Python 3.9+, PHP 8.4+ (at least the plugin's minimum) and Composer 2; Node 24.18+ (wp-env runs through npx); Docker for wp-env tests.
metadata:
  author: spenserhale
  version: "0.1"
---

# WordPress Plugin Scaffold

A plugin is a small library that other code drives through hooks. The skeleton follows that idea: hooks are the API, configuration arrives through filters, classes load lazily from a generated classmap, and the deploy branch ships only runtime files. Render it with the script, then prove it works before handing it over.

## Steps

1. **Settle the inputs.** Ask once, in one batch, only for what you can't infer from the request or the repo:
   - slug, display name, root namespace, Composer vendor
   - minimum PHP (default 8.4; 8.2 reaches end of life in December 2026 and 8.3 gets security fixes only)
   - whether to include the admin screen (`--with-js`). Before rendering it, run `npm view @wordpress/build version`. If it has reached 1.0, or the user asks for bleeding edge, offer `@wordpress/build` in place of `@wordpress/scripts` and read the watch list in `references/tooling-2026.md`. Otherwise keep `@wordpress/scripts`, the stable default
   - multisite network activation (`--network`)
   - distribution: Composer from git (the default) or WordPress.org (`--wporg`)
   - for an integration with a third-party service, its legal name, for the trademark disclaimer (`--disclaimer`)
   Done when every input has a value or a stated default.
2. **Render.** Run `python3 scripts/scaffold.py --help`, then run it with `--dry-run` and check the token values (especially `HOOK_PREFIX`). Then run it for real. To modernize an existing repo, render into a temp directory and port files across by hand. `--force` overwrites files. Done when the script prints `Wrote N files`.
3. **Install and gate.** In the new plugin directory:
   ```sh
   git init && composer install && composer check
   npm install && npm run format && npm run lint:js && npm run typecheck && npm run build   # --with-js only
   composer test:start && composer test
   ```
   Run these from the plugin directory, and run `composer test:stop` when done. Rerun `composer test:start` after editing a wp-env config. `npm run format` is needed after rendering because Prettier's line breaks depend on the slug length. Done when every command exits 0. If Docker is unavailable, say so and report which gates ran. Don't claim the tests passed.
4. **Replace the sample.** Keep `Config`, `Logger`, and `LogLevel`, and their tests. Build the user's feature next to them by the rules below. Run `composer classmap` after adding, renaming, or moving any class. Then rerun step 3.
5. **Document the hooks.** Every `{{prefix}}/…` filter and action goes in readme.md with a copy-paste example, because the readme is the plugin's API reference.

## Rules

- **Hooks are the API.** Register the plugin's own behaviour on namespaced hooks (`vendor/plugin/verb`, for example `acme/redirects/purge`). Callers then use `do_action()` or `apply_filters()` instead of calling classes, so the plugin can be replaced or removed without fatals.
- **Use array callbacks for your own classes:** `[Foo::class, 'bar']`. It loads the class on first fire and stays removable. `Foo::bar(...)` and closures load early or can't be removed. The template's rector.php skips `ArrayToFirstClassCallableRector` for this reason. Keep that skip.
- **Configure through filters, not settings screens.** Pass credentials and other settings through a `…/config` filter that reads env vars or constants. Build a settings UI only when the user asks for one.
- **Don't write logs.** Emit a `…/log` action and let the site send entries to its logger.
- **Static methods for stateless code; memoized instances for configured clients.** Use `readonly` value objects and backed enums. Return `WP_Error` from hook-facing code, and catch exceptions where they cross into WordPress.
- **Use only `src/classmap.php` at runtime.** Composer exists for dev tools. If the plugin truly needs a runtime library, prefix it with Strauss. Read `references/conventions.md` first.
- **Keep the main plugin file parseable by PHP 7.4.** It holds the header, the guard, and a `require`. Everything else lives in `src/`.

## Gotchas

- wp-env 11 and later no longer create the `tests-cli` container by default, and `env.tests` is deprecated. The test environment is a separate config: `wp-env start --config=.wp-env.test.json`. In `run`, wp-env's own flags go before the container name: `wp-env run --config=… --env-cwd=… cli vendor/bin/phpunit`. Flags placed after `cli` are passed to the command, and the run fails with `docker-compose.yml … no such file`.
- Composer scripts call `npx --yes @wordpress/env@12`, not a bare `wp-env`. In a PHP-only plugin with no package.json, `npx wp-env` installs an unrelated npm package. First starts can take minutes, so composer.json raises `process-timeout`.
- `.wp-env.test.json` mounts the plugin with `mappings` to `wp-content/plugins/<slug>`, not `"plugins": ["."]`. A plugin listed under `plugins` gets its folder name from the checkout directory, so `--env-cwd` breaks whenever a clone, `--dest`, or CI checkout uses a different name. The test bootstrap loads the plugin itself, so it doesn't need to be activated.
- Both wp-env configs need `"testsEnvironment": false`. Without it, a test config on port 8889 fails with `may not have the same port`.
- wp-env already provides `WP_TESTS_DIR` and a matching `wp-tests-config.php`. Don't write your own tests/wp-config.php, and use `getenv('X') ?: 'default'` for fallbacks. `getenv()`'s second argument is `local_only`, not a default value, which is a bug the older repos have.
- The WordPress test suite caps out at PHPUnit 9.6. Override `set_up()` and `tear_down()` as **public** methods, not `setUp()`; PHPStan flags protected ones.
- PHPStan reads only `phpstan.neon`, `phpstan.neon.dist`, or `phpstan.dist.neon`. A file with any other name, such as `phpstan.extension.neon`, is silently ignored.
- Rector 2 uses `RectorConfig::configure()->withPhpSets()`, which reads `require.php` from composer.json. Imports from Rector's old `Core` namespace and `DowngradeLevelSetList` are pre-1.0 leftovers. Typed class constants are PHP 8.3+, so the templates add them only when `--php` is 8.3 or higher.
- typescript-eslint doesn't support TypeScript 7 yet, so `lint-js` crashes with it. Keep `typescript` on `~6.0`.
- `wp_localize_script()` turns every value into a string. Pass boot config with `wp_add_inline_script( $handle, 'window.X = ' . wp_json_encode( $config ), 'before' )`.
- Import `createRoot` from `@wordpress/element`. You don't need a custom webpack config: `@wordpress/scripts` externalizes React and `@wordpress/*` packages and writes `build/index.asset.php`.
- Plugins installed by Composer or as mu-plugins skip WordPress's `Requires PHP` activation check. That's why the runtime guard exists.
- `Update URI` stops WordPress.org from offering a same-slug plugin as an "update". The script writes it unless you pass `--wporg`, which must omit it.

## Resources

- Read `references/conventions.md` when designing the plugin's classes, hooks, database tables, REST routes, or multisite behaviour. It covers the patterns taken from the reference plugins, with examples.
- Read `references/tooling-2026.md` when picking versions, upgrading an older plugin's toolchain, or a tool's output contradicts this file. It has a versions table, and lists what changed in 2026 and what to watch.
- Read `references/distribution.md` when shipping: the built branch and Composer VCS installs, WordPress VIP, WordPress.org (readme.txt, Plugin Check, zip), and releases.
- Run `python3 scripts/scaffold.py --help` for every option. The templates live in `assets/skeleton/` and `assets/skeleton-js/`. Edit those rather than patching rendered output in many repos.
- `wordpress-performance` covers hook-wiring cost, `wordpress-cli` covers WP-CLI, `wp-components` covers admin UI components, and `wp-vip-cli` covers VIP environments.
