# Spenser Hale — Skills Repo

A curated collection of Agent skills for the tools and workflows I use most. Each skill teaches Agent how to work effectively with a specific CLI, framework, or platform so I can get reliable help without re-explaining context every time.

Skills come in two flavors:

- **User skills** are agnostic and useful across projects — install them once to your user profile.
- **Project skills** are tied to a specific framework or task — install them per project, in the repos where they apply.

## Recommended workflow bundles

These live in their own repos (they're coupled, multi-skill workflows rather than single skills) but are the development loops I reach for most. Both are de-hooked, on-demand clones of the same **spec → plan → implement → verify** workflow — pick by how much you want to be in the loop:

| Bundle | Trigger | Use it when |
|--------|---------|-------------|
| [agentic-driven-development](https://github.com/spenserhale/agentic-driven-development) | `/agentic-driven-development <task>` | You want it **unattended** — it researches, decides for itself (recording an Assumptions & Decisions log), builds, and opens a PR with no human in the loop. Great for firing off several in the background. |
| [human-driven-development](https://github.com/spenserhale/human-driven-development) | `/human-driven-development <task>` | You want to **stay in the loop** — it brainstorms with you and pauses for approval at every gate (design, spec, plan, and the final merge/PR choice). |

Each repo's README covers install (as flat `npx skills` collections today; may move to plugin-based installs). Skills are prefixed `add-` / `hdd-` respectively so both can be installed side by side.

## User skills

Install once to your user profile; available in every project.

| Skill | Description |
|-------|-------------|
| [aaa](skills/aaa/SKILL.md) | Arrange · Act · Assert (`/aaa`) — a lightweight three-step loop for one-shot tasks (coding or not): gather context + plan, do the work inline, then prove it worked (tests, dry run, browser, data check). Loops back to Arrange with the failure as new context when validation fails |
| [repo-explorer](skills/repo-explorer/SKILL.md) | Clone and inspect external repositories in a reusable `~/.explore/repos` cache without cluttering the workspace — plus symlinking a project's gitignored `refs/example-repo` into the cache as `source` |
| [doc-it](skills/doc-it/SKILL.md) | Document the current work using this project's established process (markdown, Confluence, Notion, changelog, etc.) — asks once to set it up if no process is defined yet |
| [Spenser's Skills](skills/spensers-skills/SKILL.md) | Find and install skills from this repo — searches the index and runs `npx skills add spenserhale/skills@<skill>` |
| [agents-init](skills/agents-init/SKILL.md) | Scaffold a project for all AI coding agents — creates `AGENTS.md` router, `docs/` policy files, `.agents/skills/` workflows, and a `CLAUDE.md` adapter |
| [add-mcp](skills/add-mcp/SKILL.md) | One-command MCP server install across Claude Code, Cursor, VS Code, Codex, Gemini CLI, Goose, OpenCode, Zed, Claude Desktop |
| [1Password CLI](skills/1password-cli/SKILL.md) | `op inject` for securely populating config and `.env` files from vault secrets |
| [agent-native-cli-creator](skills/agent-native-cli-creator/SKILL.md) | Best practices for designing CLIs that AI agents can drive reliably — non-interactive flags, structured output (TOON / JSON / CSV), enumerated errors, idempotent mutations, profiles, `--wait`, three-layer introspection |
| [mcp-creator](skills/mcp-creator/SKILL.md) | Build MCP servers — overview + router into the official spec (architecture, transports, resources, prompts, auth, client features) with an opinionated best-practices guide; hands off tools to `mcp-tools-creator` |
| [mcp-tools-creator](skills/mcp-tools-creator/SKILL.md) | Design MCP tools agents use reliably — `domain_verb_noun` naming, intent over CRUD, strong schemas, contextful returns, error/annotation patterns; spec + opinionated best-practices |

**Install / update all user skills** (installs any you're missing and updates the rest to latest, across every detected agent):

```sh
npx skills add spenserhale/skills --global --agent '*' -y \
  --skill aaa \
  --skill repo-explorer \
  --skill doc-it \
  --skill spensers-skills \
  --skill agents-init \
  --skill add-mcp \
  --skill 1password-cli \
  --skill agent-native-cli-creator \
  --skill mcp-creator \
  --skill mcp-tools-creator
```

## WordPress project skills

For WordPress repos. Install per project (no `--global` flag).

| Skill | Description |
|-------|-------------|
| [WordPress CLI](skills/wordpress-cli/SKILL.md) | WP-CLI commands for managing WordPress — plugins, themes, users, database, content, cache, and more |
| [WP VIP CLI](skills/wp-vip-cli/SKILL.md) | VIP-CLI for local dev environments (`vip dev-env`) and remote VIP Platform commands (`vip wp`) |
| [WP Components](skills/wp-components/SKILL.md) | `@wordpress/components` reference for Gutenberg block-editor UI — picking the right component, inspector controls, toolbars, modals, and per-component docs in `references/` |

**Install all WordPress skills** into the current repo:

```sh
npx skills add spenserhale/skills --agent '*' -y \
  --skill wordpress-cli \
  --skill wp-vip-cli \
  --skill wp-components
```

## Project skills

Install per project (no `--global` flag) in the repos where they apply.

| Skill | Description |
|-------|-------------|
| [Vite+ CLI](skills/viteplus-cli/SKILL.md) | Vite+ (`vp`) monorepo task runner and packager — `vp create`, `vp dev`, `vp build`, `vp run`, `vp pack` for mixed browser-app and Node-CLI workspaces with pnpm |

**Install a project skill** into the current repo (example):

```sh
npx skills add spenserhale/skills --skill viteplus-cli
```

## References

- https://developers.openai.com/codex/skills/
- https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en
