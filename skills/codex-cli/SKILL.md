---
name: codex-cli
description: Drive OpenAI's Codex CLI non-interactively as a delegated coding sub-agent — send it a prompt with `codex exec`, capture the final result from stdout (or JSON/schema/file), and control sandbox, approvals, model, and sessions so it never blocks on a prompt.
---

# Codex CLI (headless / sub-agent use)

Teaches Claude how to hand a task to OpenAI's **Codex CLI** programmatically and get the result back — like spawning another coding agent. The key is `codex exec`, the non-interactive mode: it runs a single session to completion, streams progress to **stderr**, prints the **final agent message to stdout**, and exits. That makes it safe to capture with `$(...)`, pipe into `jq`/`grep`, or redirect to a file.

## When to use

- The user asks to run Codex, "ask Codex", get a second opinion from another model/agent, or delegate a chunk of work to it.
- You want a parallel/independent agent to attempt a task while you do something else.
- Automating Codex inside a script, CI job, or larger workflow.

Do **not** launch the interactive TUI (`codex` with no subcommand) — it blocks. Always use `codex exec`.

## Start with help

Flags change between releases. Confirm before relying on them:

```bash
codex --help
codex exec --help
```

Check auth once: `codex login` (or set `CODEX_API_KEY` / `OPENAI_API_KEY` in the environment). `codex logout` clears it.

## Core command

```bash
codex exec "summarize the repo structure and list the 5 riskiest areas"
```

- Progress → stderr, final answer → stdout, clean exit code. Alias: `codex e`.
- Capture the result: `result=$(codex exec "..." 2>/dev/null)`

## Getting the result back

| Want | How |
|------|-----|
| Final message as text | Read stdout: `codex exec "..." 2>/dev/null` |
| Final message to a file | `-o, --output-last-message <path>` |
| Machine-readable event stream | `--json` → newline-delimited JSON (JSONL), one event per state change |
| Structured JSON conforming to a schema | `--output-schema <schema.json>` (combine with `-o out.json`) |

With `--json`, parse the stream for the final answer — the last `item.completed` whose `item.type` is `agent_message`, followed by `turn.completed` (which carries token `usage`). Event types include `thread.started`, `turn.started`/`turn.completed`/`turn.failed`, and `item.*` (agent messages, reasoning, command executions, file changes, MCP calls, web searches).

```bash
# Final answer only, as text
codex exec "explain what changed in the last commit" -o /tmp/answer.md 2>/dev/null

# Structured extraction for downstream code
codex exec "Extract project metadata" --output-schema ./schema.json -o ./meta.json

# Stream events and pull the agent's final message with jq
codex exec --json "list open TODOs" \
  | jq -rc 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text' \
  | tail -1
```

## Passing the prompt

- **As an argument:** `codex exec "do the thing"`
- **Via stdin** (use `-` or omit the prompt arg) — good for large or generated prompts:
  ```bash
  cat prompt.txt | codex exec -
  printf "Summarize these logs:\n%s" "$(tail -n 200 app.log)" | codex exec -
  ```
- **Pipe context + instruction together:**
  ```bash
  git diff main | codex exec "review this diff for bugs" 2>/dev/null
  ```
- Attach images with `-i, --image <path[,path...]>`.

## Sandbox & approvals (critical for non-blocking runs)

Sandbox = what Codex is technically allowed to touch. Approvals = when it must stop and ask. In `exec` mode approvals default to **never** (it won't pause), and the sandbox defaults to **read-only** — so an unconfigured `codex exec` can *read and reason but not edit*. Grant more only as needed:

| Need | Flag |
|------|------|
| Read-only analysis (default, safe) | *(nothing)* |
| Let it edit files in the working dir + run local commands | `--sandbox workspace-write` |
| No approvals **and** workspace-write, in one flag | `--full-auto` |
| Set approval policy explicitly | `-a, --ask-for-approval <untrusted\|on-request\|never>` |
| Full access incl. network, no sandbox | `--sandbox danger-full-access`, or `--dangerously-bypass-approvals-and-sandbox` (aka `--yolo`) |

⚠️ Use `danger-full-access` / `--dangerously-bypass-approvals-and-sandbox` **only inside an already-isolated environment** (container, disposable VM, CI runner). Don't reach for it by default — prefer the narrowest sandbox that lets the task succeed.

## Model, config, and context

| Flag | Purpose |
|------|---------|
| `-m, --model <name>` | Override the model (e.g. a `gpt-5.x` codex model) |
| `-c, --config <key=value>` | Override any config value (repeatable) |
| `--profile <name>` | Apply a named profile from `config.toml` |
| `-C, --cd <dir>` | Run as if from another directory |
| `--skip-git-repo-check` | Allow running outside a git repo (git repo required by default) |
| `--ephemeral` | Don't persist the session rollout file to disk |
| `--ignore-user-config` | Skip loading `$CODEX_HOME/config.toml` |

## Multi-turn / resuming

Keep context across calls (e.g. follow-up instructions after reviewing the first result):

```bash
codex exec resume --last "now apply the fix you proposed"   # most recent session
codex exec resume <SESSION_ID> "address the review comments"
```

## Delegation pattern (Codex as a sub-agent)

1. **Scope it tightly.** One clear objective per call; include the relevant paths/context in the prompt.
2. **Pick the least privilege that works** — read-only for analysis/review; `--sandbox workspace-write` only when it must edit.
3. **Capture structured output** when you'll consume the result in code: `--output-schema` + `-o`, or `--json` and parse the final `agent_message`.
4. **Run it in the background** when you don't need to block — e.g. `codex exec ... > out.md 2>err.log &` — then read `out.md` when it finishes.
5. **Verify before trusting.** Treat Codex's output as a proposal: review the diff / run the tests yourself before reporting it as done.

## References

- Non-interactive mode: https://developers.openai.com/codex/noninteractive
- CLI reference (flags): https://developers.openai.com/codex/cli/reference
- Sandbox & approvals: https://developers.openai.com/codex/agent-approvals-security
- Repo: https://github.com/openai/codex
