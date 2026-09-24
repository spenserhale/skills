# Principle 6: Cross-CLI vocabulary consistency

The principle most under-stated in the original list. Agents don't memorize one CLI at a time; they build a generalized model of what CLIs do, drawn from every CLI they've seen. When your tool uses `info` for what every other tool calls `get`, the agent doesn't fail; it succeeds slowly, with extra retries, after burning tokens on `--help`. Multiply across thousands of agent invocations per week and the cost is real.

```bash
# Conforming — agents recognize these immediately, zero retries
$ wrangler kv namespace list --json
$ heygen videos list --json
$ aicli record list --toon

# Off-convention versions an agent has to relearn for each tool
$ aicli record ls                    # use list, not ls
$ aicli record info rec_a14b9c       # use get, not info
$ aicli record delete rec_a14b9c \
    --skip-confirmations             # use --force, not --skip-*
$ aicli record list \
    --output=json                    # use --json, not --output=json or --format=json
```

## Canonical schema-layer rules

Extend or adjust to your community, but pick something and enforce it:

- Always `get`, never `info` / `show` / `describe`
- Always `list`, never `ls`
- Always `create` / `update` / `delete`, never `add` / `set` / `remove` / `rm`
- Always `--force`, never `--skip-confirmations` / `-y` for destructive bypass
- Always `--toon` / `--json` / `--csv`, never `--format=json` / `--output json`
- Always `--limit` for pagination size, `--cursor` for continuation
- Always `--profile` for named configuration
- Always `--dry-run` for preview
- Always `--wait` for synchronous async-completion

The framing Cloudflare used is right: *"manually enforcing consistency through reviews is Swiss cheese."* Vocabulary consistency has to be enforced mechanically, at the codegen layer, the schema layer, or a CI lint, because human review will let edge cases through.

## What good looks like

- A documented naming policy committed to the repo (single page, prominently linked)
- A static check in CI that fails on banned verbs and flag aliases
- Canonical names matching the dominant convention in the language community

## Grading

> **Blocker:** verbs/flags contradicting universal conventions (`info` for `get`, `--skip-confirmations` for `--force`). **Friction:** internal inconsistency between subcommands. **Target:** schema-enforced vocabulary an agent trained on neighboring CLIs recognizes on first encounter.
