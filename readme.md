# Spenser Hale — Skills Repo

A curated collection of Agent skills for the tools and workflows I use most. Each skill teaches Agent how to work effectively with a specific CLI, framework, or platform so I can get reliable help without re-explaining context every time.

## Skills

| Skill | Description |
|-------|-------------|
| [WordPress CLI](skills/wordpress-cli/SKILL.md) | WP-CLI commands for managing WordPress — plugins, themes, users, database, content, cache, and more |
| [WP VIP CLI](skills/wp-vip-cli/SKILL.md) | VIP-CLI for local dev environments (`vip dev-env`) and remote VIP Platform commands (`vip wp`) |
| [1Password CLI](skills/1password-cli/SKILL.md) | `op inject` for securely populating config and `.env` files from vault secrets |
| [add-mcp](skills/add-mcp/SKILL.md) | One-command MCP server install across Claude Code, Cursor, VS Code, Codex, Gemini CLI, Goose, OpenCode, Zed, Claude Desktop |
| [agent-native-cli-creator](skills/agent-native-cli-creator/SKILL.md) | Best practices for designing CLIs that AI agents can drive reliably — non-interactive flags, structured output (TOON / JSON / CSV), enumerated errors, idempotent mutations, profiles, `--wait`, three-layer introspection |
| [Vite+ CLI](skills/viteplus-cli/SKILL.md) | Vite+ (`vp`) monorepo task runner and packager — `vp create`, `vp dev`, `vp build`, `vp run`, `vp pack` for mixed browser-app and Node-CLI workspaces with pnpm |
| [WP Components](skills/wp-components/SKILL.md) | `@wordpress/components` reference for Gutenberg block-editor UI — picking the right component, inspector controls, toolbars, modals, and per-component docs in `references/` |
| [agents-init](skills/agents-init/SKILL.md) | Scaffold a project for all AI coding agents — creates `AGENTS.md` router, `docs/` policy files, `.agents/skills/` workflows, and a `CLAUDE.md` adapter |
| [doc-it](skills/doc-it/SKILL.md) | Document the current work using this project's established process (markdown, Confluence, Notion, changelog, etc.) — asks once to set it up if no process is defined yet |
| [Spenser's Skills](skills/spensers-skills/SKILL.md) | Find and install skills from this repo — searches the index and runs `npx skills add spenserhale/skills@<skill>` |
| [mcp-creator](skills/mcp-creator/SKILL.md) | Build MCP servers — overview + router into the official spec (architecture, transports, resources, prompts, auth, client features) with an opinionated best-practices guide; hands off tools to `mcp-tools-creator` |
| [mcp-tools-creator](skills/mcp-tools-creator/SKILL.md) | Design MCP tools agents use reliably — `domain_verb_noun` naming, intent over CRUD, strong schemas, contextful returns, error/annotation patterns; spec + opinionated best-practices |
| [repo-explorer](skills/repo-explorer/SKILL.md) | Clone and inspect external repositories in a reusable `~/.explore/repos` cache without cluttering the workspace — plus symlinking a project's gitignored `refs/example-repo` into the cache as `source` |

## References

- https://developers.openai.com/codex/skills/
- https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en
