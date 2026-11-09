<?php
/**
 * Plugin Name: {{NAME}}
 * Description: {{DESCRIPTION}}
 * Version: 0.1.0
 * Requires at least: {{WP_MIN}}
 * Requires PHP: {{PHP_MIN}}
 * Author: {{AUTHOR}}
{{AUTHOR_URI_HEADER}} * License: GPL-3.0-or-later
 * License URI: https://www.gnu.org/licenses/gpl-3.0.html
 * Text Domain: {{TEXT_DOMAIN}}
{{UPDATE_URI_HEADER}}{{NETWORK_HEADER}} *
 * {{NAME}}
 * Copyright (C) {{YEAR}} {{AUTHOR}}
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
{{DISCLAIMER}} */

// This file must stay parseable by old PHP so the guard below can run.
// Keep modern syntax (match, enums, readonly, ?->, named args) in src/.

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( PHP_VERSION_ID < {{PHP_ID}} ) {
	add_action(
		'admin_notices',
		static function () {
			echo '<div class="notice notice-error"><p>'
				. esc_html__( '{{NAME}} requires PHP {{PHP_MIN}} or higher.', '{{TEXT_DOMAIN}}' )
				. '</p></div>';
		}
	);

	return;
}

define( '{{CONST}}_FILE', __FILE__ );

require __DIR__ . '/src/hooks.php';
