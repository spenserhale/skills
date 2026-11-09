<?php

declare(strict_types=1);

namespace {{NAMESPACE}};

use WP_Error;

/**
 * PSR-3-shaped logger with no writer. It emits the `{{HOOK_PREFIX}}/log` action
 * and lets the site decide where logs go (error_log, New Relic, a DB table).
 *
 * @method static void debug( string $message, array<string, mixed> $context = [] )
 * @method static void info( string $message, array<string, mixed> $context = [] )
 * @method static void notice( string $message, array<string, mixed> $context = [] )
 * @method static void warning( string $message, array<string, mixed> $context = [] )
 * @method static void error( string $message, array<string, mixed> $context = [] )
 * @method static void critical( string $message, array<string, mixed> $context = [] )
 * @method static void alert( string $message, array<string, mixed> $context = [] )
 * @method static void emergency( string $message, array<string, mixed> $context = [] )
 */
final class Logger {

	/**
	 * @param array<mixed> $arguments
	 */
	public static function __callStatic( string $name, array $arguments ): void {
		$message = isset( $arguments[0] ) && is_string( $arguments[0] ) ? $arguments[0] : '';
		$context = isset( $arguments[1] ) && is_array( $arguments[1] ) ? $arguments[1] : [];

		self::log( LogLevel::fromName( $name ), $message, $context );
	}

	/**
	 * @param array<mixed> $context
	 */
	public static function log( LogLevel $level, string $message, array $context = [] ): void {
		if ( $level->value < Config::get()->logLevel->value ) {
			return;
		}

		do_action( '{{HOOK_PREFIX}}/log', strtolower( $level->name ), $message, $context );
	}

	public static function logWpError( WP_Error $error, LogLevel $level = LogLevel::Error ): void {
		foreach ( $error->get_error_codes() as $code ) {
			self::log( $level, $error->get_error_message( $code ), [
				'code' => $code,
				'data' => $error->get_error_data( $code ),
			] );
		}
	}
}
