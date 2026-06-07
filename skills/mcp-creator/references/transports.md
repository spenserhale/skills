# MCP Transports — Specification

> **This file is the SPECIFICATION** for transports. Descriptive, not opinionated. See `specification.md` for the core protocol and `best-practices.md` for design opinions on which to choose.

All transports carry **JSON-RPC 2.0** messages. The protocol defines two standard transports.

## stdio

The server runs as a subprocess of the host. Messages are exchanged over standard input/output.

- The client writes JSON-RPC to the server's **stdin**; the server writes JSON-RPC to its **stdout**.
- Messages are newline-delimited; a single message MUST NOT contain embedded newlines.
- **stdout is reserved for protocol messages.** Anything else corrupts the stream.
- The server MAY use **stderr** for logging (clarified/expanded in 2025-11-25 — stderr may carry all logging).

Best fit: local servers, CLI-launched integrations, single-user desktop hosts.

## Streamable HTTP

The server runs as an independent HTTP service. The client POSTs JSON-RPC requests; the server responds with JSON or an **SSE** (Server-Sent Events) stream for streaming/multiple messages.

- A single HTTP endpoint handles POST (client → server) and supports SSE for server → client streaming.
- **Origin validation:** the server MUST return **`403`** for an invalid `Origin` header (DNS-rebinding protection; tightened in 2025-11-25).
- SSE supports resumption/polling (clarified in 2025-11-25) so a dropped stream can be resumed.
- Sessions may be tracked via a session id header.

Best fit: remote/hosted servers, multi-user services, anything behind auth.

> Authorization (OAuth 2.0 / OIDC) applies to HTTP-based transports — see `authorization.md`.

## Choosing (spec-level facts)

- stdio: lowest overhead, local trust boundary, no network exposure.
- Streamable HTTP: network-reachable, requires Origin validation and (typically) authorization.

(An earlier "HTTP+SSE" transport from the original spec has been superseded by Streamable HTTP.)
