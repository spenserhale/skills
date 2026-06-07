# MCP Prompts — Specification

> **This file is the SPECIFICATION** for the Prompts server feature. Descriptive, not opinionated. See `specification.md` for the core protocol and `best-practices.md` for design opinions.

## What prompts are

**Prompts** are templated messages and workflows the server offers to the user — typically surfaced as slash commands, menu items, or quick actions. They are **user-controlled**: the user chooses to invoke them. Contrast with tools (model-controlled) and resources (application-driven).

## Capability

```json
{ "capabilities": { "prompts": { "listChanged": true } } }
```

- `listChanged` — server emits `notifications/prompts/list_changed` when the prompt set changes.

## Methods

| Method | Purpose |
|---|---|
| `prompts/list` | List available prompts (paginated) |
| `prompts/get` | Resolve a prompt into messages |
| `notifications/prompts/list_changed` | The prompt list changed |

## Prompt object

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Unique identifier |
| `title` | optional | Human-readable display name |
| `description` | optional | What the prompt does |
| `arguments` | optional | List of arguments |
| `icons` | optional *(2025-11-25)* | UI icons |
| `_meta` | optional | Metadata escape hatch |

Each **argument**: `name`, `description`, `required`.

## `prompts/get`

Takes `name` + `arguments` (arguments autocompletable via the **Completion** API). Returns a `description` plus `messages[]`.

### PromptMessage

- `role` — `"user"` or `"assistant"`.
- `content` — one of:
  - **Text** — `{ "type": "text", "text": "..." }`
  - **Image** — `{ "type": "image", "data": "<base64>", "mimeType": "..." }`
  - **Audio** — `{ "type": "audio", "data": "<base64>", "mimeType": "..." }`
  - **Embedded resource** — `{ "type": "resource", "resource": { "uri", "mimeType", "text" | "blob" } }`

All content blocks support the shared annotations (`audience`, `priority`, `lastModified`).

## Errors

- Invalid prompt name / missing required arguments → `-32602`.
- Internal error → `-32603`.

## Implementation & security (normative)

- Servers SHOULD validate arguments before processing; clients SHOULD handle pagination; both SHOULD respect capability negotiation.
- *"Implementations MUST carefully validate all prompt inputs and outputs to prevent injection attacks or unauthorized access to resources."*
