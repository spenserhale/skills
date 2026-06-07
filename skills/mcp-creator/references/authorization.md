# MCP Authorization — Specification

> **This file is the SPECIFICATION** for authorization. Descriptive, not opinionated. Applies to **HTTP-based transports** (Streamable HTTP); stdio servers inherit the host's local trust boundary and do not use this. See `best-practices.md` for opinions.

## Model

MCP authorization is built on **OAuth 2.0**. The MCP server acts as an OAuth **resource server**; a separate authorization server issues tokens. The client obtains a token and presents it as a bearer token on requests.

Key standards the spec aligns to:

- **OAuth 2.0** (and OAuth 2.1 drafts' security guidance).
- **RFC 9728 — Protected Resource Metadata.** The server publishes metadata describing its authorization requirements at a `.well-known` location, so clients can discover where/how to authenticate.
- **RFC 8414 — Authorization Server Metadata** for discovery of the auth server.

## Discovery flow (high level)

1. Client makes an unauthenticated request.
2. Server responds `401` and points the client to its Protected Resource Metadata.
3. Client discovers the authorization server, obtains a token (authorization code + PKCE, or other supported grant).
4. Client retries with `Authorization: Bearer <token>`.

## 2025-11-25 additions

- **OpenID Connect Discovery 1.0** support for discovering the authorization server.
- **Incremental scope consent** signaled via the `WWW-Authenticate` header — the server can request additional scopes mid-session.
- **OAuth Client ID Metadata Documents** — clients can be identified by a URL pointing to their metadata, easing dynamic client registration.
- **RFC 9728 alignment:** `WWW-Authenticate` becomes optional, with a `.well-known` fallback for discovery.

## Security (normative intent)

- Tokens MUST be validated (audience, expiry, scopes) before honoring a request.
- Servers SHOULD scope tokens to the minimum required.
- Authorization does not replace the consent principles in `specification.md` — a valid token still does not imply the user consented to a specific destructive action.
