/** Shape of the JSON that AdminPage::enqueue() prints before the bundle. */
export interface BootConfig {
	restPath: string;
	version: string;
}

export interface Status {
	plugin: string;
	version: string;
	logLevel: number;
}
