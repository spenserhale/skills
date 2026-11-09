# {{NAME}}

{{DESCRIPTION}}

## Installation

Install with Composer from the built branch (compiled assets, no dev files):

```json
{
  "repositories": [
    { "type": "vcs", "url": "https://github.com/{{VENDOR}}/{{SLUG}}" }
  ],
  "require": {
    "{{VENDOR}}/{{SLUG}}": "dev-main-built"
  }
}
```

`composer/installers` (or your site's `installer-paths`) places it in `wp-content/plugins/{{SLUG}}`.

## Configuration

The plugin has no settings screen. Configure it through filters.

### `{{HOOK_PREFIX}}/config`

Return an array of settings. Defaults are merged in at priority 0.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `log_level` | int | `5` (error) | Lowest level passed to the log action. 1 debug … 8 emergency |

```php
add_filter( '{{HOOK_PREFIX}}/config', static fn ( array $config ): array => [
	'log_level' => 1,
] + $config );
```

## Hooks

### Actions emitted

#### `{{HOOK_PREFIX}}/log`

The plugin has no log writer. Receive log entries and write them wherever you like.

```php
add_action( '{{HOOK_PREFIX}}/log', static function ( string $level, string $message, array $context ): void {
	error_log( sprintf( '[{{SLUG}}] %s: %s %s', $level, $message, wp_json_encode( $context ) ) );
}, 10, 3 );
```

## Development

Requirements: PHP {{PHP_MIN}}+, Composer, Node 24 (see `.nvmrc`), Docker.

```sh
composer install
composer env:start        # dev site on http://localhost:8888 (admin / password)
composer test:start       # separate test environment
composer test             # PHPUnit integration tests inside wp-env
composer check            # classmap freshness, PHPStan (max), Rector dry run
composer classmap         # after adding, renaming, or moving a class in src/
```

## License

GPL-3.0-or-later.
