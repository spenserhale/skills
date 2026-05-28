---
name: agents-init
description: Scaffold a project for all AI coding agents using the three-layer progressive disclosure model — AGENTS.md router, docs/ policies, .agents/skills/ workflows — plus a thin CLAUDE.md adapter. Use this skill whenever the user says "set up this project for AI agents", "init agents", "create AGENTS.md", "make this repo agent-ready", "add agent guidance", "scaffold agent tooling", or wants to add multi-agent context files to a codebase. Also use it when asked to improve or migrate an existing AGENTS.md or CLAUDE.md.
---

# Agents Init

Sets up a project with a vendor-neutral, multi-agent guidance structure so every coding agent (Claude Code, Codex, Cursor, Windsurf, GitHub Copilot, Goose, OpenCode, and future tools) works from the same source of truth without duplicated or conflicting instructions.

## The Three-Layer Model

| Layer | Location | Purpose | When loaded |
|-------|----------|---------|-------------|
| Router | `AGENTS.md` | Always-on rules, progressive disclosure index | Automatically by most agents |
| Policies | `docs/<topic>.md` | Domain-specific project explanations and constraints | On demand, only when task touches that domain |
| Workflows | `.agents/skills/*/SKILL.md` | Repeatable multi-step tasks with steps, scripts, references | On demand, when task matches |

A thin `CLAUDE.md` adapter points Claude Code to `AGENTS.md` so there's one source of truth. Other tool-specific files (Cursor rules, Windsurf rules, Cline rules, etc.) are left for those tools to manage — the key insight is that `AGENTS.md` is already read natively by most agents without any extra config.

The deeper insight: agents shouldn't load everything upfront. A 300-line `AGENTS.md` that covers every edge case gets ignored or bloats context. A 200-line router that says "for security, read `docs/security.md`" gives the agent what it needs exactly when it needs it.

## Workflow

### Step 1: Survey the Project

Read the project before generating anything. Understanding it well makes everything downstream more useful — especially the progressive disclosure index and the done criteria commands.

Check for:
- **Tech stack**: `package.json`, `composer.json`, `requirements.txt`, `go.mod`, `Gemfile`, `Cargo.toml`, `pyproject.toml`
- **Existing AI guidance**: `AGENTS.md`, `CLAUDE.md` — check what's already there
- **Commands**: `package.json` scripts, `Makefile`, `composer.json` scripts — find the actual test, lint, and build commands
- **Project overview**: `README.md`
- **Existing docs structure**: `docs/` directory — note the format (plain markdown, Docusaurus, MkDocs, etc.) and existing organization
- **Integrations**: imports or config files hinting at Sentry, Stripe, HubSpot, Datadog, etc.

From this, determine:
- What the project does (one paragraph for the AGENTS.md Purpose section)
- Primary language(s), frameworks, and tools
- The actual commands to run tests and builds (not `npm test` as a placeholder — the real thing)
- Which domains have enough complexity to warrant a policy doc
- Where policy docs should live given the existing docs structure

### Step 2: Determine the Docs Path

Before proposing files, figure out where `docs/` policy files should go:

- If the project has no `docs/` directory: create `docs/` at the repo root with plain markdown files
- If `docs/` exists and is plain markdown: add new files there, matching the existing naming conventions
- If `docs/` uses a doc framework (Docusaurus, MkDocs, VitePress, etc.): add files in the appropriate source directory (e.g., `docs/docs/` for Docusaurus, `docs/` for MkDocs) and follow the existing file naming style
- If the project uses a completely different conventions (e.g., `documentation/`, `wiki/`): use that location instead

The goal is that agent-facing policy docs live alongside human-facing docs, not in a separate namespace. They're useful to both audiences.

### Step 3: Propose the Structure

Before writing any files, tell the user what you found and what you plan to create:

- What the docs path will be and why
- Which policy doc files you'll scaffold and why each one is relevant
- Whether any existing files will be updated vs. left alone
- Whether you'll create `.agents/skills/` stubs
- Offer a choice: **minimal** (AGENTS.md + CLAUDE.md only) vs. **full** (AGENTS.md + policy docs + skill scaffold)

Get a quick thumbs-up before writing files. The user knows their project — they may redirect you on which domains matter or where docs should go.

### Step 4: Create AGENTS.md

Write `AGENTS.md` to the project root. Target 150–250 lines — shorter is better if the project is small. Here's the structure:

```markdown
# AGENTS.md

## Purpose
[One paragraph: what this repo does and what this file is for]

## Quick start
[The 2–4 commands an agent needs to install deps, run tests, and build — use real commands from the project]

## Repo layout
[Brief map of directories that matter for coding — src, tests, config, docs, etc.]

## Progressive disclosure
Before editing, check whether the task touches one of these areas and read the referenced doc first:
- [Domain]: read `docs/[file].md`
[One line per domain. Only list files that exist or that you're creating right now.]

## Skills
Use `.agents/skills/` when the task matches a documented workflow:
- `.agents/skills/[name]/` — [one-line description]
[Only include this section if skills actually exist.]

## Done criteria
Before finishing any task:
- Run [real test command] and fix failures before declaring done
- If a check was skipped, say why
- Flag risky assumptions explicitly
- Update docs when behavior, architecture, or operational process changes
```

Key principles when writing AGENTS.md:
- Use real commands from the project. Placeholders get ignored; real commands get run.
- Only list progressive disclosure entries for docs that will actually exist after this run.
- Keep it a router. If you find yourself writing a full explanation of a domain, move it to a policy doc.

### Step 5: Create Policy Docs

For each relevant domain, create a `docs/<topic>.md` (or wherever you determined in Step 2). Structure each file:

```markdown
# [Domain Title]

## Purpose
Use this guide when [specific trigger — what task context makes this file relevant].

## Policy
[Bullet-point rules the agent should follow — make them actionable and project-specific]

## Implementation notes
[Project-specific conventions, gotchas, known patterns — things not obvious from reading the code]

## Related docs
- [Link to other doc files that intersect with this one]
```

Common domains to consider (create only what's relevant to this project):

| Domain | File | When relevant |
|--------|------|---------------|
| Error handling | `error-handling.md` | Any backend or service project |
| Security | `security.md` | Auth, user data, APIs, financial data |
| Database | `database.md` | Projects with schema or query concerns |
| Logging | `logging.md` | Backend services with observability needs |
| Testing | `testing.md` | Projects with meaningful test conventions |
| Deployment / CI | `deployment.md` | Projects with non-trivial deploy or branch rules |
| API conventions | `api.md` | REST/GraphQL APIs with versioning or auth patterns |
| Integration-specific | `sentry.md`, `hubspot.md`, etc. | Discovered during survey |

For large domains (more than ~150 lines of real content), use a folder:
```
docs/sentry/
  index.md          # summary + when to use the skill
  cli.md            # tool usage
  issue-triage.md   # step-by-step diagnosis
```
Point AGENTS.md only to the `index.md`.

Don't create stubs with placeholder content. If you don't have real policy to write for a domain, leave a TODO comment in AGENTS.md instead: `# TODO: document error-handling conventions in docs/error-handling.md`

### Step 6: Create CLAUDE.md

Write a thin adapter so Claude Code follows the same source of truth:

```markdown
# CLAUDE.md
Follow `AGENTS.md` for all project conventions, commands, and guidelines.
```

If `CLAUDE.md` already exists:
- Short with good content: add a line at the top pointing to AGENTS.md and keep the rest
- Long/encyclopedic: migrate the content into AGENTS.md or the appropriate policy doc, then replace with a pointer
- Already points to AGENTS.md: leave it alone

### Step 7: Scaffold .agents/skills/ (Optional)

If the project has clear candidates for repeatable workflows, create `.agents/skills/` with a brief README:

```markdown
# Skills

Repeatable agent workflows for this project. Each subdirectory contains a SKILL.md.

Add a skill when a task has well-defined inputs, steps, and expected outputs that an agent would run repeatedly.
```

Offer to stub out one skill if you identified a strong candidate during the survey — things like:
- A complex external integration with its own CLI or API (Sentry, Datadog, HubSpot)
- A multi-step debug flow that always follows the same pattern
- A data sync or migration workflow

A stub is better than nothing — it shows contributors the pattern to follow.

## What to Avoid

**Don't use `@import` in CLAUDE.md for policy docs.** Claude Code's `@path/to/file` imports expand at launch and bloat the context window for every task, even irrelevant ones. Plain path references let the agent load them only when needed.

**Don't create policy docs with nothing real to say.** A file that says "handle errors carefully" isn't useful. Leave a TODO comment in AGENTS.md instead.

**Don't over-engineer the first pass.** A lean AGENTS.md that's actually followed beats a comprehensive one that gets ignored. The structure can grow as the team adds more docs and skills.

## Updating an Existing Setup

If `AGENTS.md` or `CLAUDE.md` already exist, read them before touching anything:

1. Identify what's already good and keep it
2. Move overly long content into the right layer: encyclopedic rules → policy docs, repeatable workflows → `.agents/skills/`
3. Update the progressive disclosure index in AGENTS.md to reflect what actually exists
4. Slim CLAUDE.md down to a pointer if it's grown large
