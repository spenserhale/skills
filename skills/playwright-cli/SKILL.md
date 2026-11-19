---
name: playwright-cli
description: Automate and test browsers with Playwright CLI. Use when a task needs signed-in Chrome or Edge tabs, parallel browser sessions, or an isolated browser for testing.
license: Apache-2.0
allowed-tools: Bash(playwright-cli:*) Bash(npx playwright:*) Bash(npx --no-install playwright:*)
---

# Playwright CLI

Use Playwright CLI for local browser automation. Each task gets its own CLI session. Tasks can share a signed-in browser profile through the Playwright Extension, which gives each connection its own tabs.

## Attach to a signed-in profile

1. Choose the browser and profile where the app is signed in. Use the browser the user requested or the known profile for that app. Pass the profile directory name when the task needs a specific signed-in profile.
2. Run [the launcher](scripts/attach.py) from the task workspace with a short task label. Resolve its script path relative to this skill folder. Include the harness or agent name when it helps identify the task. The launcher adds a random suffix so parallel tasks with the same label stay independent.

   ```powershell
   python -B scripts/attach.py --browser chrome --task claude-calendar
   ```

   Use `--browser edge` for Edge, or `--profile` with a browser profile directory name to select another profile. If the extension asks for connection approval, ask the user to approve with no existing tabs selected. The connection starts with a newly created tab that may show the extension status page.
3. Keep the printed session name and the launch working directory. Pass `-s=<printed-session>` on every command. Start the work with `tab-new <app-url>` and finish with `detach`. Reuse that session for follow-up commands in the same task. Start a new attachment for another task, even in the same harness or workspace.
4. Work in the tabs this task opened. `tab-list` and `tab-select` operate within the task’s session. When finished, use `tab-close` for disposable tabs the task created, then `detach` the task’s session. Leave any tabs the user wants to keep.

Account changes are shared through the profile and web app. Keep other tasks’ sessions and tab groups out of this task’s cleanup. `close-all`, `kill-all`, and shared session names can interrupt work in progress.

## Open a fresh browser for testing

For tasks that need clean browser state, generate a new session name and use `open`. Keep the name for all commands in this task, and end it with `close`.

```powershell
$suffix = [guid]::NewGuid().ToString("N").Substring(0, 12)
$session = "chrome-check-layout-$suffix"
playwright-cli "-s=$session" open --browser=chrome
# Use -s with the same name throughout the task.
playwright-cli "-s=$session" close
```

Use `--browser=msedge` for an independent Edge browser. Read [session management](references/session-management.md) for routing, connection failures, and persistent test profiles.

## Inspect only what the task needs

Use `find` for a targeted search, `snapshot <target>` or `snapshot --depth=3` for a smaller tree, and `--raw eval` for a small structured result. Read the relevant lines of a snapshot file. Use `playwright-cli --help <command>` for syntax.

- [Playwright tests](references/playwright-tests.md) and [test generation](references/test-generation.md) cover running or writing tests.
- [Element attributes](references/element-attributes.md) and [running code](references/running-code.md) cover cases where standard commands need help.
- [Request mocking](references/request-mocking.md) and [storage state](references/storage-state.md) cover specialized test setup.
- [Tracing](references/tracing.md), [video recording](references/video-recording.md), and [PR attachments](references/pr-attachments.md) cover capture and sharing.
