# MCP Tools — Specification

> **This file is the SPECIFICATION.** It describes what the Model Context Protocol *requires and permits* on the wire — the normative truth a tool implementation must conform to. It is deliberately descriptive, not opinionated. For how to *design* good tools on top of this, read `best-practices.md`.
>
> **Source of truth:** the MCP TypeScript schema at `schema/<version>/schema.ts` and the rendered spec at modelcontextprotocol.io. RFC 2119 keywords (MUST / SHOULD / MAY) are the spec's, not mine.

## Versioning

- **Target revision: `2025-11-25`** (current latest, released Nov 2025).
- **Prior stable revision: `2025-06-18`** — still negotiated by many deployed clients and SDKs.
- The protocol version is the date string itself, exchanged during `initialize` (e.g. `"protocolVersion": "2025-11-25"`).

A "Differences from 2025-06-18" section is at the bottom. Build for `2025-11-25`; stay aware that a client may negotiate `2025-06-18`.

## What a tool is

A **tool** is a function the server exposes for the **model** to invoke. In MCP's control-model taxonomy, tools are **model-controlled**: the LLM discovers them via `tools/list` and decides when to call them via `tools/call`. (Resources are application-driven; prompts are user-controlled.)

The spec is explicit that this power requires oversight: *"For trust & safety and security, there SHOULD always be a human in the loop with the ability to deny tool invocations."* Hosts SHOULD surface which tools exist, indicate when one is invoked, and present confirmation prompts for consequential calls.

## Capability declaration

A server that offers tools **MUST** declare the `tools` capability during initialization:

```json
{ "capabilities": { "tools": { "listChanged": true } } }
```

- `listChanged` (boolean) — whether the server will emit `notifications/tools/list_changed` when its tool set changes. Only send that notification if you declared this.

## JSON-RPC methods

| Method | Direction | Purpose |
|---|---|---|
| `tools/list` | client → server | Discover available tools (paginated) |
| `tools/call` | client → server | Invoke a tool |
| `notifications/tools/list_changed` | server → client | Tool list changed (requires `listChanged`) |

## The Tool definition object

Returned in the `tools[]` array of `tools/list`.

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Unique programmatic identifier within the server |
| `title` | optional | Human-readable display name |
| `description` | yes | Human-readable description of what the tool does |
| `inputSchema` | yes | JSON Schema (`type: "object"`) for the arguments |
| `outputSchema` | optional | JSON Schema for the structured result |
| `annotations` | optional | Behavior hints (see below) — **untrusted** unless from a trusted server |
| `icons` | optional *(2025-11-25)* | `[{ src, mimeType, sizes: ["48x48"] }]` for UI display |
| `execution` | optional *(2025-11-25)* | `{ taskSupport: "forbidden" \| "optional" \| "required" }`, default `"forbidden"` |
| `_meta` | optional | General metadata escape hatch |

### `name` rules (2025-11-25)

- 1–128 characters, **case-sensitive**.
- Allowed characters: `A–Z a–z 0–9 _ - .` — no spaces, no commas.
- Unique within a server.
- Valid examples from the spec: `getUser`, `DATA_EXPORT_v2`, `admin.tools.list`.

### `inputSchema`

- **MUST** be a valid JSON Schema object — never `null`.
- **JSON Schema 2020-12** is the default dialect as of 2025-11-25.
- A tool with no parameters: prefer `{ "type": "object", "additionalProperties": false }`.

### Tool annotations (hints, exact names)

Optional behavioral hints. **Clients MUST treat annotations as untrusted unless they come from a trusted server.** Schema defaults shown.

| Annotation | Type | Default | Meaning |
|---|---|---|---|
| `title` | string | — | Human-readable title (display) |
| `readOnlyHint` | boolean | `false` | Tool does not modify its environment |
| `destructiveHint` | boolean | `true` | Tool may perform destructive updates (only meaningful when not read-only) |
| `idempotentHint` | boolean | `false` | Repeated calls with the same args have no additional effect (only meaningful when not read-only) |
| `openWorldHint` | boolean | `true` | Tool interacts with an open world of external entities (e.g. web search); `false` = closed domain (e.g. local memory) |

These are *hints* — not guarantees, not enforced by the protocol.

## `tools/list`

Request (cursor optional):

```json
{ "jsonrpc": "2.0", "id": 1, "method": "tools/list",
  "params": { "cursor": "optional-cursor-value" } }
```

Response (`nextCursor` optional; absence = last page):

```json
{ "jsonrpc": "2.0", "id": 1, "result": {
    "tools": [
      { "name": "get_weather",
        "title": "Weather Information Provider",
        "description": "Get current weather information for a location",
        "inputSchema": {
          "type": "object",
          "properties": { "location": { "type": "string", "description": "City name or zip code" } },
          "required": ["location"] } }
    ],
    "nextCursor": "next-page-cursor" } }
```

Pagination uses opaque cursors shared by all `*/list` methods.

## `tools/call`

Request:

```json
{ "jsonrpc": "2.0", "id": 2, "method": "tools/call",
  "params": { "name": "get_weather", "arguments": { "location": "New York" } } }
```

Response — a **CallToolResult**:

```json
{ "jsonrpc": "2.0", "id": 2, "result": {
    "content": [
      { "type": "text",
        "text": "Current weather in New York:\nTemperature: 72°F\nConditions: Partly cloudy" }
    ],
    "isError": false } }
```

### CallToolResult fields

- `content` — array of **unstructured** content blocks (may mix types).
- `isError` — boolean. `true` signals a **tool execution error** (still a *successful* JSON-RPC response). See error handling.
- `structuredContent` — JSON object of **structured** results.

> Structured content is returned in `structuredContent`. **For backwards compatibility, a tool that returns structured content SHOULD also return the serialized JSON in a TextContent block.**

### Content block types (in `content[]`)

All support optional `annotations` (`audience`, `priority`, `lastModified`).

1. **Text** — `{ "type": "text", "text": "..." }`
2. **Image** — `{ "type": "image", "data": "<base64>", "mimeType": "image/png" }`
3. **Audio** — `{ "type": "audio", "data": "<base64>", "mimeType": "audio/wav" }`
4. **Resource link** — URI reference to a resource:
   ```json
   { "type": "resource_link", "uri": "file:///project/src/main.rs", "name": "main.rs",
     "description": "Primary application entry point", "mimeType": "text/x-rust" }
   ```
   Resource links returned by tools are **not** guaranteed to appear in `resources/list`.
5. **Embedded resource** — inline resource contents (server SHOULD implement the `resources` capability):
   ```json
   { "type": "resource", "resource": {
       "uri": "file:///project/src/main.rs", "mimeType": "text/x-rust",
       "text": "fn main() {\n    println!(\"Hello world!\");\n}" } }
   ```

### `outputSchema` + structured content

If a tool declares `outputSchema`:

- The server **MUST** return `structuredContent` conforming to it.
- The client **SHOULD** validate the structured result against the schema.

Example pairing serialized-JSON text with structured content:

```json
{ "jsonrpc": "2.0", "id": 5, "result": {
    "content": [ { "type": "text",
      "text": "{\"temperature\": 22.5, \"conditions\": \"Partly cloudy\", \"humidity\": 65}" } ],
    "structuredContent": { "temperature": 22.5, "conditions": "Partly cloudy", "humidity": 65 } } }
```

## Error handling — two distinct mechanisms

**1. Protocol errors** — standard JSON-RPC `error` objects. Used for unknown tools, malformed requests, and server-internal failures:

```json
{ "jsonrpc": "2.0", "id": 3,
  "error": { "code": -32602, "message": "Unknown tool: invalid_tool_name" } }
```

**2. Tool execution errors** — reported *inside the result* with `isError: true`. Used for API failures, **input/parameter validation errors**, and business-logic errors:

```json
{ "jsonrpc": "2.0", "id": 4, "result": {
    "content": [ { "type": "text", "text": "Failed to fetch weather data: API rate limit exceeded" } ],
    "isError": true } }
```

> **2025-11-25 clarification:** input/parameter validation errors should be returned as **tool execution errors** (`isError: true`), *not* protocol errors — so the model can read the message and self-correct. *"Clients SHOULD provide tool execution errors to language models to enable self-correction. Clients MAY provide protocol errors to language models, though these are less likely to result in successful recovery."*

This distinction matters for design: a JSON-RPC protocol error is for "this call is structurally invalid / impossible"; a tool execution error is for "the call was understood but the work failed, and the model might do better next time."

## `notifications/tools/list_changed`

```json
{ "jsonrpc": "2.0", "method": "notifications/tools/list_changed" }
```

## Security considerations (normative)

- Servers **MUST**: validate all tool inputs; implement access controls; rate-limit invocations; sanitize outputs.
- Clients **SHOULD**: confirm sensitive operations with the user; show tool inputs before calling (to prevent data exfiltration); validate results before passing them to the LLM; apply timeouts; log usage for audit.

## Differences from 2025-06-18 (tools-relevant)

- **`icons`** added to tools (and resources, resource templates, prompts).
- **`execution.taskSupport`** added — `"forbidden"` (default) / `"optional"` / `"required"`, tied to the new experimental **Tasks** utility (durable requests with polling / deferred result retrieval).
- **Tool name rules** formalized (1–128 chars, `A–Z a–z 0–9 _ - .`, case-sensitive, unique).
- **JSON Schema 2020-12** is the default dialect; `inputSchema` MUST be a valid schema object (not `null`).
- **Input validation errors → tool execution errors** (`isError: true`) rather than protocol errors.
