import apiFetch from '@wordpress/api-fetch';
import { Card, CardBody, CardHeader, Notice, Spinner } from '@wordpress/components';
import { useEffect, useState } from '@wordpress/element';
import { __, sprintf } from '@wordpress/i18n';
import type { BootConfig, Status } from './types';

export default function App( { config }: { config: BootConfig } ) {
	const [ status, setStatus ] = useState< Status | null >( null );
	const [ error, setError ] = useState< string | null >( null );

	useEffect( () => {
		// apiFetch adds the REST nonce in wp-admin, so no auth code is needed here.
		apiFetch< Status >( { path: config.restPath } )
			.then( setStatus )
			.catch( ( e: { message?: string } ) =>
				setError( e.message ?? __( 'Request failed', '{{TEXT_DOMAIN}}' ) )
			);
	}, [ config.restPath ] );

	return (
		<Card>
			<CardHeader>
				<h2>{ __( '{{NAME}}', '{{TEXT_DOMAIN}}' ) }</h2>
			</CardHeader>
			<CardBody>
				{ error && (
					<Notice status="error" isDismissible={ false }>
						{ error }
					</Notice>
				) }
				{ ! error && ! status && <Spinner /> }
				{ status && (
					<p>
						{ sprintf(
							/* translators: 1: plugin version, 2: log level number */
							__( 'Version %1$s, log level %2$d', '{{TEXT_DOMAIN}}' ),
							status.version,
							status.logLevel
						) }
					</p>
				) }
			</CardBody>
		</Card>
	);
}
