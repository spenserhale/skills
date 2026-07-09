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

Flags and provider IDs change between releases — **confirm against the installed binary before relying on anything below.** A wrong flag makes `opencode run` exit 1 and dump the help text (e.g. older docs mention `-q/--quiet`, which does **not** exist in current releases like 1.17.x).

```bash
opencode --version         # know which version's flags you're dealing with
opencode run --help        # authoritative flag list for this install
opencode models            # enumerate the exact valid provider/model strings (see Auth)
opencode auth list         # which provider credentials are authenticated
```

Auth is per-provider: `opencode auth login` (interactive, run once by the user). List with `opencode auth list`.

⚠️ **One provider family can expose several distinct provider IDs.** `opencode auth list` may show, e.g., both "Z.AI" and "Z.AI Coding Plan" as separate credentials — these map to *different* model-string prefixes (`zai/glm-5.2` vs `zai-coding-plan/glm-5.2`), each with its own billing/quota. Picking the wrong one can fail silently or expensively (one may be out of balance while the other works). Always cross-check the exact string against `opencode models` before assuming `-m provider/model` is correct — don't guess the prefix.

## Core command

```bash
opencode run "explain the use of context in Go"
opencode run "add a null check in" src/parser.ts   # extra args concatenate into the message
```

- Result → stdout, then exits. Capture with `result=$(opencode run "..." )`.
- In `run` mode stdout is already just the agent's answer (no spinner chrome) — there is no `--quiet` flag. To *see* internal logs for debugging, add `--print-logs` (and optionally `--log-level DEBUG`); by default logs are suppressed, not printed.

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

## Diagnosing a stuck / silent run

A run that produces a header line (e.g. `build · glm-5.2`) and then **nothing for minutes looks identical to a hang but usually isn't**. On an API error (out of balance, rate limit, bad key) OpenCode **silently retries with exponential backoff** (roughly +3s, +7s, +16s, +30s…) and does **not** surface the error to stdout/stderr by default — so a caller can't tell "still working" from "stuck retrying a call that will never succeed." Because this skill is about *unattended* delegation, guard every call:

- **Always bound the call** with a timeout so a retry loop can't spin forever with zero output:
  ```bash
  timeout 300 opencode run --auto -m zai-coding-plan/glm-5.2 "..." > out.md 2>err.log
  ```
  A non-zero exit from `timeout` (124) tells you it was killed — treat that as "investigate," not "done."
- **If it goes quiet longer than expected, re-run with logs on** to see whether it's genuinely hung or retrying an API failure:
  ```bash
  opencode run --print-logs --log-level DEBUG -m <provider/model> "..."
  ```
  Look for lines like `AI_APICallError: Insufficient balance …` with climbing retry timestamps — that's an auth/billing problem (often the wrong provider-ID prefix, see Auth), not a code problem. Fix the credential/model string rather than waiting.

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
| `--print-logs` | | Print internal logs to stderr (for debugging; off by default) |
| `--log-level` | | `DEBUG` \| `INFO` \| `WARN` \| `ERROR` — pair with `--print-logs` |
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
