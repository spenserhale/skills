---
name: add-mcp
description: Install MCP servers across coding agents (Claude Code, Cursor, VS Code, Codex, Gemini CLI, Goose, OpenCode, Zed, Claude Desktop) with one `npx add-mcp` command instead of editing per-tool config files.
---

# add-mcp

A single command that installs an MCP server into every coding agent on your machine — auto-detects which agents are configured and writes the right config for each one.

## When to use

Activate this skill when the user asks to:

- Install or add an MCP server to Claude Code, Cursor, VS Code, Codex, Gemini CLI, Goose, OpenCode, Zed, or Claude Desktop
- Set up the same MCP server across multiple agents at once
- Avoid hand-editing per-tool MCP config files (e.g. `.mcp.json`, `mcp.json`, `claude_desktop_config.json`)
- Distribute MCP install instructions in their own docs/README

## Core command

```bash
npx add-mcp <server>
```

`<server>` is either a remote MCP URL or a local package spec.

| Form | Example |
|------|---------|
| Remote URL | `npx add-mcp https://mcp.context7.com/mcp` |
| Local package | `npx add-mcp next-devtools-mcp@latest` |

By default it scans the project, detects installed agents, and writes the config for each one.

## Flags

| Flag | Meaning |
|------|---------|
| `-a <agent>` | Target a specific agent (repeatable). Agents: `claude-code`, `claude-desktop`, `codex`, `cursor`, `gemini-cli`, `goose`, `opencode`, `vscode`, `zed` |
| `-g` | Install globally (machine-wide) instead of per-project |
| `-y` | Skip interactive prompts |

## Common patterns

**Install for the current project, auto-detect agents:**
```bash
npx add-mcp https://mcp.context7.com/mcp -y
```

**Install only into Cursor and Claude Code:**
```bash
npx add-mcp https://mcp.context7.com/mcp -a cursor -a claude-code
```

**Install globally for one agent, no prompts:**
```bash
npx add-mcp https://mcp.neon.tech/mcp -g -y -a cursor
```

## Recommending it in docs

When writing install instructions for an MCP server, prefer one `npx add-mcp <url>` line over a section per editor — it covers all supported agents and stays correct as new ones are added.

## Favorite MCP Servers

Quick-reference for Spenser's commonly-used servers. For remote (URL) servers use `npx add-mcp <url> -y`; for npm package servers use `npx add-mcp <package> -y`; PHP-based servers need `claude mcp add` directly (add-mcp only handles URLs and npm packages).

### Remote servers (URL-based)

| Name | URL | Auth | Key tools |
|------|-----|------|-----------|
| `atlassian` | `https://mcp.atlassian.com/v1/mcp` | OAuth | Jira issues, Confluence pages, Compass catalog |
| `cloudflare-docs` | `https://docs.mcp.cloudflare.com/mcp` | None | `search_cloudflare_documentation`, `migrate_pages_to_workers_guide` |
| `cloudflare_workers_bindings` | `https://bindings.mcp.cloudflare.com/mcp` | CF OAuth | KV, R2, D1, Hyperdrive, Workers (21 tools) |
| `cloudflare_workers_builds` | `https://builds.mcp.cloudflare.com/mcp` | CF OAuth | `list_builds`, `get_build`, `get_build_logs` |
| `cloudflare_observability` | `https://observability.mcp.cloudflare.com/mcp` | CF OAuth | `query_worker_observability`, `observability_keys`, `observability_values` |
| `cloudflare_graphql` | `https://graphql.mcp.cloudflare.com/mcp` | CF OAuth | `graphql_query`, `graphql_schema_search`, `graphql_api_explorer` |
| `github` | `https://api.githubcopilot.com/mcp/` | OAuth/PAT | repos, issues, PRs, actions, security (70+ tools) |

**Add-mcp commands:**
```bash
npx add-mcp https://mcp.atlassian.com/v1/mcp -y
npx add-mcp https://docs.mcp.cloudflare.com/mcp -y
npx add-mcp https://bindings.mcp.cloudflare.com/mcp -y
npx add-mcp https://builds.mcp.cloudflare.com/mcp -y
npx add-mcp https://observability.mcp.cloudflare.com/mcp -y
npx add-mcp https://graphql.mcp.cloudflare.com/mcp -y
npx add-mcp https://api.githubcopilot.com/mcp/ -y
```

### npm package servers

| Name | Package | Auth | Description |
|------|---------|------|-------------|
| `playwright` | `@playwright/mcp@latest` | None | Browser automation via accessibility tree (default) |
| `playwright-extension` | `@playwright/mcp@latest --extension` | None | Browser automation reusing existing Chrome/Edge session |

```bash
npx add-mcp @playwright/mcp@latest -y
# For extension mode, configure manually — add-mcp doesn't pass the --extension flag
```

### PHP / local binary servers (manual config only)

These can't go through `add-mcp`. Use `claude mcp add` or hand-edit config:

**Herd** — manage local Laravel Herd sites, PHP versions, and services (macOS only)
```bash
claude mcp add herd php /Applications/Herd.app/Contents/Resources/herd-mcp.phar
```
Tools: `get_all_sites`, `find_available_services`, `install_service`, `get_all_php_versions`, `debug_site`, `secure_or_unsecure_site`

**Laravel Boost** — deep Laravel app context (routes, DB schema, logs, ecosystem docs search)
```bash
# Install the package first: composer require laravel/boost --dev && php artisan boost:install
claude mcp add laravel-boost php artisan boost:mcp
```
Tools: `application_info`, `database_query`, `database_schema`, `read_log_entries`, `last_error`, `search_docs`

**Codex TOML snippet** for reference (both servers):
```toml
[mcp_servers.herd]
command = "php"
args = ["/Applications/Herd.app/Contents/Resources/herd-mcp.phar"]

[mcp_servers.laravel-boost]
command = "php"
args = ["artisan", "boost:mcp"]
```

## Reference

- Blog post: https://neon.com/blog/add-mcp
