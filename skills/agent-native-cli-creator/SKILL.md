---
name: agent-native-cli-creator
description: "Design CLI tools that AI agents can drive reliably: non-interactive flags, structured output (TOON default, JSON, CSV), enumerated errors, idempotent mutations, bounded responses, cross-CLI vocabulary, introspection, --wait for async, profiles, and two-way I/O. Use whenever the user is designing, scaffolding, reviewing, or refactoring a CLI in any language, wants a tool that is agent-friendly, scriptable, or headless, or is debating flag names, --json output, exit codes, error messages, or async ergonomics, even if they never say agent-native. Not for driving an existing CLI (use that tool's skill). For MCP tools hand off to mcp-tools-creator; for MCP servers, mcp-creator."
---

# Agent-Native CLI Creator

Design CLIs so an AI agent can drive them in production without burning tokens, retries, or surprise. Design for agents first: everything that makes a CLI legible to an agent also makes it more pleasant for a human at a terminal. The opposite is not true.

## Scope

This skill is for *building* CLIs. A user *using* an existing CLI needs that tool's own skill. A CLI wrapped as an MCP server is in scope here for the CLI half; the MCP half belongs to mcp-tools-creator (tools) and mcp-creator (server).

Examples in the references use a fictional `aicli` for managing DNS records (a domain everyone has intuition for: `zone`, `record`, `type`, `name`, `content`, `ttl`).

## The ten principles

Tier 1 is table stakes: fail any of these and the deck is stacked against the model on every call. Tier 2 compounds: each makes the CLI better the more it gets used and lets it compose with CLIs the agent already knows. Grade each as blocker, friction, or at target.

| # | Principle | Rule | Blocker looks like |
|---|-----------|------|--------------------|
| 1 | Non-interactive by default | `--force` on destructive, `--yes` elsewhere, headless when stdout is not a TTY | A prompt that hangs silently |
| 2 | Structured output | `--toon` (default), `--json`, `--csv` on every data command; stderr for diagnostics; exit-code taxonomy | No machine format |
| 3 | Errors that enumerate | Validate before side effects; echo the bad value; list the valid set; add a working example | Vague or silent failure |
| 4 | Safe retries | Idempotency keys or natural keys; `--dry-run` returns the real shape plus `status: dry_run` | Duplicates on retry |
| 5 | Bounded responses | Paginate by default; truncation names the narrowing flags; MCP descriptions get a token budget | Unbounded dumps |
| 6 | Cross-CLI vocabulary | One verb and one flag per concept, enforced by schema or lint | `info` for `get`, `--skip-confirmations` |
| 7 | Three-layer introspection | `--help`, versioned `agent-context` JSON, and a skill manifest, all generated together | Only `--help` |
| 8 | Async-aware | `--wait` with backoff and jitter; durable job ledger; `jobs list`/`get`/`prune` | Job ID returned, then nothing |
| 9 | Profiles | `profile save`/`use`/`list`/`show`/`delete`; `--profile` root flag; listed in `agent-context` | Every call re-specifies eight flags |
| 10 | Two-way I/O | `--deliver=stdout|file:|webhook:`; `feedback <text>` local JSONL plus optional upstream | stdout only, no feedback channel |

## Canonical vocabulary

Pick these unless the language community's dominant convention differs, and then enforce your choice mechanically; review-based consistency is Swiss cheese.

- `get` (not `info`/`show`/`describe`), `list` (not `ls`), `create`/`update`/`delete` (not `add`/`set`/`remove`/`rm`)
- `--force` for destructive bypass (not `--skip-confirmations`/`-y`); `--yes` for non-destructive
- `--toon`/`--json`/`--csv` (not `--format=` or `--output=`); no `-j` aliases
- `--limit` and `--cursor` for pagination; `--profile` for named config; `--dry-run` for preview; `--wait` for async completion
- Exit codes: `0` ok, `1` generic, `2` usage, `3` config, `4` not-found, `5` auth, `6` rate-limited
- Config precedence: explicit flag > environment variable > profile > built-in default

## Architecture

Tier 1 can be delivered by hand on a small surface. Tier 2 only holds when a canonical schema (TypeScript, Protobuf, OpenAPI, JSONSchema) generates the CLI, `agent-context`, help text, MCP server, and fixtures, and a CI lint enforces vocabulary, format triplets, `--dry-run` and `--wait` coverage, and MCP token budgets. The cost of inconsistency scales with the number of operations.

## Gotchas

- A prompt with no TTY does not error; it hangs until something kills the process. Detect the TTY honestly and skip prompts, pagers, and color.
- Retry safety spans the whole submit-poll-collect arc: a `--wait` killed mid-poll must find the in-flight job on the next call, which needs the ledger, not just an idempotency key.
- "truncated: true" alone teaches nothing; name `--limit`, `--filter`, `--cursor` in the hint.
- CSV only fits flat tabular output. On nested commands, refuse with an enumerated error pointing at `--toon` or `--json` rather than flattening.
- `agent-context` without `schema_version` cannot signal breaking changes; skill manifests that are not generated from the schema drift.
- File sinks write to a temp file and rename, so a partial artifact is never observed; webhook sinks return the HTTP status rather than swallowing it.
- MCP wrappers pay for every tool description on every call. Budget per tool at build time.

## Checklist when designing or reviewing

Run the CLI through this list. Any "no" is a blocker, friction, or at target; say which.

**Tier 1**
- [ ] Every command runs without prompting given `--force` / `--yes` (no silent hangs)
- [ ] Every data-returning command supports `--toon`, `--json`, `--csv` uniformly
- [ ] stdout = results, stderr = diagnostics, exit codes follow a documented taxonomy
- [ ] Errors enumerate valid values when the cause is enum-shaped
- [ ] Mutations are idempotent (key or natural-key based); `--dry-run` exists on consequential ops
- [ ] List commands paginate by default; truncation messages name the narrowing flag

**Tier 2**
- [ ] Verbs and flags match the cross-CLI convention above
- [ ] All three introspection layers exist: `--help`, `agent-context` (versioned), skill manifest
- [ ] Every async-wrapping command has `--wait` plus a durable job ledger and `jobs list`/`get`/`prune`
- [ ] Profiles via `profile save`/`use`/`list`/`show`/`delete`; precedence explicit > env > profile > default; enumerated in `agent-context`
- [ ] `--deliver` supports `stdout` / `file:` / `webhook:`; `feedback <text>` writes locally and optionally upstream

**Architecture**
- [ ] One canonical schema source generates CLI, `agent-context`, help, MCP, fixtures
- [ ] CI lint enforces vocabulary, format triplets, `--dry-run` / `--wait` coverage, MCP token budgets

## References

Each file carries the worked `aicli` examples, the "what good looks like" list, and the blocker/friction/target grading for its principle.

| Read when | File |
|-----------|------|
| Deciding prompt bypass flags or TTY behavior | `references/non-interactive.md` |
| Choosing or defaulting output formats, exit codes, or stdout/stderr split; explaining why TOON | `references/output-formats.md` |
| Writing error messages or a validation layer | `references/errors.md` |
| Designing create/update/delete, idempotency keys, or `--dry-run` | `references/mutations-and-retries.md` |
| Designing list commands, pagination, or MCP tool descriptions | `references/bounded-responses.md` |
| Naming verbs and flags, writing a naming policy or CI lint | `references/vocabulary.md` |
| Designing `--help`, `agent-context`, or a skill manifest | `references/introspection.md` |
| Wrapping an async API; designing `--wait` and the job ledger | `references/async.md` |
| Designing profiles, `--deliver` sinks, or a `feedback` channel | `references/profiles-and-io.md` |
| Planning schema-driven codegen, or wanting the sources behind the principles | `references/architecture.md` |
