# The architecture beneath the principles, and where they came from

## Why agents first

The classic Command Line Interface Guidelines treat a human at a terminal as the primary user and agents as a tolerated secondary audience. That's the wrong default now. Cloudflare puts it directly in their schema-CLI post: *"Increasingly, agents are the primary customer of our APIs."* HeyGen launched their CLI with "agent" in the marketing copy. Design for agents first, and humans benefit. Designing for humans first and bolting on agent support is what produces the inconsistent, prompt-prone, stdout-only CLIs that Tier 1 exists to correct.

The 10 principles split into two tiers:

- **Tier 1, table stakes.** Don't break the agent. Fail any of these and the deck is stacked against the model on every call.
- **Tier 2, compounding.** Empower the agent. These make the CLI better the more it gets used and let one CLI compose with dozens of others the agent already knows.

## Schema-driven generation

Most of Tier 2 is hard to apply by hand and easy to apply mechanically. Cross-CLI vocabulary, three-layer introspection, async detection, profile precedence, delivery routing: every one of them is the kind of thing you'd be inconsistent about across a dozen subcommands if you wrote them by hand, and trivially consistent about if a schema or codegen pipeline writes them.

That's why Cloudflare's TypeScript schema is the load-bearing detail of their post, not a side note. Generating the CLI, the SDKs, the Terraform provider, and the MCP server from one source is what makes ten principles hold across thousands of operations without drift.

If you're maintaining a hand-written CLI of any size, the consistency bar will keep rising, and the only way to keep up is to move enforcement out of code review and into the schema or the build. Concretely:

- A canonical schema (TypeScript, Protobuf, OpenAPI, JSONSchema, whichever your stack speaks) describing every command, subcommand, flag, type, enum, and return shape
- Codegen for: the CLI itself, the `agent-context` output, the help text, the MCP server (if applicable), and the test fixtures
- A CI lint that enforces the vocabulary policy (banned verbs, flag aliases, missing `--toon`/`--json`/`--csv` triplets, missing `--dry-run` on mutating commands, missing `--wait` on async commands)
- A token budget per MCP tool description, checked at build time

You can deliver Tier 1 by hand if the surface is small. Tier 2 lands cleanly only if it's mechanically generated, because the cost of inconsistency scales with the number of operations.

## Sources

- Cloudflare, *Why we built Code Mode and what it means for agents using APIs* (schema-driven CLI / SDK / Terraform / MCP generation): https://blog.cloudflare.com/code-mode/
- HeyGen, agent-first CLI launch: https://heygen.com/blog
- TOON (Token-Oriented Object Notation): https://github.com/johannschopplich/toon
- Classic *Command Line Interface Guidelines* (the human-first reference these principles depart from): https://clig.dev/
