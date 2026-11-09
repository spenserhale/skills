<?php

declare(strict_types=1);

namespace {{NAMESPACE}}\Tests;

use WP_REST_Request;
use WP_UnitTestCase;

final class StatusControllerTest extends WP_UnitTestCase {

	public function test_requires_capability(): void {
		$this->login_as( 'subscriber' );

		$response = rest_do_request( new WP_REST_Request( 'GET', '/{{REST_NAMESPACE}}/v1/status' ) );

		self::assertSame( 403, $response->get_status() );
	}

	public function test_returns_status_for_admin(): void {
		$this->login_as( 'administrator' );

		$response = rest_do_request( new WP_REST_Request( 'GET', '/{{REST_NAMESPACE}}/v1/status' ) );
		$data     = $response->get_data();

		self::assertSame( 200, $response->get_status() );
		self::assertIsArray( $data );
		self::assertSame( '{{SLUG}}', $data['plugin'] );
	}

	private function login_as( string $role ): void {
		$user_id = self::factory()->user->create( [ 'role' => $role ] );
		self::assertIsInt( $user_id );
		wp_set_current_user( $user_id );
	}
}
