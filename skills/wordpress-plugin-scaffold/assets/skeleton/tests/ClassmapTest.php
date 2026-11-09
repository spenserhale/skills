<?php

declare(strict_types=1);

namespace {{NAMESPACE}}\Tests;

use WP_UnitTestCase;

/**
 * The runtime autoloader only knows classes listed in src/classmap.php.
 * A class added without `composer classmap` works in tests (Composer's
 * PSR-4 autoloader finds it) and then fatals in production.
 */
final class ClassmapTest extends WP_UnitTestCase {

	public function test_classmap_is_current(): void {
		$root = dirname( __DIR__ );
		exec( escapeshellarg( PHP_BINARY ) . ' ' . escapeshellarg( $root . '/bin/classmap.php' ) . ' --check 2>&1', $output, $code );

		self::assertSame( 0, $code, implode( "\n", $output ) );
	}

	public function test_every_mapped_file_exists(): void {
		/** @var array<string, string> $map */
		$map = require __DIR__ . '/../src/classmap.php';

		foreach ( $map as $class => $path ) {
			self::assertFileExists( __DIR__ . '/../src' . $path, $class );
		}
	}
}
