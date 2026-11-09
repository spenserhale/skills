<?php
/**
 * PHPUnit bootstrap for WordPress integration tests.
 *
 * Inside wp-env, WP_TESTS_DIR points at the core test library that matches the
 * installed WordPress, along with a wp-tests-config.php for its database.
 * Outside wp-env, the wp-phpunit/wp-phpunit package is the fallback.
 */

declare(strict_types=1);

require_once __DIR__ . '/../vendor/autoload.php';

$tests_dir = getenv( 'WP_TESTS_DIR' ) ?: getenv( 'WP_PHPUNIT__DIR' ) ?: __DIR__ . '/../vendor/wp-phpunit/wp-phpunit';

if ( ! is_file( $tests_dir . '/includes/functions.php' ) ) {
	fwrite( STDERR, "WordPress test library not found in {$tests_dir}. Run `composer test` (wp-env) or set WP_TESTS_DIR.\n" );
	exit( 1 );
}

define( 'WP_TESTS_PHPUNIT_POLYFILLS_PATH', __DIR__ . '/../vendor/yoast/phpunit-polyfills' );

require_once $tests_dir . '/includes/functions.php';

tests_add_filter(
	'muplugins_loaded',
	static function (): void {
		require __DIR__ . '/../{{SLUG}}.php';
	}
);

require $tests_dir . '/includes/bootstrap.php';
