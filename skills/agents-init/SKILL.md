---
name: agents-init
description: "Scaffold a repo for AI coding agents: an AGENTS.md router with shared coding standards, a thin CLAUDE.md adapter, and a docs structure for feature specs, decision records (ADRs), change plans, and guides, written as Starlight-compatible Markdown. Use whenever the user says 'set up this project for AI agents', 'init agents', 'create AGENTS.md', 'make this repo agent-ready', 'set up docs, specs, or ADRs', or wants to improve or migrate an existing AGENTS.md or CLAUDE.md. Not for recording one decision or documenting a finished change; use doc-it instead."
---

# Agents Init

Give every coding agent (Claude Code, Codex, Cursor, Copilot, OpenCode, and the rest) one source of truth: a short `AGENTS.md` router, durable docs it loads only when a task needs them, and rules that keep code, tests, and docs changing in the same commit. Plain Markdown in the repo is the default; a rendered site is an opt-in view over the same files.

## The layers

| Layer | Location | Purpose | Loaded |
|---|---|---|---|
| Router | `AGENTS.md` + a `CLAUDE.md` pointer | Commands, docs map, always-on rules | Every session |
| Project docs | `docs/specs/`, `docs/decisions/`, `docs/plans/`, `docs/product/` | What the product does now, why, and how each change was planned | When a task touches that area |
| Guides | `docs/guides/<topic>.md` | Engineering policies: testing, security, deployment | When a task touches that domain |
| Workflows | `.agents/skills/*/SKILL.md` | Repeatable multi-step tasks | When a task matches |

A 300-line `AGENTS.md` gets skimmed; a router that says "for billing, read `docs/specs/billing.md`" gets followed. The `## Documentation` section you write into `AGENTS.md` is also the contract other skills read (`doc-it`, `agentic-driven-development`, `human-driven-development`), so keep its heading and table columns.

## Workflow

### Step 1: Survey the project

Read before generating anything:

- **Stack and commands**: `package.json`, `pyproject.toml`, `composer.json`, `go.mod`, `Cargo.toml`, `Makefile`, lockfiles. Find the real install, test, lint, and build commands.
- **Existing guidance**: `AGENTS.md`, `CLAUDE.md`, `README.md`.
- **Existing docs structure**: decision folders (`docs/adr/`, `doc/architecture/decisions/`, `docs/decisions/`, `docs/rfcs/`), spec tools (`openspec/`, `.specify/`), workflow output from older runs (`docs/add/`, `docs/hdd/`, `docs/superpowers/`), docs frameworks (Starlight, Docusaurus, MkDocs, VitePress, Mintlify), `CHANGELOG.md`, release tooling (release-please config, `.changeset/`).
- **Commercial signals**: billing or entitlement code (Stripe, plans, tiers, feature flags). They decide whether pricing docs are worth offering.
- **Conventions worth a guide**: rules an agent would otherwise get wrong, visible in config, scripts, or repeated code patterns (a lint config, a deploy script, a testing pattern used across files). One example file is not yet a convention.

Done when you can state the project's purpose in one paragraph, its real commands, and which docs roles already have a home.

### Step 2: Choose the structure: one batch of questions, or the defaults

The default structure and its naming rules are in `references/project-structure.md`; read it now. In short:

```
AGENTS.md  CLAUDE.md  CHANGELOG.md
docs/
  index.md
  product/vision.md          (+ pricing.md for commercial products)
  specs/_template.md         <feature>.md: what it does now
  decisions/_template.md     0001-keep-docs-and-decisions-in-the-repo.md (the structure record), NNNN-<title>.md: why
  plans/_template.md         YYYY-MM-DD-<topic>.md: one change, designed and planned
  guides/<topic>.md          engineering policies, once a domain has real ones
```

Ask once, all questions in one call (AskUserQuestion in Claude Code; otherwise one message), with the recommended option listed first (reorder question 3 when billing code exists). Put what you found and the proposed tree in the question text, so the batch is both the proposal and the approval:

1. **Structure**: Default (recommended) · Customize paths · Minimal (`AGENTS.md` + `CLAUDE.md` only)
2. **Viewable site**: Markdown only (recommended) · Also scaffold a Starlight site that renders `docs/`
3. **Product docs**: Vision only (recommended) · Vision + pricing and plans (recommend this one instead when Step 1 found billing code) · None
4. **Changelog**: `CHANGELOG.md` in Keep a Changelog format (recommended) · None. When release tooling already generates it, skip the question and keep the tool.

Skip any question the repo already answers (an existing Docusaurus site means no site question; existing release tooling means no changelog question), and adopt existing folders without asking (an existing `docs/adr/` is the decisions folder). Skip the whole batch and take the recommended answers when the user said "use the defaults" or "don't ask", or when no human can answer (a headless run); say so in your reply and in the structure record. Under "don't ask", later offers (commit, specs, skill stubs) become follow-ups in the report instead of questions. If they pick Customize, ask one follow-up batch for only the paths that differ; free-text answers come through the tool's Other option. Minimal writes only `AGENTS.md` and `CLAUDE.md`: skip Steps 3 to 6, and follow the Minimal variant in `references/agents-md-template.md`.

### Step 3: Create the docs structure

Copy each asset into the resolved paths:

| Asset | Destination | Write when |
|---|---|---|
| `assets/spec-template.md` | `docs/specs/_template.md` | Always (default or custom structure); drop its Availability section when there is no pricing page |
| `assets/decision-template.md` | `docs/decisions/_template.md` | Always |
| `assets/decision-0001.md` | `docs/decisions/NNNN-keep-docs-and-decisions-in-the-repo.md`: 0001 in a new folder, else the next free number | Always; fill every slot |
| `assets/plan-template.md` | `docs/plans/_template.md` | Always |
| `assets/docs-index.md` | `docs/index.md` | Always; drop rows for folders that do not exist |
| `assets/vision.md` | `docs/product/vision.md` | When the README, the survey, or the user supplies real content |
| `assets/pricing.md` | `docs/product/pricing.md` | Only when chosen and real plans exist; link a machine-readable catalog if the code has one |
| `assets/changelog.md` | `CHANGELOG.md` | When chosen and none exists |

Templates are copied as they are, except folder names: rewrite `docs/decisions/` and `../decisions/` (and the other folders) to the resolved paths. Everything else is filled in: replace each `<placeholder>`, and drop rows and sections that do not apply. For the structure record, the date is today, `status: accepted`, and `decision-makers` is the person who asked for the setup (by name from the conversation, else `git config user.name`) plus the drafting agent by name (for example `Codex (drafting agent)`), even in a headless run: they chose the structure or asked for the defaults. When an earlier record already adopted decision records, the structure record links it and builds on it; it does not supersede it. A product page whose sections apply but lack data keeps one `TODO:` line per missing section, listed in the report.

Existing records keep their format: never rewrite them to match the template. New records use the template; when the folder mixes formats, say so in the docs map.

The `_` prefix keeps templates out of a Starlight build and keeps the folder in git. Do not invent feature specs; offer to write specs for existing features as a follow-up. In an existing structure, map each role onto the folder already in use instead of creating a parallel one, and leave legacy workflow folders (`docs/add/`, `docs/hdd/`) where they are, listed as history in the docs map.

### Step 4: Write guides

For each convention from Step 1 with real policy to state, create `docs/guides/<topic>.md`; read `references/policy-docs.md` when choosing domains and writing each file. A domain that matters but has no policy yet gets a TODO line in `AGENTS.md`'s Progressive disclosure section instead of a stub: `- TODO <Domain> (docs/guides/<topic>.md): <what the guide will cover, and when to write it>`.

### Step 5: Scaffold the Starlight site (only if chosen)

Read `references/starlight.md` and follow it. Done when the site builds with exit 0.

### Step 6: Scaffold `.agents/skills/` (optional)

When the survey found a repeatable workflow (an integration with its own CLI, a fixed debug flow, a data sync), create `.agents/skills/README.md` explaining that each subdirectory holds a `SKILL.md`, and offer to stub that one skill.

### Step 7: Write AGENTS.md

Written last, so it lists only what now exists. Read `references/agents-md-template.md` when writing it. Use the repo's real commands; fill the `## Documentation` table with the resolved paths; copy the `## Coding standards` section as written; list the guides, the TODO lines from Step 4, the site commands from Step 5, and the skills from Step 6. Keep it a router: when a section starts explaining a domain, move that text into a guide.

### Step 8: Write the CLAUDE.md pointer

```markdown
# CLAUDE.md
Follow `AGENTS.md` for all project conventions, commands, and guidelines.
```

An existing short `CLAUDE.md` with good content keeps it under a pointer line at the top. A long one gets migrated into `AGENTS.md` or guides, then replaced with the pointer. One that already points to `AGENTS.md` stays as is.

### Step 9: Report

List the files created, the choices recorded in the structure record, and the follow-ups: specs worth writing for existing features, TODOs left in `AGENTS.md` and the product pages, and repo problems the survey found. Offer to commit everything as one commit (`docs: adopt agent docs structure`).

## Gotchas

- **No `@import` of docs in `CLAUDE.md`.** Claude Code expands imports at launch for every task; plain path references load only when needed.
- **Every page under `docs/` needs `title` frontmatter** and no body H1. A Starlight build fails on a missing title, and a body H1 renders twice.
- **Specs describe what the code does now.** Purpose and vision can come from the README; specs come from the code. When the README promises features the code lacks, say so in `AGENTS.md`'s Purpose and in the report instead of writing a spec for them.
- **Broken commands are reported, not fixed.** A script that cannot work as configured (missing `tsconfig.json`, no lint config, no lockfile) goes into Quick start with a one-line warning and into the report; say whether you ran it or inferred it from the config. Repairing the repo is a separate task, and installing or building to check needs the user's go-ahead.
- **One home per role.** A second decisions folder next to an existing `docs/adr/` splits the record; extend what exists.
- **The site is a view, not the source.** Agents and humans edit `docs/`; the Starlight project only renders it.

## Updating an existing setup

Read `AGENTS.md` and `CLAUDE.md` before touching anything. Keep what is good, move encyclopedic rules into guides and repeatable workflows into `.agents/skills/`, add or refresh the `## Documentation` table so it matches the folders that exist, add the `## Coding standards` section if it is missing, and slim `CLAUDE.md` to a pointer if it has grown.

## Resources

| Read when | File |
|---|---|
| Choosing paths, naming, lifecycle rules, and what counts as a strong decision | `references/project-structure.md` |
| Writing `AGENTS.md` | `references/agents-md-template.md` |
| Choosing and writing guides | `references/policy-docs.md` |
| Scaffolding the Starlight site | `references/starlight.md` |
