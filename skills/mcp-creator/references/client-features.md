# MCP Client Features & Utilities — Specification

> **This file is the SPECIFICATION** for the client features (Sampling, Roots, Elicitation) and the cross-cutting utilities. Descriptive, not opinionated. See `specification.md` for the core protocol.

Client features are capabilities the **client** offers to the **server** — i.e. the server can make requests *back* to the client. The client declares these in its `initialize` capabilities; a server MUST NOT use one unless the client declared it.

## Sampling

Lets the **server** ask the **client** to run an LLM completion — enabling recursive / agentic behavior without the server holding its own model credentials.

- Method: `sampling/createMessage`.
- The client controls the model, mediates the request, and SHOULD require user approval (principle 4 in `specification.md`).
- The server's visibility into the actual prompt is intentionally limited.
- **2025-11-25:** sampling supports **tool calling** via `tools` and `toolChoice` params.

## Roots

Lets the server ask the client which filesystem/URI **boundaries** it may operate within.

- Method: `roots/list`; notification `notifications/roots/list_changed`.
- A root is a `{ uri, name? }` describing a directory or URI scope the server is allowed to consider.

## Elicitation

Lets the server request **additional input from the user** mid-operation (e.g. a missing parameter, a confirmation).

- Method: `elicitation/create`.
- The server sends a JSON-Schema-described request; the client renders UI, collects input, and returns an `ElicitResult`.
- **2025-11-25:** standards-based `ElicitResult` / `EnumSchema` (titled/untitled, single- and multi-select enums); **URL mode** elicitation (point the user to a URL to complete a flow); default values for primitive types.

## Utilities (cross-cutting)

| Utility | Mechanism | Notes |
|---|---|---|
| **Pagination** | opaque `cursor` → `nextCursor` | Shared by all `*/list` methods; absence of `nextCursor` = last page |
| **Completion** | `completion/complete` | Argument autocompletion for prompt args and resource-template args |
| **Logging** | `notifications/message` | Server → client log messages at standard syslog levels; client sets level via `logging/setLevel` |
| **Ping** | request/response | Liveness check, either direction |
| **Cancellation** | `notifications/cancelled` | Abort an in-flight request by `id` |
| **Progress** | `notifications/progress` | For requests that included a `progressToken` |
| **Tasks** *(experimental, 2025-11-25)* | durable request + polling | Deferred result retrieval; tools opt in via `execution.taskSupport` |
