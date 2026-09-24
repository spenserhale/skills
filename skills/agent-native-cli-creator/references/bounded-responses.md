# Principle 5: Bounded responses, at every layer

Tokens cost money and context. Big outputs are sometimes justified; the default should be narrow.

```bash
# Default page size is bounded; truncation tells the agent how to narrow
$ aicli record list
records[20]:
  - { id: rec_a14b9c, type: A, name: www, content: 192.0.2.10 }
  ...
truncated: true
total: 487
hint: add --limit=N, --filter=type:A, or --cursor=<next> to narrow

# Cursor for explicit continuation
$ aicli record list --cursor=eyJwYWdlIjoyfQ
records[20]:
  ...
next: eyJwYWdlIjozfQ
```

This applies at two layers:

1. **Runtime output.** `list` returning 10,000 rows, logs dumping forever, debug output the agent can't escape.
2. **Tool-description surface.** This is the layer most CLIs miss. Cloudflare's Code Mode MCP serves over 3,000 operations in under 1,000 tokens; most MCP servers spend 1,000 tokens on a single tool's description. A bloated description never gets read by a human, but every agent that loads the server pays the toll on every call.

## What good looks like

- Filtering, pagination, `--limit` on every list-style command
- Concise vs. detailed modes (`--summary` vs. `--detailed`)
- Truncation messages that teach the agent how to narrow the next query (don't just say "truncated"; name the flags)
- Summary-before-detail responses for nested structures
- For MCP wrappers: a per-tool description token budget, audited at build time, not "however much explanation felt natural"

## Grading

> **Blocker:** routine commands dumping unbounded output. **Friction:** broad defaults with narrowing available but unhinted. **Target:** bounded defaults that *teach* better queries, plus an MCP surface where every tool description fits in a tweet.
