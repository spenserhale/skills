<?php

declare(strict_types=1);

namespace {{NAMESPACE}}\Admin;

/**
 * Tools screen that mounts the React app from resources/js.
 */
final class AdminPage {

	public const {{CONST_TYPE}}SLUG   = '{{SLUG}}';
	public const {{CONST_TYPE}}HANDLE = '{{SLUG}}-admin';

	private static string $hookSuffix = '';

	public static function capability(): string {
		$capability = apply_filters( '{{HOOK_PREFIX}}/capability', 'manage_options' );

		return is_string( $capability ) ? $capability : 'manage_options';
	}

	public static function register(): void {
		self::$hookSuffix = (string) add_management_page(
			__( '{{NAME}}', '{{TEXT_DOMAIN}}' ),
			__( '{{NAME}}', '{{TEXT_DOMAIN}}' ),
			self::capability(),
			self::SLUG,
			[ self::class, 'render' ]
		);
	}

	public static function render(): void {
		echo '<div class="wrap"><div id="' . esc_attr( self::SLUG ) . '-root"></div></div>';
	}

	public static function enqueue( string $hookSuffix ): void {
		if ( '' === self::$hookSuffix || $hookSuffix !== self::$hookSuffix ) {
			return;
		}

		$assetFile = dirname( {{CONST}}_FILE ) . '/build/index.asset.php';
		if ( ! is_file( $assetFile ) ) {
			return; // Not built yet: run `npm run build`.
		}

		/** @var array{dependencies: list<non-empty-string>, version: string} $asset */
		$asset = require $assetFile;

		wp_enqueue_script(
			self::HANDLE,
			plugins_url( 'build/index.js', {{CONST}}_FILE ),
			$asset['dependencies'],
			$asset['version'],
			[ 'in_footer' => true ]
		);
		wp_set_script_translations( self::HANDLE, '{{TEXT_DOMAIN}}' );
		wp_enqueue_style( 'wp-components' );

		// JSON keeps types; wp_localize_script() would turn every number into a string.
		$config = [
			'restPath' => '/' . StatusController::NAMESPACE . StatusController::ROUTE,
			'version'  => $asset['version'],
		];
		wp_add_inline_script(
			self::HANDLE,
			'window.{{JS_GLOBAL}} = ' . wp_json_encode( $config ) . ';',
			'before'
		);
	}
}
