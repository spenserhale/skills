# Principles 9 and 10: Persistent identity through profiles, and two-way I/O

## Contents

- Principle 9: Persistent identity through profiles
- Principle 10: Two-way I/O (`--deliver` and `feedback`)

## Principle 9: Persistent identity through profiles

Agents don't show up once. They show up tomorrow, and the day after, and a week from now, in a different shell, with the same underlying intent and a different specific input. Stateless leaf-shaped CLIs make every invocation re-specify the same eight flags.

The fix is a profile system.

```bash
# Save a named bundle of configuration once
$ aicli profile save prod \
    --zone=example.com \
    --account=acct_9c2b \
    --default-ttl=300
profile_saved: prod

# Reuse on every subsequent invocation
$ aicli record create --profile=prod --type=A --name=api --content=192.0.2.20
id: rec_d44a01
using_profile: prod
zone: example.com

# Explicit flags win over profile values
$ aicli record create --profile=prod --zone=staging.example.com \
    --type=A --name=api --content=10.0.0.20
id: rec_e51b08
using_profile: prod
zone: staging.example.com   # explicit flag overrode the profile's zone

# Surfaced through introspection so agents discover available identities
$ aicli agent-context | jq '.available_profiles'
["prod","staging","sandbox"]
```

**Recommended precedence:** explicit flag > environment variable > profile > built-in default. Surfacing available profile names in `agent-context` is what lets an introspecting agent discover which identities exist without parsing a config file by hand.

Once an agent has a profile, the per-invocation flag burden drops to just the parts that actually vary. Cross-session identity is durable without the agent writing its own state file. The human and the agent share the same configuration vocabulary.

### What good looks like

- `profile save` / `use` / `list` / `show` / `delete` subcommands
- `--profile <name>` as a persistent root flag
- Profile contents enumerated in `agent-context`
- Stable storage location (`~/.aicli/profiles.json` or `~/.config/aicli/profiles.json`)

### Grading

> **Blocker:** no way to persist configuration. **Friction:** profiles exist but aren't discoverable via introspection. **Target:** named profiles with clean precedence, surfaced through `agent-context`.

## Principle 10: Two-way I/O (`--deliver` and `feedback`)

The classic principle covered stdin/stdout pipelining and that's still true. But agents don't only consume CLIs through pipes, and the CLI doesn't only emit through stdout. Two new mechanisms matter: a way for the CLI to put artifacts where the agent actually needs them, and a way for the agent to report friction back.

```bash
# --deliver routes the artifact to where it's actually needed
$ aicli zone export --zone=example.com --deliver=stdout
zone: example.com
records[142]:
  ...

$ aicli zone export --zone=example.com --deliver=file:./example.com.zone
delivered_to: file:./example.com.zone
bytes: 18432

$ aicli zone export --zone=example.com \
    --deliver=webhook:https://ops.example.com/zone-export
delivered_to: webhook:https://ops.example.com/zone-export
status: 201

# Unknown schemes get a structured refusal naming what's supported
$ aicli zone export --zone=example.com --deliver=s3:bucket/key
error: --deliver scheme must be one of: stdout, file:<path>, webhook:<url> (got: "s3:...")

# feedback closes the loop in the other direction
$ aicli feedback "the --proxied flag is rejected for TXT records but the docs imply it's universal"
feedback_recorded: local (1 entry)

$ aicli feedback list
2026-05-08T18:31:02  the --proxied flag is rejected for TXT records but the docs imply it's universal

# Optional upstream POST when configured
$ AICLI_FEEDBACK_ENDPOINT=https://maintainers.example.com/cli-feedback \
    aicli feedback "race condition in --wait when zone import completes during the first poll"
feedback_recorded: local + upstream
upstream_status: 200
```

`--deliver` routes the artifact directly: stdout, a file path, or a webhook URL. A zone export landing as a file at a known path, or POSTing to a webhook the agent already set up, is one fewer hop than "stdout to a temp file then move." File sinks should write atomically (write-and-rename) so a partial file is never observed. Webhook sinks POST and surface HTTP status. Unknown schemes return a structured refusal, the same pattern as Principle 3's enumerated errors.

`feedback` runs the other way. Agents hit friction constantly: flags rejected for the wrong reason, race conditions in async paths, error messages that don't enumerate. Most of it never gets reported because there's no channel; the agent retries, eventually succeeds, the maintainer never learns the call was painful. `aicli feedback "..."` writes locally by default (JSONL is fine); with `AICLI_FEEDBACK_ENDPOINT` configured, the entry POSTs upstream too.

### What good looks like

- `--deliver` with `stdout` / `file:<path>` / `webhook:<url>` sinks; structured refusal on unknown schemes
- File sinks: write atomically (temp file + rename)
- Webhook sinks: POST and return HTTP status; don't swallow it
- `feedback <text>` with local JSONL by default, upstream POST when an endpoint is configured
- Both `--deliver` and `feedback` surfaced in `agent-context` so the agent knows the channels exist

### Grading

> **Blocker:** stdout-only output, no feedback channel. **Friction:** sinks exist but aren't atomic; feedback exists but the upstream channel isn't discoverable. **Target:** structured delivery and discoverable feedback, both versioned in introspection.
