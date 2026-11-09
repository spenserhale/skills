<?php

declare(strict_types=1);

namespace {{NAMESPACE}};

enum LogLevel: int {
	case Debug     = 1;
	case Info      = 2;
	case Notice    = 3;
	case Warning   = 4;
	case Error     = 5;
	case Critical  = 6;
	case Alert     = 7;
	case Emergency = 8;

	public static function fromName( string $level ): self {
		return match ( strtolower( $level ) ) {
			'debug'    => self::Debug,
			'info'     => self::Info,
			'notice'   => self::Notice,
			'warning'  => self::Warning,
			'error'    => self::Error,
			'critical' => self::Critical,
			'alert'    => self::Alert,
			default    => self::Emergency,
		};
	}
}
