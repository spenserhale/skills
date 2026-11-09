<?php

declare(strict_types=1);

use Rector\Php81\Rector\Array_\ArrayToFirstClassCallableRector;
use Rector\Config\RectorConfig;

return RectorConfig::configure()
	->withPaths( [ __DIR__ . '/src', __DIR__ . '/tests' ] )
	->withSkip( [
		__DIR__ . '/src/classmap.php',
		// [Foo::class, 'bar'] hook callbacks load lazily and stay removable;
		// Foo::bar(...) autoloads at registration and cannot be remove_filter()'d.
		ArrayToFirstClassCallableRector::class,
	] )
	// Upgrade to the PHP version in composer.json's config.platform; never past it.
	->withPhpSets()
	->withPreparedSets(
		deadCode: true,
		codeQuality: true,
		typeDeclarations: true,
		earlyReturn: true,
	);
