# MCP Resources — Specification

> **This file is the SPECIFICATION** for the Resources server feature. Descriptive, not opinionated. See `specification.md` for the core protocol and `best-practices.md` for design opinions.

## What resources are

**Resources** expose context and data to the host — files, database rows, API responses, anything addressable by URI. They are **application-driven**: the host decides how/when to surface them (attach to context, let the user pick, etc.). Contrast with tools (model-controlled) and prompts (user-controlled).

## Capability

```json
{ "capabilities": { "resources": { "subscribe": true, "listChanged": true } } }
```

- `subscribe` — client may subscribe to change notifications for individual resources.
- `listChanged` — server emits `notifications/resources/list_changed` when the set of resources changes.

Both sub-features are optional.

## Methods

| Method | Purpose |
|---|---|
| `resources/list` | List available resources (paginated) |
| `resources/read` | Read the contents of a resource |
| `resources/templates/list` | List URI templates (paginated) |
| `resources/subscribe` | Subscribe to updates for a specific resource |
| `resources/unsubscribe` | Cancel a subscription |
| `notifications/resources/list_changed` | The resource list changed |
| `notifications/resources/updated` | A subscribed resource changed |

## Resource object

| Field | Required | Meaning |
|---|---|---|
| `uri` | yes | Unique identifier |
| `name` | yes | Programmatic name |
| `title` | optional | Human-readable display name |
| `description` | optional | What the resource is |
| `mimeType` | optional | MIME type |
| `size` | optional | Size in bytes |
| `icons` | optional *(2025-11-25)* | UI icons |
| `_meta` | optional | Metadata escape hatch |

## Resource contents (`resources/read`)

Returns `contents[]`; each item is either **text** (`text`) or **binary** (`blob`, base64), with its own `uri` and `mimeType`.

## Resource templates (`resources/templates/list`)

For parameterized resources. Fields: `uriTemplate` (RFC 6570), `name`, `title`, `description`, `mimeType`. Template arguments are autocompletable via the **Completion** API. Paginated.

## Annotations (shared)

These annotations are shared by resources, templates, and content blocks (and reused by tool/prompt content):

- `audience` — array of `"user"` / `"assistant"`.
- `priority` — number `0.0`–`1.0` (`1` = most important / required, `0` = least).
- `lastModified` — ISO 8601 timestamp.

## Common URI schemes

- `https://` — client may fetch directly.
- `file://` — filesystem-like; MAY use XDG MIME types such as `inode/directory`.
- `git://`.
- Custom schemes — permitted, MUST comply with RFC 3986.

## Subscriptions

```json
{ "jsonrpc": "2.0", "method": "notifications/resources/updated",
  "params": { "uri": "file:///project/src/main.rs" } }
```

## Errors

- Resource not found → `-32002` (the error `data` carries the `uri`).
- Internal error → `-32603`.

## Security (normative)

Servers MUST validate all resource URIs. Access controls SHOULD protect sensitive resources. Binary data MUST be properly encoded. Permissions SHOULD be checked before operations.
