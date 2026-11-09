<?php

declare(strict_types=1);

namespace {{NAMESPACE}};

/**
 * Immutable settings, supplied by the site through the `{{HOOK_PREFIX}}/config`
 * filter (env vars, constants, or options) instead of a settings screen.
 */
final class Config {

	/**
	 * Default values; the plugin registers this on the config filter at priority 0
	 * so site code at the default priority overrides it.
	 *
	 * @param array<string, mixed> $config
	 *
	 * @return array<string, mixed>
	 */
	public static function defaults( array $config ): array {
		return $config + [
			'log_level' => LogLevel::Error->value,
		];
	}

	private static ?self $instance = null;

	/**
	 * Built once per process. Call reset() when the inputs can change:
	 * in tests, and on `switch_blog` if config differs per site.
	 */
	public static function get(): self {
		return self::$instance ??= self::fromArray( (array) apply_filters( '{{HOOK_PREFIX}}/config', [] ) );
	}

	public static function reset(): void {
		self::$instance = null;
	}

	/**
	 * @param array<mixed> $config
	 */
	public static function fromArray( array $config ): self {
		$level = $config['log_level'] ?? null;

		return new self(
			logLevel: LogLevel::tryFrom( is_int( $level ) ? $level : 0 ) ?? LogLevel::Error,
		);
	}

	public function __construct(
		public readonly LogLevel $logLevel,
	) {
	}
}
