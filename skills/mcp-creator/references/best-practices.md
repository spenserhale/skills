# MCP Servers — Best Practices (opinionated)

> **This file is OPINIONATED.** It's how I think MCP *servers* should be built — the design choices the spec leaves open. The protocol facts live in `specification.md` and the sibling spec files; read those for what's allowed, read this for what's wise.
>
> For *tool* design specifically — naming, schemas, returns, errors — use the **`mcp-tools-creator`** skill, which has its own opinionated guide. This file covers the server around the tools.
>
> Backing sources: the MCP spec (modelcontextprotocol.io), Anthropic's *Writing effective tools for agents* (the eval mindset and "design for the agent, not the API" thesis), and AWS Labs' MCP `DESIGN_GUIDELINES.md` (security, structure, runtime conventions). Examples are TypeScript on `@modelcontextprotocol/sdk`.

## Contents

1. [Pick the right surface for each capability](#1-pick-the-right-surface-for-each-capability)
2. [Choose a transport](#2-choose-a-transport)
3. [Scope capabilities honestly](#3-scope-capabilities-honestly)
4. [Project structure](#4-project-structure)
5. [Consent, safety, and the trust boundary](#5-consent-safety-and-the-trust-boundary)
6. [Errors, logging, and observability](#6-errors-logging-and-observability)
7. [Versioning and compatibility](#7-versioning-and-compatibility)
8. [Test and iterate against a real host](#8-test-and-iterate-against-a-real-host)
9. [Sources](#9-sources)

---

## 1. Pick the right surface for each capability

The most consequential server-design decision is mapping each thing you want to expose to the right MCP feature. The feature isn't about *where data lives* — it's about *who controls invocation*:

| Surface | Controlled by | Use when… | Spec |
|---|---|---|---|
| **Tool** | the **model** | the model should *act* or compute something | `mcp-tools-creator` skill |
| **Resource** | the **application/host** | the model or user needs *data/context to read* | `resources.md` |
| **Prompt** | the **user** | you're offering a reusable *templated workflow / slash command* | `prompts.md` |

Common mistakes this prevents:

- **Exposing read-only data as a tool** when it should be a resource. If the host just needs to *attach context*, a resource is cheaper and clearer than a tool the model has to decide to call.
- **Hiding a user workflow inside a tool** when it should be a prompt. If the user is the one who wants to trigger a templated multi-step interaction, that's a prompt (slash command), not a tool.
- **Making everything a tool.** Tools are the model's to invoke and the most safety-sensitive surface. Don't reach for one when a resource or prompt fits.

Anthropic's broader thesis applies at the server level too: **design for what the agent (and user) actually needs to accomplish, not for completeness against your backend.** Don't expose a surface just because you can.

---

## 2. Choose a transport

There are two standard transports (see `transports.md`). My defaults:

- **Local / single-user / launched-by-the-host → stdio.** Lowest overhead, no network exposure, inherits the host's trust boundary. This is the right default for a personal integration, a dev tool, or anything that runs on the same machine as the host. **The one rule you cannot break: stdout carries protocol messages only.** A single stray `console.log` to stdout corrupts the JSON-RPC stream and the server silently stops working. Log to **stderr**.

- **Remote / multi-user / hosted → Streamable HTTP.** Network-reachable, supports SSE streaming and session resumption. The moment more than one user connects, or the server runs somewhere the host can't spawn it, use this — and then you owe it **authorization** (`authorization.md`) and **`Origin` validation** (the server MUST return `403` for an invalid `Origin`, for DNS-rebinding protection).

Don't start with HTTP for a local tool "in case you need it later." stdio is simpler and safer; migrating to HTTP later is a contained change because the feature code is transport-agnostic.

---

## 3. Scope capabilities honestly

Capability negotiation is a promise. **Declare only what you implement**, and only the sub-flags you'll honor:

```ts
// Declare listChanged ONLY if you will actually emit notifications/tools/list_changed.
// Declare resources.subscribe ONLY if you implement resources/subscribe.
const server = new McpServer(
  { name: "acme-server", version: "1.0.0" },
  { capabilities: {
      tools:     { listChanged: true },
      resources: { subscribe: false, listChanged: false },
  } }
);
```

Over-declaring is a real bug: if you advertise `listChanged` and never send the notification, hosts may cache a stale list; if you advertise `subscribe` and don't implement it, subscription calls fail. Under-declaring is safer than over-declaring — start minimal and add capabilities as you implement them.

Keep the **server identity meaningful**: a clear `name`, a real semver `version`, and (2025-11-25) an optional `description`. Hosts and users see these.

---

## 4. Project structure

A predictable layout makes a server easy to read and extend. AWS's reference structure generalizes well (theirs is Python; the shape is language-agnostic):

```
src/
  server.ts        # wiring: create server, register features, connect transport
  tools/           # one file per tool (or per domain) — see mcp-tools-creator
  resources.ts     # resource + template registrations
  prompts.ts       # prompt registrations
  schemas.ts       # shared input/output schemas (Zod / JSON Schema)
  config.ts        # env-var config with sensible defaults
  consts.ts        # constants
```

Conventions worth adopting:

- **One entry point.** Put `main()` (which wires up and starts the server) in `server.ts`/`server.py` rather than a separate `main` module — AWS makes this explicit, and it keeps "how does this start?" answerable in one place.
- **Configuration via environment variables**, named `UPPERCASE_WITH_UNDERSCORES`, each with a sensible default and documented in the README.
- **Co-locate a feature's schema with its handler** so the contract and the implementation move together.
- **A real README**: setup, usage examples, every tool/resource/prompt documented with input/output examples, known limitations, and all env vars. AWS treats this as a hard requirement; for anything others will run, so should you.

---

## 5. Consent, safety, and the trust boundary

The spec is blunt: **tools are arbitrary code execution**, and MCP **cannot enforce consent at the protocol level**. The server is where safety actually lives.

- **Validate every input, server-side.** Annotations and client behavior are untrusted; the server is the only place you can guarantee a tool can't be misused. This is also the spec's explicit requirement (servers MUST validate tool inputs, implement access control, rate-limit, sanitize outputs).
- **Keep a human in the loop for consequential actions.** Use honest behavior annotations (`destructiveHint`, `readOnlyHint`, …) so hosts can gate destructive calls — but treat that as UX, not a security control.
- **Harden any code or path you accept.** AWS's guidelines focus their security section on servers that run or touch untrusted input: scan user-provided code (e.g. Bandit + AST), execute it in an isolated namespace behind an explicit module/function **allowlist**, enforce **timeouts** on long-running operations, and block dangerous calls (`exec`, `eval`, `subprocess`, `os.system`). More generally — and per the spec's resource rules — validate URIs, sanitize file paths against directory traversal, and apply access control to sensitive data.
- **Auth ≠ consent.** A valid OAuth token (HTTP transports) authenticates the caller; it does not mean the user approved a specific destructive action. Design consent flows separately.
- **Don't leak internal plumbing into schemas.** Framework context objects, loggers, and request handles must never appear as user-facing parameters — they cause validation failures and confuse the model.

---

## 6. Errors, logging, and observability

- **Tool/feature failures go in the result, not the protocol.** Return execution failures as `isError: true` inside the result with an actionable message, so the model can self-correct. Reserve JSON-RPC protocol errors for "unknown method / malformed request." (Full treatment in the `mcp-tools-creator` best-practices.)
- **Use standard error codes** where the spec defines them — e.g. resource-not-found `-32002`, invalid-params `-32602`, internal `-32603`.
- **Log to the right channel.** On stdio, **never** write logs to stdout — use stderr, or the MCP **logging** utility (`notifications/message`) so the host can surface server logs at a chosen level. (AWS's servers, for instance, send Loguru output to stderr at a configurable `FASTMCP_LOG_LEVEL`.)
- **Log tool usage for audit** (a spec SHOULD), especially for anything with side effects. If you have an action/audit pattern, the audit write belongs inside the action — see the `mcp-tools-creator` guide.

---

## 7. Versioning and compatibility

- **Target `2025-11-25`**, but **tolerate clients negotiating `2025-06-18`** — many deployed hosts and SDKs still do. The SDK handles most of the negotiation; your job is not to depend on a 2025-11-25-only feature (icons, `execution.taskSupport`, URL-mode elicitation, sampling tool-calls) without a fallback when an older client connects.
- **Version your server independently** of the protocol version (semver in `serverInfo`).
- **Treat tool names and schemas as a public contract.** Renaming a tool or tightening a schema can break agents and saved workflows that depend on it; deprecate deliberately.

---

## 8. Test and iterate against a real host

Building the server is half the job; the other half is confirming a real agent can actually use it.

- **Use the MCP Inspector** to verify the handshake, that your declared capabilities appear, and that each tool/resource/prompt round-trips with realistic inputs.
- **Register it with a real client and drive it as an agent would.** (The `add-mcp` skill handles registration across clients.) Watch where the model misfires — wrong tool, bad arguments, too much/too little returned.
- **Apply the eval mindset** (Anthropic): generate many realistic, verifiable tasks grounded in real use (strong ones need several tool calls), run them through the agent programmatically, and track accuracy alongside tool-call counts, tokens, and errors. Tighten descriptions, schemas, and return shapes based on what you observe — even small refinements compound. Let the agent read its own transcripts and tell you where the server confused it; keep a held-out set so you don't overfit.
- **Iterate the definitions like prompts**, because that's what they are.

---

## 9. Sources

- **MCP Specification** — modelcontextprotocol.io (`2025-11-25`; also `2025-06-18`). See `specification.md` and the sibling spec files.
- **Anthropic — *Writing effective tools for agents*** — https://www.anthropic.com/engineering/writing-tools-for-agents — design-for-the-agent thesis and the Prototype→Evaluate→Collaborate loop.
- **AWS Labs — MCP `DESIGN_GUIDELINES.md`** — https://github.com/awslabs/mcp/blob/main/DESIGN_GUIDELINES.md — project structure, single entry point, env-var config, Loguru→stderr logging, safe execution of untrusted code, documentation requirements. (Python/FastMCP-flavored; the shapes generalize.)

> **Sourcing note (verified 2026-06-07):** the Anthropic and AWS sources were fetched and read in full via browser and the attributions reconciled against the originals — notably, AWS's security guidance is specifically about safely executing untrusted code, and the eval methodology (generate many realistic verifiable tasks, measure, let the agent help) is Anthropic's.

For tool-level opinions (the largest design surface), use the **`mcp-tools-creator`** skill.
