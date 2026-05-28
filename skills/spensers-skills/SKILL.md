---
name: spensers-skills
description: Find and install skills from Spenser's personal skills repo (github.com/spenserhale/skills). Use when the user asks "find Spenser's skill for X", "do I have a skill for X", "install one of Spenser's skills", or "check Spenser's skills repo".
---

# Spenser's Skills

Discover and install skills from Spenser Hale's personal skills repository at `github.com/spenserhale/skills`.

## When to Use

Activate this skill when the user:

- Asks "find Spenser's skill for X" or "do I have a skill for X"
- Says "check Spenser's skills" or "look in my skills repo"
- Wants to install a skill from Spenser's GitHub collection
- Asks if a skill exists for a tool or workflow Spenser commonly uses

## Workflow

### Step 1: Fetch the Current Skills Index

Read the live index from GitHub to get the up-to-date list:

```
https://raw.githubusercontent.com/spenserhale/skills/main/readme.md
```

The index is a markdown table listing every skill name and its description.

### Step 2: Match Against the User's Request

Scan the table for skills whose name or description matches what the user is looking for. Present any matches with:

- The skill name
- What it does (from the description column)
- The install command

### Step 3: Install the Skill

**Install for the current project only:**
```bash
npx skills add spenserhale/skills@<skill-name>
```

**Install globally (available in every project):**
```bash
npx skills add spenserhale/skills@<skill-name> -g -y
```

Ask the user whether they want it installed globally or just for the current project before running.

## Current Skills (as of last update)

| Skill | Description |
|-------|-------------|
| `wordpress-cli` | WP-CLI commands for managing WordPress — plugins, themes, users, database, content, cache, and more |
| `wp-vip-cli` | VIP-CLI for local dev environments and remote VIP Platform commands |
| `1password-cli` | `op inject` for securely populating config and `.env` files from vault secrets |
| `add-mcp` | One-command MCP server install across Claude Code, Cursor, VS Code, Codex, Gemini CLI, Goose, OpenCode, Zed, Claude Desktop |
| `agent-native-cli-creator` | Best practices for designing CLIs that AI agents can drive reliably |
| `viteplus-cli` | Vite+ (`vp`) monorepo task runner and packager for mixed browser-app and Node-CLI workspaces |
| `wp-components` | `@wordpress/components` reference for Gutenberg block-editor UI |
| `agents-init` | Scaffold a project for all AI coding agents — AGENTS.md router, docs/ policies, .agents/skills/ workflows |

Always fetch the live index first — this table may be stale.

## When No Match Is Found

If no skill matches, tell the user and offer to help directly without a skill. You can also point them to the repo to browse:

```
https://github.com/spenserhale/skills
```
