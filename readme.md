# Spenser Hale — Skills Repo

A curated collection of Agent skills for the tools and workflows I use most. Each skill teaches Agent how to work effectively with a specific CLI, framework, or platform so I can get reliable help without re-explaining context every time.

Skills come in two flavors:

- **User skills** are agnostic and useful across projects — install them once to your user profile.
- **Project skills** are tied to a specific framework or task — install them per project, in the repos where they apply.

## Recommended workflow bundles

These live in their own repos (they're coupled, multi-skill workflows rather than single skills) but are the development loops I reach for most. Both are de-hooked, on-demand clones of the same **spec → plan → implement → verify** workflow — pick by how much you want to be in the loop:

| Bundle | Trigger | Use it when |
|--------|---------|-------------|
| [agentic-driven-development](https://github.com/spenserhale/agentic-driven-development) | `/agentic-driven-development <task>` | You want it **unattended** — it sizes the task, plans it for parallel work (superlite-style), decides for itself (rulings with their cost if wrong, decision records for strong calls), builds with tiered subagents, and opens a PR with no human in the loop. Great for firing off several in the background. |
| [human-driven-development](https://github.com/spenserhale/human-driven-development) | `/human-driven-development <task>` | You want to **stay in the loop** — it brainstorms with you and pauses for approval at every gate (the design and its decision records, the written design, plan review with the execution choice, and the final merge/PR choice). |

Each repo's README covers install (as flat `npx skills` collections today; may move to plugin-based installs). Skills are prefixed `add-` / `hdd-` respectively so both can be installed side by side. Both read the project's docs map from the `## Documentation` section that [agents-init](skills/agents-init/SKILL.md) writes, keep specs current and decisions recorded, and make every commit carry its code, tests, and docs together.

## User skills

Install once to your user profile; available in every project.

| Skill | Description |
|-------|-------------|
| [aaa](skills/aaa/SKILL.md) | Arrange · Act · Assert (`/aaa`) — a lightweight three-step loop for one-shot tasks (coding or not): gather context + plan, do the work inline, then prove it worked (tests, dry run, browser, data check). Loops back to Arrange with the failure as new context when validation fails |
| [github-ref](skills/github-ref/SKILL.md) | Inspect external GitHub source, docs, and examples in a shared per-user cache, refreshed and locked through reads, with detached worktrees for explicit refs |
| [repo-explorer](skills/repo-explorer/SKILL.md) | Clone and inspect external repositories in a reusable `~/.explore/repos` cache without cluttering the workspace — plus symlinking a project's gitignored `refs/example-repo` into the cache as `source` |
| [doc-it](skills/doc-it/SKILL.md) | Document the current work using this project's established process (markdown, Confluence, Notion, changelog, etc.) — asks once to set it up if no process is defined yet |
| [reflect](skills/reflect/SKILL.md) | Sprint retro for a thread (`/reflect`) — what worked, what didn't, which docs or skills were stale, and which lookups burned tokens a CLI or API would have saved; routes each finding to the smallest durable fix and waits for approval. Ships a transcript reader that measures tool-result cost in Claude Code |
| [kaizen](skills/kaizen/SKILL.md) | Quality-first working mode (`/kaizen on`) after the Toyota Production System — every failing test, warning, and deprecation notice gets noticed, then triaged: your own defects fixed first, small in-path ones fixed in passing, the rest reported at end of turn with evidence instead of fixed or ignored. `/kaizen audit [path]` measures a repo's dev process (checks, feedback time, CI gates, standing inventory) and recommends one improvement to do first |
| [Spenser's Skills](skills/spensers-skills/SKILL.md) | Find and install skills from this repo — searches the index and runs `npx skills add spenserhale/skills@<skill>` |
| [agents-init](skills/agents-init/SKILL.md) | Scaffold a project for all AI coding agents — an `AGENTS.md` router with a docs map and shared coding standards, a `CLAUDE.md` adapter, and a docs structure for living feature specs, decision records (ADRs), change plans, and guides in Starlight-compatible Markdown. Asks one batch of questions or uses the defaults; can scaffold a Starlight site over the same files |
| [add-mcp](skills/add-mcp/SKILL.md) | One-command MCP server install across Claude Code, Cursor, VS Code, Codex, Gemini CLI, Goose, OpenCode, Zed, Claude Desktop |
| [Codex CLI](skills/codex-cli/SKILL.md) | Drive OpenAI's Codex CLI as a delegated sub-agent — `codex exec` non-interactively, capture the result from stdout/JSON/schema, and control sandbox, approvals, model, and sessions |
| [OpenCode CLI](skills/opencode-cli/SKILL.md) | Drive the OpenCode terminal agent as a delegated sub-agent — `opencode run` non-interactively, pipe context via stdin, capture stdout/JSON, and control model, agent, `--auto`, and sessions |
| [hand-and-brain](skills/hand-and-brain/SKILL.md) | "Be the brain" or `/hand-and-brain` — a top-tier model stays the brain (decisions, briefs, review) and routes reading, search, and mechanical work to cheaper same-family subagents (Opus → Sonnet/Haiku, Sol → Terra/Luna, GLM → GLM-flash) to save context and tokens; cross-harness hands only when you name them |
| [with-advisor](skills/with-advisor/SKILL.md) | "Use X as an advisor" or `/with-advisor` — a mid-tier model runs the long thread and consults a stronger same-family model (Sonnet → Opus, Terra → Sol, GLM-flash → GLM) as a read-only advisor for plan review, hard decisions, and getting unstuck; cross-harness advisors only when you name them |
| [1Password CLI](skills/1password-cli/SKILL.md) | `op inject` for securely populating config and `.env` files from vault secrets |
| [agent-native-cli-creator](skills/agent-native-cli-creator/SKILL.md) | Best practices for designing CLIs that AI agents can drive reliably — non-interactive flags, structured output (TOON / JSON / CSV), enumerated errors, idempotent mutations, profiles, `--wait`, three-layer introspection |
| [mcp-creator](skills/mcp-creator/SKILL.md) | Build MCP servers — overview + router into the official spec (architecture, transports, resources, prompts, auth, client features) with an opinionated best-practices guide; hands off tools to `mcp-tools-creator` |
| [mcp-tools-creator](skills/mcp-tools-creator/SKILL.md) | Design MCP tools agents use reliably — `domain_verb_noun` naming, intent over CRUD, strong schemas, contextful returns, error/annotation patterns; spec + opinionated best-practices |
| [sh-skill-creator](skills/sh-skill-creator/SKILL.md) | Create, restructure, review, or audit agent skills against a 2026 rule set — trigger-first descriptions, lean bodies, one-level references, evals with a baseline, security audit — with a scaffolder and a spec + house-rules validator |
| [outlook-web-rules](skills/outlook-web-rules/SKILL.md) | Read, audit, create, and edit Outlook web rules through a signed-in browser; focused observations, exact sender + subject filters, duplicate checks, and verified edits |
| [video-pitch](skills/video-pitch/SKILL.md) | Produce a ~20-second video pitch of a feature, tool, PR, or app for customer success, sales, or stakeholders — narration over a real screen-recorded demo, frame-exact HTML motion scenes, captions, poster, share blurb; local tools only (ffmpeg, Chrome, playwright-core, any TTS) |

**Install / update all user skills** (installs any you're missing and updates the rest to latest, across every detected agent):

```sh
npx skills add spenserhale/skills --global --agent '*' -y \
  --skill aaa \
  --skill github-ref \
  --skill repo-explorer \
  --skill doc-it \
  --skill reflect \
  --skill kaizen \
  --skill spensers-skills \
  --skill agents-init \
  --skill add-mcp \
  --skill codex-cli \
  --skill opencode-cli \
  --skill hand-and-brain \
  --skill with-advisor \
  --skill 1password-cli \
  --skill agent-native-cli-creator \
  --skill mcp-creator \
  --skill mcp-tools-creator \
  --skill sh-skill-creator \
  --skill outlook-web-rules \
  --skill video-pitch
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
