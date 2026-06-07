# MCP — Core Specification

> **This file is the SPECIFICATION.** It is the faithful, descriptive account of the Model Context Protocol's architecture and base protocol — the normative rules a server must conform to. It is the **index** for the other spec files in this folder. For opinions on how to *build* a good server, read `best-practices.md`.
>
> **Source of truth:** the MCP TypeScript schema at `schema/<version>/schema.ts` and the rendered spec at modelcontextprotocol.io. RFC 2119 keywords (MUST / SHOULD / MAY) are the spec's.

## Versioning

- **Target revision: `2025-11-25`** (current latest).
- **Prior stable: `2025-06-18`** — still negotiated by many deployed clients/SDKs.
- The protocol version is the **date string** itself, exchanged during `initialize` (e.g. `"protocolVersion": "2025-11-25"`).

Build for `2025-11-25`; tolerate clients that negotiate `2025-06-18`.

## The subareas of the spec (map of this folder)

The spec derives authoritatively from the TypeScript schema and is organized into these areas. This file covers **Architecture** and **Base Protocol**; the rest live in sibling files.

| Spec area | What it covers | Where |
|---|---|---|
| Architecture | Hosts / clients / servers, statefulness, capability negotiation | this file |
| Base Protocol | JSON-RPC 2.0, lifecycle, version negotiation | this file |
| Transports | stdio, Streamable HTTP | `transports.md` |
| Authorization | OAuth 2.0 / OIDC for HTTP transports | `authorization.md` |
| **Tools** (server feature) | Functions the model invokes | **the `mcp-tools-creator` skill** |
| Resources (server feature) | Context/data for user or model | `resources.md` |
| Prompts (server feature) | Templated messages / workflows | `prompts.md` |
| Sampling / Roots / Elicitation (client features) | Server-initiated requests back to the client | `client-features.md` |
| Utilities | Pagination, Completion, Logging, Ping, Cancellation, Progress, Tasks | `client-features.md` (+ noted inline) |

> **Tools live in their own skill.** Tools are the largest and most design-sensitive surface, so the tools specification and its opinionated guide are in the separate `mcp-tools-creator` skill. Read that skill whenever the work centers on tools.

## Architecture

- **Host** — the LLM application that initiates connections (e.g. an IDE, a chat client).
- **Client** — a connector living inside the host, **1:1** with a single server.
- **Server** — provides context and capabilities (this is what you build).

Transport is **JSON-RPC 2.0**. Connections are **stateful**. Capabilities are **negotiated** at startup — neither side assumes a feature exists until it is declared.

## Base Protocol — JSON-RPC 2.0

Three message shapes:

- **Request** — has `id`, `method`, optional `params`; expects a response.
- **Response** — has matching `id`, and either `result` or `error`.
- **Notification** — has `method`, optional `params`, **no `id`**; expects no response.

## Lifecycle

1. **`initialize`** (client → server) — the client sends its `protocolVersion` and `capabilities`; the server replies with the version it agrees to, its own `capabilities`, and `serverInfo`. Version negotiation: if the server can't speak the client's version, it returns the latest it supports and the client decides whether to proceed.
2. **`notifications/initialized`** (client → server) — handshake complete; normal operation may begin.
3. **Operation** — requests/notifications flow per negotiated capabilities.
4. **Shutdown** — transport-level close.

`serverInfo` (the `Implementation` object) carries `name`, `version`, and — as of 2025-11-25 — an optional `description`.

## Capability negotiation

Each side declares only what it supports. A server announces server features it offers; a client announces client features it offers. Example server declaration:

```json
{ "capabilities": {
    "tools":     { "listChanged": true },
    "resources": { "subscribe": true, "listChanged": true },
    "prompts":   { "listChanged": true }
} }
```

Sub-flags like `listChanged` and `subscribe` are themselves part of the negotiation: only emit a `notifications/*/list_changed` (or `.../updated`) if you declared the matching flag.

## Utilities (base protocol)

- **Ping** — liveness check.
- **Cancellation** — `notifications/cancelled` to abort an in-flight request by `id`.
- **Progress** — `notifications/progress` for long-running requests that opted in with a `progressToken`.
- **Tasks** *(experimental, 2025-11-25)* — durable requests with polling / deferred result retrieval; tools opt in via `execution.taskSupport`.

Server-side utilities **Pagination**, **Completion** (argument autocompletion), and **Logging** are covered alongside the features that use them (`resources.md`, `prompts.md`, `client-features.md`).

## Security & trust principles (normative intent)

The spec states four principles that MCP **cannot enforce at the protocol level** — implementors SHOULD build the consent/authorization flows that uphold them:

1. **User consent and control** — users explicitly consent to and control what data and actions are exposed.
2. **Data privacy** — hosts get explicit consent before exposing user data; data isn't transmitted elsewhere without it.
3. **Tool safety** — tools represent **arbitrary code execution**. Tool annotations are **untrusted** unless the server is trusted. Obtain explicit user consent before invoking.
4. **LLM sampling controls** — users approve sampling requests and control prompts; a server's visibility into sampling prompts is intentionally limited.

## Differences from 2025-06-18 (structural)

- **Authorization** — OpenID Connect Discovery 1.0 support; incremental scope consent via `WWW-Authenticate`; OAuth Client ID Metadata Documents; RFC 9728 alignment (`WWW-Authenticate` now optional with `.well-known` fallback).
- **Elicitation** — standards-based `ElicitResult` / `EnumSchema` (titled/untitled, single/multi-select enums); **URL mode** elicitation; default values for primitives.
- **Sampling** — tool-calling support via `tools` and `toolChoice` params.
- **Tasks** — new experimental utility under the base protocol.
- **Transports** — stdio may use stderr for all logging; Streamable HTTP MUST return `403` for invalid `Origin`; SSE polling/resumption clarifications.
- **`icons`** added across tools/resources/templates/prompts; `Implementation` gains optional `description`.
- See the tools spec (`mcp-tools-creator` skill) for tool-specific 2025-11-25 changes.
