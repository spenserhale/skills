---
name: opencode-cli
description: Drive the OpenCode terminal coding agent non-interactively as a delegated sub-agent — send it a prompt with `opencode run`, capture the result from stdout (text or `--format json`), pipe context in via stdin, and control model, agent, sessions, and auto-approval so it never blocks on a prompt.
---

# OpenCode CLI (headless / sub-agent use)

Teaches Claude how to hand a task to **OpenCode** (the open-source terminal AI coding agent) programmatically and get the result back — like spawning another coding agent. The key is `opencode run`, which drives the agent without the TUI, prints the result to stdout, and exits. It's the building block for scripting, CI, and shell pipelines.

## When to use

- The user asks to run OpenCode, "ask OpenCode", get a second opinion from another agent/model, or delegate work to it.
- You want an independent agent (possibly on a different model/provider) to attempt a task.
- Automating OpenCode inside a script or larger workflow.

Do **not** launch the bare `opencode` TUI — it's interactive and blocks. Use `opencode run`.

## Start with help

Flags change between releases. Confirm before relying on them:

```bash
opencode run --help
opencode --help
```

Auth is per-provider: `opencode auth login` (interactive, run once by the user). List/manage with `opencode auth list`.

## Core command

```bash
opencode run "explain the use of context in Go"
opencode run "add a null check in" src/parser.ts   # extra args concatenate into the message
```

- Result → stdout, then exits. Capture with `result=$(opencode run "..." )`.
- Add `-q, --quiet` to suppress the spinner/log chrome in scripts.

## Getting the result back

| Want | How |
|------|-----|
| Formatted human-readable answer (default) | `--format default` (default) |
| Machine-readable event data | `--format json` — raw events for parsing |

```bash
opencode run --format json "list all TODO comments" > todos.json
```

## Passing the prompt

- **As arguments:** `opencode run "review this function for edge cases"`
- **Via stdin (pipe context in):**
  ```bash
  cat error.log | opencode run "analyze this error log and find the root cause"
  git diff main | opencode run "check if these changes introduce any bugs"
  ```

⚠️ Known limitation: if the agent runs a command that needs mid-run input (sudo password, SSH passphrase, `apt`/`npm` confirmation), the process can hang — OpenCode can't pipe a response back. Prefer non-interactive commands in the task, or pre-approve/pre-auth so nothing prompts.

## Key flags

| Flag | Short | Purpose |
|------|-------|---------|
| `--model` | `-m` | Model as `provider/model` (e.g. `anthropic/claude-...`, `openai/gpt-...`) |
| `--agent` | | Use a specific configured agent |
| `--variant` | | Model variant / reasoning effort |
| `--auto` | | Auto-approve all non-denied permissions (use for unattended runs) |
| `--dir` | | Working directory to run in |
| `--file` | `-f` | Attach file(s) to the message |
| `--format` | | `default` or `json` |
| `--quiet` | `-q` | Suppress spinner/log output |
| `--session` | `-s` | Continue a specific session ID |
| `--continue` | `-c` | Resume the last session |
| `--fork` | | Branch off the continued session |
| `--title` | | Name the session |
| `--attach` | | Connect to a running server (e.g. `http://localhost:4096`) |
| `--thinking` | | Show thinking blocks |

Note: `-p` / `--password` (and `-u` / `--username`) are HTTP basic-auth for `--attach`, **not** "print" — don't confuse them with a prompt flag.

## Unattended runs

For a truly non-blocking delegated run, pass `--auto` so the agent doesn't pause for permission on file edits or command execution:

```bash
opencode run --auto -m anthropic/claude-sonnet-5 "fix the failing test in tests/parse.test.ts"
```

Grant this only when the working directory is safe to modify — treat it like `--dangerously`-style autonomy.

## Multi-turn / sessions

Keep context across calls (e.g. a follow-up after reviewing the first result):

```bash
opencode run -c "now write a test that covers that bug"        # continue last session
opencode run -s <SESSION_ID> "address the review comments"      # specific session
opencode run -c --fork "try an alternative approach instead"    # branch without losing the original
```

## Server mode (repeated runs)

Avoid cold-boot / MCP startup cost across many calls by running a persistent server, then attaching:

```bash
opencode serve                                    # terminal 1 — starts HTTP server (default :4096)
opencode run --attach http://localhost:4096 "..." # terminal 2 — each call reuses it
```

OpenCode also exposes an ACP (Agent Client Protocol) server that speaks nd-JSON over stdin/stdout for programmatic integration.

## Delegation pattern (OpenCode as a sub-agent)

1. **Scope tightly.** One objective per `run`; include the relevant paths/context (pipe files in via stdin or `-f`).
2. **Choose the model deliberately** with `-m provider/model` when you want a specific second opinion.
3. **Use `--format json`** when you'll consume the result in code; plain stdout when you just need the answer.
4. **Run in the background** when you don't need to block: `opencode run --auto "..." > out.md 2>&1 &`, then read `out.md`.
5. **Add `--auto` only in a safe workspace**, and prefer no-auto (read/plan) when you just want analysis.
6. **Verify before trusting.** Review the diff / run tests yourself before reporting OpenCode's work as done.

## References

- CLI reference: https://opencode.ai/docs/cli/
- Commands: https://opencode.ai/docs/commands/
- Repo: https://github.com/sst/opencode
