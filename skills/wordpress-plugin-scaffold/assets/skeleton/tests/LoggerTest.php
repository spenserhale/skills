<?php

declare(strict_types=1);

namespace {{NAMESPACE}}\Tests;

use {{NAMESPACE}}\Config;
use {{NAMESPACE}}\Logger;
use {{NAMESPACE}}\LogLevel;
use WP_UnitTestCase;

final class LoggerTest extends WP_UnitTestCase {

	/** @var list<array{string, string}> */
	private array $logged = [];

	public function set_up(): void {
		parent::set_up();

		Config::reset();
		$this->logged = [];
		add_action( '{{HOOK_PREFIX}}/log', function ( string $level, string $message ): void {
			$this->logged[] = [ $level, $message ];
		}, 10, 2 );
	}

	public function tear_down(): void {
		Config::reset();
		parent::tear_down();
	}

	public function test_default_level_drops_messages_below_error(): void {
		Logger::warning( 'quiet' );
		Logger::error( 'loud' );

		self::assertSame( [ [ 'error', 'loud' ] ], $this->logged );
	}

	public function test_config_filter_lowers_level(): void {
		add_filter( '{{HOOK_PREFIX}}/config', static fn ( array $config ): array => [ 'log_level' => LogLevel::Debug->value ] + $config );

		Logger::debug( 'visible' );

		self::assertSame( [ [ 'debug', 'visible' ] ], $this->logged );
	}

	public function test_wp_error_logs_every_code(): void {
		$error = new \WP_Error( 'first', 'First failure' );
		$error->add( 'second', 'Second failure' );

		Logger::logWpError( $error );

		self::assertSame( [ [ 'error', 'First failure' ], [ 'error', 'Second failure' ] ], $this->logged );
	}
}
