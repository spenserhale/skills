import { createRoot } from '@wordpress/element';
import App from './App';
import type { BootConfig } from './types';

declare global {
	interface Window {
		{{JS_GLOBAL}}?: BootConfig;
	}
}

const mount = () => {
	const root = document.getElementById( '{{SLUG}}-root' );
	const config = window.{{JS_GLOBAL}};
	if ( ! root || ! config ) {
		return;
	}

	createRoot( root ).render( <App config={ config } /> );
};

if ( document.readyState === 'loading' ) {
	document.addEventListener( 'DOMContentLoaded', mount );
} else {
	mount();
}
