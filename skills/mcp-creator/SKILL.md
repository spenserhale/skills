---
name: mcp-creator
description: Build Model Context Protocol (MCP) servers — the overview skill covering architecture, lifecycle, transports, resources, prompts, authorization, and client features (sampling/roots/elicitation), backed by the official specification and an opinionated best-practices guide. Use this skill whenever the user wants to create, build, scaffold, design, plan, or debug an MCP server, add resources/prompts/transports/auth to one, asks "how do I build an MCP server," mentions @modelcontextprotocol/sdk or FastMCP, or is implementing the MCP protocol — even if they don't say "MCP" but describe exposing tools/data/prompts to an LLM host like Claude. For designing the server's TOOLS specifically, hand off to the mcp-tools-creator skill.
---

# MCP Creator

Build a Model Context Protocol server that an LLM host (Claude Desktop, Claude Code, Cursor, etc.) can connect to and use. This skill is the **overview and router**: it orients you, gives you the build workflow, and points you into the specification subareas and an opinionated best-practices guide as you need them.

The single most important framing: **MCP is a stateful, capability-negotiated JSON-RPC protocol.** A server doesn't "have" features — it *declares* them at startup, and the host uses only what was declared. Everything below hangs off that.

## When to use

Activate this skill when the user is:

- Creating, scaffolding, or planning a new MCP server (any language; examples here are TypeScript)
- Adding or changing a server feature — **resources**, **prompts**, **transports**, **authorization**, or **client features** (sampling/roots/elicitation)
- Choosing a transport (stdio vs Streamable HTTP) or adding auth to a remote server
- Debugging handshake/capability/lifecycle issues, or "my host won't see my server"
- Asking what MCP is, how the pieces fit, or which spec revision to target
- Describing the *goal* of MCP without naming it — "let Claude read my database," "expose my API to an agent host," "give the model access to my files"

**Hand off for tools.** If the work centers on *designing the tools the model will call* — naming them, writing their schemas, deciding what to expose, shaping their return values — use the **`mcp-tools-creator`** skill instead. Tools are the largest, most design-sensitive surface, so they get their own skill. This skill keeps a one-paragraph tools stub for completeness and points there.

**Not this skill:** *installing/registering* an existing MCP server into a client is the `add-mcp` skill. *Designing a CLI* (even one an agent drives) is `agent-native-cli-creator`.

## The two reference layers

Everything detailed lives in `references/`, split into two kinds of file so you always know whether you're reading fact or opinion:

- **Specifications** (`specification.md`, `resources.md`, `prompts.md`, `transports.md`, `authorization.md`, `client-features.md`) — the faithful, descriptive protocol: exact methods, fields, and MUST/SHOULD/MAY rules. Read these when you need to get the wire format right.
- **Best practices** (`best-practices.md`) — opinionated guidance on how to build a *good* server: which transport to default to, how to scope capabilities, error/consent patterns, project structure. Read this when you're making design choices.

Load reference files **as you need them** — don't read all of them upfront. The table below tells you where to go.

| You're working on… | Spec file | Also see |
|---|---|---|
| Architecture, lifecycle, capabilities, versioning | `references/specification.md` | best-practices.md |
| Transports (stdio / Streamable HTTP) | `references/transports.md` | best-practices.md |
| Authorization (OAuth/OIDC, remote servers) | `references/authorization.md` | best-practices.md |
| Resources (exposing data/context) | `references/resources.md` | best-practices.md |
| Prompts (slash commands / templated workflows) | `references/prompts.md` | best-practices.md |
| Sampling / roots / elicitation / utilities | `references/client-features.md` | best-practices.md |
| **Tools** | → **`mcp-tools-creator` skill** | — |

## Spec revision to target

- **Target `2025-11-25`** (current latest).
- Tolerate clients that still negotiate **`2025-06-18`** — many deployed hosts/SDKs do.
- The protocol version is the date string, exchanged during `initialize`.

`references/specification.md` has the full "differences from 2025-06-18" list. Start there if you're unsure what's new.

## The build workflow

Work through these in order. Each step has a home in `references/`.

1. **Decide what you're exposing, and as which feature.** Map each capability to the right MCP surface — this is the highest-leverage decision:
   - The model should *act* / call a function → **Tool** (model-controlled) → `mcp-tools-creator` skill.
   - The model/user needs *data or context* to read → **Resource** (application-driven) → `resources.md`.
   - The user wants a reusable *templated workflow / slash command* → **Prompt** (user-controlled) → `prompts.md`.
   Getting this taxonomy right is most of the design. When in doubt, see the "control model" guidance in `best-practices.md`.

2. **Pick a transport.** Local/single-user → **stdio**. Remote/multi-user/hosted → **Streamable HTTP** (+ authorization). See `transports.md` and the opinionated default in `best-practices.md`.

3. **Scaffold with the official SDK.** TypeScript: `@modelcontextprotocol/sdk`. Declare only the capabilities you implement. See `best-practices.md` for project structure.

4. **Implement features**, reading the matching spec file for exact methods/fields. Validate every input; uphold the consent principles (tools are arbitrary code execution).

5. **Add authorization** if the transport is HTTP — `authorization.md`.

6. **Test against a real host.** Use the MCP Inspector and/or register the server with a client (the `add-mcp` skill handles registration). Verify the handshake, that capabilities appear, and that each feature round-trips.

7. **Iterate** using the evaluation mindset in `best-practices.md` — exercise the server the way an agent will, then tighten descriptions, schemas, and return shapes.

## Tools — one-paragraph stub (full guidance in `mcp-tools-creator`)

Tools are functions the **model** invokes (`tools/list` to discover, `tools/call` to invoke). A server that offers tools declares `{ "capabilities": { "tools": { "listChanged": true } } }`. Each tool has a `name`, `description`, JSON-Schema `inputSchema`, optional `outputSchema`, and optional behavior `annotations` (untrusted unless the server is trusted). Results carry a `content[]` array (and optional `structuredContent`); execution failures use `isError: true` *inside* the result so the model can self-correct, rather than a JSON-RPC protocol error. **That is the summary — for designing tools well, switch to the `mcp-tools-creator` skill.**

## Quick orientation example (TypeScript)

A minimal stdio server using the official SDK, declaring one capability per feature kind. This is a shape to anchor on, not a substitute for the spec files.

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "acme-server", version: "1.0.0" });

// A TOOL (model-controlled) — see the mcp-tools-creator skill for how to design these well.
server.registerTool(
  "weather_get_current",
  {
    title: "Get current weather",
    description: "Return current conditions for a city. Use when the user asks about present weather, not forecasts.",
    inputSchema: { location: z.string().describe("City name or zip code") },
  },
  async ({ location }) => ({
    content: [{ type: "text", text: `Weather for ${location}: 72°F, partly cloudy` }],
  })
);

// A RESOURCE (application-driven) — context the host can attach. See references/resources.md.
server.registerResource(
  "readme",
  "file:///acme/README.md",
  { title: "Project README", mimeType: "text/markdown" },
  async (uri) => ({ contents: [{ uri: uri.href, mimeType: "text/markdown", text: "# Acme" }] })
);

await server.connect(new StdioServerTransport()); // stdout = protocol only; log to stderr
```

## Cardinal rules (the why behind them lives in best-practices.md)

- **Declare only what you implement.** Capability negotiation is a promise; don't emit `list_changed`/`updated` notifications for sub-features you didn't declare.
- **stdout is sacred on stdio.** One stray `console.log` to stdout corrupts the JSON-RPC stream. Log to stderr.
- **Validate every input, server-side.** Annotations and client behavior are untrusted; the server is the only place you can enforce safety. Tools are arbitrary code execution.
- **Keep a human in the loop for consequential actions.** The protocol can't enforce consent — your design has to.
- **Match the feature to the control model.** Tool vs resource vs prompt is a decision about *who controls invocation* (model / application / user), not just where the data lives.
