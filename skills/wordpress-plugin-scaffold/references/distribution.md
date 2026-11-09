# Distribution

## Contents

- Built branch plus Composer (the default)
- WordPress VIP
- WordPress.org
- Releases and versioning

## Built branch plus Composer (the default)

The `built-branch` CI job runs on every push to a branch that doesn't end in `-built`, after the `check` and `test` jobs pass. It:

1. builds JS assets (with `--with-js`)
2. swaps `.deploy.gitignore` in for `.gitignore`
3. runs `git rm -r --cached .` and then `git add -A`, which re-adds only the files the deploy ignore list allows (tracked dev files drop out with no hand-kept `rm` list)
4. force-pushes `<branch>-built`

Sites install it with:

```json
"repositories": [ { "type": "vcs", "url": "https://github.com/acme/acme-redirects" } ],
"require": { "acme/acme-redirects": "dev-main-built" }
```

The site's `composer/installers` places it in `wp-content/plugins/<slug>`. For private repos, the site needs a GitHub token (`composer config github-oauth.github.com …`) or an SSH URL.

- `build/` is gitignored on the source branch and ships on the built branch. Never commit build output to `main`.
- Add a file to `.deploy.gitignore` when it's needed only for development. Remove a line when the runtime needs that file (for example `vendor-prefixed/` after Strauss).
- To pin releases instead of tracking `dev-main-built`, tag the built commit. Add a step after the push that runs `git tag "v$VERSION" && git push origin "v$VERSION"` when the header version changes. Sites then require `^1.2`.
- Pushes made with `GITHUB_TOKEN` don't trigger workflows, and `branches-ignore: ['**-built']` prevents loops if someone pushes to the built branch by hand.

## WordPress VIP

- VIP sites deploy from their own repo. Install the plugin there with Composer, from the built branch, in `plugins/` or `client-mu-plugins/`. On VIP, `vendor/` belongs to the site repo, which is another reason the plugin carries no runtime dependencies.
- As an mu-plugin, nothing fires the activation hook. Expose setup through a filter (`vendor/plugin/create_table`) and call it from a deploy-time WP-CLI command or a version-gated `admin_init` check.
- VIP Code Analysis runs PHPCS with the WordPress-VIP-Go standard on the site repo. Run it locally before shipping a plugin there: `composer require --dev automattic/vipwpcs` and `vendor/bin/phpcs --standard=WordPress-VIP-Go src`. Fix errors; review warnings.
- Cron on VIP runs through Cron Control, where each event is a full WordPress boot. Batch work per event. See the `wordpress-performance` skill.
- Use the `wp-vip-cli` skill for `vip dev-env` and remote `vip wp` commands.

## WordPress.org

Render with `--wporg`. That omits `Update URI`, which would block WordPress.org updates. Then:

- Make the text domain equal the slug (the default). WordPress.org loads translations automatically, so you don't need `load_plugin_textdomain()`. Translation calls before `init` trigger `_load_textdomain_just_in_time` notices (WordPress 6.7+), so translate inside hooks, not at file scope.
- Add a `readme.txt` in WordPress.org format: `=== Name ===`, `Contributors`, `Tags` (5 at most), `Requires at least`, `Tested up to`, `Requires PHP`, `Stable tag`, `License`, then the Description, Installation, FAQ, and Changelog sections. `Stable tag` must match the header `Version`.
- Declare plugin dependencies with the `Requires Plugins: other-slug` header (WordPress 6.5+).
- License: GPL-2.0-or-later or a compatible license. GPL-3.0-or-later is accepted.
- Run Plugin Check before submitting and in CI:
  ```sh
  wp plugin install plugin-check --activate      # inside wp-env: wp-env run cli wp plugin install plugin-check --activate
  wp plugin check <slug>                         # static checks; runtime checks need --require=./wp-content/plugins/plugin-check/cli.php
  ```
  The GitHub Action is `WordPress/plugin-check-action@v1`, with `build-dir` pointing at the built plugin.
- Build the zip with `wp dist-archive .` and a `.distignore`. To keep one list, copy `.deploy.gitignore` to `.distignore` (the patterns are compatible).
- Deploy to SVN with `10up/action-wordpress-plugin-deploy` on tag push, with the `SVN_USERNAME` and `SVN_PASSWORD` secrets.
- Consider a WordPress Playground blueprint (`blueprint.json`) for a live demo link on the plugin page.

## Releases and versioning

- Keep the version in one place, the plugin header. Read it with `get_file_data( FILE, [ 'version' => 'Version' ] )`, not a duplicated constant.
- For asset cache-busting, use the content hash in `build/index.asset.php`, not the plugin version.
- Changelog: keep a `## Unreleased` section in `CHANGELOG.md` (or readme.txt for WordPress.org), and move entries under the version when you tag.
