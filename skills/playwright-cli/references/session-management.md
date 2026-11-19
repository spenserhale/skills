# Browser sessions

## Existing browser profiles

Use [the attachment launcher](../scripts/attach.py) to keep each task’s CLI name, browser channel, profile, and authentication aligned. Launch from the working directory you will use for the rest of the browser task. Starting an attachment with an existing name in the same workspace replaces that session.

- The launcher asks for connection approval by default. Without `--profile`, Playwright chooses an installed extension profile.
- `--profile` takes the last component of the browser?s Profile Path, such as `Profile 2`. Tabs share app sign-in within the chosen profile. Chrome and Edge maintain separate profiles.
- For a trusted unattended workflow, pass `--use-profile-token` with an explicit `--profile` and set `PLAYWRIGHT_MCP_EXTENSION_TOKEN` for that browser profile in the launcher environment. The token is specific to its browser profile.

```powershell
python -B scripts/attach.py --browser edge --profile Default --task opencode-calendar-check
```

After attachment, use only the session printed by the launcher. Open the first work page with `tab-new <app-url>`. The initial Chrome tab can show the Playwright connection page. If the task reopens the same signed-in app later, create a fresh attachment with a new name. The profile retains its login while the app session is valid.

If an attachment fails, check the browser channel, profile, extension install, and pending approval in that profile. A token mismatch can time out. Retry without `--use-profile-token` when the user is available to approve. `playwright-cli list` can help diagnose a missing session in the current workspace.

## Fresh browser sessions

A fresh session has separate open tabs and browser storage. `open` keeps its profile in memory by default. For testing that needs persistence across restarts, use `open --persistent` under a unique session name or use `open --profile` with a dedicated test directory. An active persistent profile is locked to its running browser process.

Use the same `-s` from startup through cleanup. End a launched session with `close` and an extension attachment with `detach`.

For a task targeting a browser explicitly exposed through a Playwright server or a debugging endpoint, see `playwright-cli --help attach`. Use the extension launcher for concurrent tasks on a shared signed-in profile.
