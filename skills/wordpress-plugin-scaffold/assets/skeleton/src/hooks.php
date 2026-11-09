<?php
/**
 * Runtime wiring: autoloader, then hook registrations.
 *
 * The plugin's public API is its hooks. Other code talks to it with
 * do_action() / apply_filters() on the `{{HOOK_PREFIX}}/*` names below,
 * never by calling classes directly, so it stays loosely coupled and
 * every callback stays removable with remove_filter().
 */

declare(strict_types=1);

namespace {{NAMESPACE}};

use function add_filter;
use function spl_autoload_register;

defined( 'ABSPATH' ) || exit;

/**
 * Classmap autoloader. No Composer autoloader at runtime, so the plugin
 * ships without vendor/ and cannot clash with another plugin's copy of a
 * dependency. Regenerate the map with `composer classmap`.
 */
spl_autoload_register(
	static function ( string $class ): void {
		static $map = null;

		if ( ! str_starts_with( $class, __NAMESPACE__ . '\\' ) ) {
			return;
		}

		$map ??= require __DIR__ . '/classmap.php';

		if ( is_array( $map ) && isset( $map[ $class ] ) && is_string( $map[ $class ] ) ) {
			require_once __DIR__ . $map[ $class ];
		}
	}
);

// Array callbacks load their class on first fire only and stay removable.
add_filter( '{{HOOK_PREFIX}}/config', [ Config::class, 'defaults' ], 0 );
{{JS_HOOKS}}