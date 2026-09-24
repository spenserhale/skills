# Principle 7: Three-layer introspection

The classic principle was "progressive help discovery": top-level `--help` lists commands, subcommand `--help` shows usage. That's still true, and it's now the *bottom* layer of a three-layer stack. Each layer answers a different question.

```bash
# Layer 1 — what does this command do? (human-shaped text)
$ aicli --help
aicli  Manage DNS zones, records, and async operations.

USAGE: aicli <command> [flags]

COMMANDS:
  zone      Manage zones
  record    Manage DNS records
  jobs      Inspect async jobs (zone imports, scans, DNSSEC ops)
  profile   Manage saved configurations
  feedback  Send feedback upstream

# Layer 2 — what's the shape of everything? (structured, versioned)
$ aicli agent-context | jq '.schema_version, (.commands | keys)'
"1"
["feedback","jobs","profile","record","zone"]

$ aicli agent-context | jq '.commands.record.subcommands.create.flags'
{
  "--type":      {"type":"enum","values":["A","AAAA","CNAME","MX","TXT","NS","SRV","CAA"],"required":true},
  "--name":      {"type":"string","required":true},
  "--content":   {"type":"string","required":true},
  "--ttl":       {"type":"int","default":3600},
  "--proxied":   {"type":"bool","default":false},
  "--idempotency-key": {"type":"string"},
  "--toon":      {"type":"bool","default":true},
  "--json":      {"type":"bool","default":false},
  "--csv":       {"type":"bool","default":false},
  "--dry-run":   {"type":"bool","default":false}
}

# Layer 3 — when would I use this? (long-form skill manifest)
$ cat $(aicli skill-path)/SKILL.md
# Common DNS workflows
1. Save a profile for your default zone and credentials.
2. Create records with --idempotency-key derived from (zone,type,name) so retries are safe.
3. For bulk imports, use `aicli zone import --file=zone.txt --wait` and inspect via `aicli jobs list`.
```

## The three layers

- **Layer 1: `--help`.** Necessary because some agents hit it before anything else, and humans dropping into the terminal need it.
- **Layer 2: `agent-context`.** What an introspecting agent should actually consume: versioned, machine-readable JSON describing the full shape. Cloudflare's `/cdn-cgi/explorer/api` is the runtime version of this idea; the equivalent for a CLI is a top-level subcommand. The `schema_version` field matters: the consuming agent can detect breaking shape changes deterministically.
- **Layer 3: skill manifest.** Long-form prose teaching the agent how to compose operations into useful workflows. HeyGen ships a skills repo of `SKILL.md` files alongside their CLI; Cloudflare's MCP server is the equivalent. A description of the CLI from the perspective of the *tasks* an agent might use it for, not the commands it exposes.

## What good looks like

All three layers present, each versioned, each kept in sync with the implementation by the same generation step.

## Grading

> **Blocker:** only `--help`, nothing structured. **Friction:** `agent-context` exists but isn't versioned, or skill manifests drift from the real command surface. **Target:** three layers, schema-versioned, machine-validated against the real implementation.
