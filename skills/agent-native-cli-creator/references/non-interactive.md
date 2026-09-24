# Principle 1: Non-interactive by default

If a command can prompt, an agent will eventually hit it from a context where nothing answers: a subagent, a CI job, a piped invocation. The command hangs. Silently. Until something kills it.

```bash
# Hangs forever — there's no human to type "y"
$ aicli record delete rec_a14b9c < /dev/null
Are you sure you want to delete rec_a14b9c (A www.example.com)? [y/N]: ^C

# --force bypasses the prompt; agent gets through cleanly
$ aicli record delete rec_a14b9c --force
type: deleted
id: rec_a14b9c
```

## What good looks like

- `--force` on every destructive command (Cloudflare's standard; explicitly bans `--skip-confirmations`)
- `--yes` for non-destructive confirmation bypass
- Honest TTY detection: when stdout/stderr aren't a terminal, behave as headless automatically (don't paginate, don't prompt, don't color)
- Replace interactive menus with explicit flags or file input (`--from-file=records.csv`)

## Grading

> **Blocker:** silent hang on a prompt. **Friction:** inconsistent prompt-bypass across subcommands. **Target:** one comprehensive non-interactive mode the agent never has to look up.
