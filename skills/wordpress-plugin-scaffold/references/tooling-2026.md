# Toolchain, 2026

Versions verified November 2026 against Packagist, npm, and the Gutenberg changelogs. If a tool's output contradicts this file, believe the tool, check its changelog, and update the template.

## Contents

- Versions table
- PHP and WordPress targets
- wp-env
- PHPUnit and the WordPress test suite
- PHPStan
- Rector
- JavaScript build
- Upgrading an older plugin repo
- Watch list

## Versions table

| Tool | Constraint in template | Notes |
|------|------------------------|-------|
| PHP (minimum) | 8.4 default | 8.2 reaches end of life in December 2026 and 8.3 is security-only; 8.4 and 8.5 are in active support. Pass `--php 8.3` for hosts that lag |
| WordPress `Requires at least` | 6.9 | 7.1 is current; 6.9 added the Abilities API |
| `@wordpress/env` | ^12.1 | declares Node ≥ 22.13, but its dependencies want Node 24.18+ and npm 11.16+; use Node 24 (`.nvmrc`) |
| `phpunit/phpunit` | ^9.6 | the WordPress test suite caps out at 9.6 |
| `yoast/phpunit-polyfills` | ^4.0 | supports PHPUnit 7.5 to 9, 11, and 12 |
| `wp-phpunit/wp-phpunit` | ^7.0 | fallback test library outside wp-env |
| `phpstan/phpstan` | ^2.1 | |
| `szepeviktor/phpstan-wordpress` | ^2.0 | brings `php-stubs/wordpress-stubs` |
| `php-stubs/wordpress-tests-stubs` | ^7.0 | lets PHPStan understand `WP_UnitTestCase` |
| `phpstan/phpstan-phpunit` | ^2.0 | |
| `rector/rector` | ^2.0 | configured with the fluent `RectorConfig::configure()` |
| `@wordpress/scripts` | ^37.1 | Node 22.22.2+, 24.15+, or 26+ |
| `typescript` | ~6.0 | not 7: typescript-eslint supports TypeScript below 6.1 only |
| `@wordpress/element` / `components` / `api-fetch` / `i18n` | ^10 / ^44 / ^8 / ^7 | externalized at runtime; the versions matter only for types |
| GitHub Actions | `actions/checkout@v7`, `actions/setup-node@v7`, `shivammathur/setup-php@v2`, `ramsey/composer-install@v4` | |

## PHP and WordPress targets

- WordPress 7.0 raised the core minimum to PHP 7.4 and recommends 8.3. A private plugin can require more. Set `Requires PHP`, composer.json `require.php`, and `config.platform.php` to the same version (the script does this), so Composer resolves dev tools for the version you actually run.
- Keep the main file parseable by PHP 7.4, because the guard has to execute before any modern syntax. Verify with `docker run --rm -v "$PWD":/app -w /app php:7.4-cli php -l <slug>.php`.

## wp-env

- **Runtimes:** Docker is the default and the only runtime with `wp-env run`, so tests need Docker. The `--runtime=playground` runtime (SQLite, since 10.39) and `--runtime=php` (the installed PHP's built-in server plus SQLite, since 12.1) are experimental. They're fine for a quick look, but can't run PHPUnit through `run`.
- **The tests environment is gone by default.** `testsEnvironment` and `env.tests` are deprecated. Isolate tests with a second config file: `.wp-env.test.json`, with its own containers, port, and database. Set `"testsEnvironment": false` in both files.
- **Flag order:** `wp-env run --config=.wp-env.test.json --env-cwd=wp-content/plugins/<slug> cli vendor/bin/phpunit`. Everything after the container name goes to the command. Use `--` when the command has flags of its own that wp-env would otherwise take, such as `--help`.
- **Test library:** inside the containers, `WP_TESTS_DIR` points to the PHPUnit library for the installed WordPress version, with its own `wp-tests-config.php`. Since 12.0, alpha, beta, and RC versions fetch the library from the matching `X.Y` branch.
- **11.0 breaking changes:** pretty permalinks are on by default; `port` defaults to automatic (8888/8889 first); `install-path` was replaced by `status`; `--auto-port` was added. Use `wp-env status --json` to find the work directory and ports.
- The PHPUnit install step resets the test site's database, so plugins listed in `.wp-env.test.json` show as inactive after a test run. Use the dev environment for manual checks.
- `"phpmyadmin": true`, `mariadbVersion`, `--xdebug=debug,profile,trace` (`composer env:debug`), and `lifecycleScripts.afterStart` cover most other needs.

## PHPUnit and the WordPress test suite

- Core's own `composer.json` still pins polyfills ^1.1, so plugins stay on PHPUnit 9.6. Don't bump to 10 or later until core's suite supports it (Trac #62004).
- Use snake_case fixtures (`set_up`, `tear_down`, `set_up_before_class`) from the polyfills TestCase, declared `public`.
- Load the plugin in `tests/bootstrap.php` on `muplugins_loaded`. That simulates an always-on install, skipping activation, so call `createTable()` and similar setup in `set_up()`.
- `rest_do_request()` with `wp_set_current_user()` tests REST routes, permission callbacks included, without HTTP.
- `self::factory()->user->create()` returns `int|WP_Error`. Narrow it with `self::assertIsInt()` before passing it on (PHPStan max).

## PHPStan

- `phpstan.dist.neon` at `level: max`, with `phpVersion` matching the minimum. phpstan/extension-installer includes szepeviktor/phpstan-wordpress and phpstan-phpunit automatically. Don't list them under `includes`.
- Analyse the main file, `src/`, and `tests/`. Exclude the generated classmap.
- Values from `require` and `apply_filters()` are `mixed`. Narrow them at runtime (`is_array()`, `is_string()`) instead of using `@var`, so the check protects production too.
- PHPStan 2.x prints agent-facing instructions with errors: fix the cause, no ignores, no baselines. Follow them.

## Rector

```php
return RectorConfig::configure()
	->withPaths( [ __DIR__ . '/src', __DIR__ . '/tests' ] )
	->withSkip( [ ArrayToFirstClassCallableRector::class ] )   // from Rector's Php81 rule set
	->withPhpSets()                                            // reads composer.json require.php
	->withPreparedSets( deadCode: true, codeQuality: true, typeDeclarations: true, earlyReturn: true );
```

`composer rector` is a dry run in `composer check`, so CI fails on drift. `composer rector:fix` applies the changes. Review the diff, because Rector doesn't know the WordPress callback rules.

## JavaScript build

- `wp-scripts build --webpack-src-dir=resources/js --output-path=build` finds `resources/js/index.tsx`, transpiles TypeScript with Babel, externalizes React and `@wordpress/*`, and writes `build/index.asset.php` with dependencies and a content-hash version. You don't need a webpack.config.js.
- `tsc --noEmit` does the type-checking, because Babel strips types without checking them.
- For blocks, add `block.json` files and build with `--blocks-manifest`, then register with `wp_register_block_types_from_metadata_collection()` (WordPress 6.8+). For Interactivity API view scripts, also pass `--experimental-modules`. For a block-only plugin, start from `npx @wordpress/create-block` instead of this skeleton.
- `@wordpress/scripts` 36 moved unit tests to Vitest (`test-unit-js`), and 33 moved e2e tests to Playwright (`test-e2e`, which accepts `--wp-env-config=.wp-env.test.json`).

## Upgrading an older plugin repo

Common findings in pre-2025 plugin repos, with their fixes:

| Found | Fix |
|-------|-----|
| `wp-env run tests-cli …` in composer scripts | `.wp-env.test.json`, then `wp-env run --config=.wp-env.test.json … cli …` |
| `tests/wp-config.php` using `getenv( 'X', 'default' )` | delete it; use wp-env's `WP_TESTS_DIR` config |
| `phpstan.extension.neon` or another non-standard name | rename it to `phpstan.dist.neon` |
| phpstan or rector used but missing from `require-dev` | add them explicitly |
| imports from Rector's old `Core` namespace, or `DowngradeLevelSetList`, in rector.php | rewrite with `RectorConfig::configure()` |
| custom webpack config only to externalize React | drop it; `@wordpress/scripts` handles externals |
| `wp_localize_script` passing numbers or booleans | `wp_add_inline_script` with `wp_json_encode` |
| modern syntax (`?->`, `match`) in the main plugin file before the PHP guard | move it to `src/`; the main file only guards and requires |
| hand-maintained classmap | `bin/classmap.php`, plus `ClassmapTest` and `composer classmap:check` in CI |
| CI that only builds the deploy branch, `actions/checkout@v3` | the template's check, test, and built-branch jobs |
| a 500-line VisualStudio `.gitignore` | the template's short `.gitignore` |

## Watch list

- `@wordpress/build` (0.x): a Rolldown-based plugin build tool that generates PHP registration files. It's the bleeding-edge option: faster builds, and generated script and block registration in place of hand-written `wp_register_script` calls. It's pre-1.0 and monorepo-oriented, so the template stays on `@wordpress/scripts`. Check each time the skill runs: `npm view @wordpress/build version`, plus its README and changelog in the Gutenberg repo (`packages/build`). Swap it in when it reaches 1.0, or earlier if the user asks for bleeding edge and accepts breaking changes. Swapping it in means:
  - replacing the `build` and `start` scripts in package.json
  - replacing the asset loading in `AdminPage::enqueue()` with the PHP file it generates
  - moving `build/` paths in `.deploy.gitignore` and CI if its output directory differs
  - rerunning step 3 and updating this file and the template if the swap becomes the default
- wp-env's `php` and `playground` runtimes: once `run` works on them, tests can run without Docker.
- PHPUnit 10+ support in the core test suite (Trac #62004).
- Real-time collaboration was deferred from WordPress 7.0 to 7.1+. Plugins with custom editor UIs should test against it once it ships.
