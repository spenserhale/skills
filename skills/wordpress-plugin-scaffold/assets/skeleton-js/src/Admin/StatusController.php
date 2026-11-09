<?php

declare(strict_types=1);

namespace {{NAMESPACE}}\Admin;

use {{NAMESPACE}}\Config;
use WP_REST_Response;
use WP_REST_Server;

final class StatusController {

	public const {{CONST_TYPE}}NAMESPACE = '{{REST_NAMESPACE}}/v1';
	public const {{CONST_TYPE}}ROUTE     = '/status';

	public static function register(): void {
		register_rest_route( self::NAMESPACE, self::ROUTE, [
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => [ self::class, 'show' ],
			'permission_callback' => static fn (): bool => current_user_can( AdminPage::capability() ),
		] );
	}

	public static function show(): WP_REST_Response {
		$plugin = get_file_data( {{CONST}}_FILE, [ 'version' => 'Version' ] );

		return new WP_REST_Response( [
			'plugin'   => '{{SLUG}}',
			'version'  => $plugin['version'],
			'logLevel' => Config::get()->logLevel->value,
		] );
	}
}
