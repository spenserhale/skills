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

## Reference

- Blog post: https://neon.com/blog/add-mcp
