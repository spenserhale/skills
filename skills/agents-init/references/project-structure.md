# Project structure

The default layout agents-init creates, the naming and lifecycle rules each folder follows, and what counts as a strong decision. `agentic-driven-development` and `human-driven-development` fall back to these same defaults when a repo has no `## Documentation` section, so keep the paths identical across those skills.

## Contents

- The default tree
- The three kinds of project doc
- Naming
- Format: Starlight-compatible Markdown
- Lifecycle rules
- Strong decisions: decision record or ruling
- Atomic commits
- Product and pricing docs
- Customizing and existing structures
- Why this shape

## The default tree

```
AGENTS.md                          router: commands, docs map, rules
CLAUDE.md                          one line: follow AGENTS.md
CHANGELOG.md                       Keep a Changelog, ## [Unreleased] at the top
docs/
  index.md                         docs home: what lives where (the Starlight home page)
  product/
    vision.md                      who it is for, the problem, what it is not
    pricing.md                     commercial products only: plans, entitlements, limits
  specs/
    _template.md
    <feature>.md                   current truth: what the feature does now
  decisions/
    _template.md
    0001-keep-docs-and-decisions-in-the-repo.md
    NNNN-<title>.md                why: one decision per record, superseded, never rewritten
  plans/
    _template.md
    YYYY-MM-DD-<topic>.md          one change: intent, design, spec delta, tasks, rulings
  guides/
    <topic>.md                     engineering policies: testing, security, deployment
```

## The three kinds of project doc

| Kind | Answers | Changes when | Never |
|---|---|---|---|
| Spec (`docs/specs/`) | What does the feature do now? | In the same commit as the behavior it describes | Describes behavior that has not shipped |
| Decision (`docs/decisions/`) | Why is it this way? | Written once when the decision is made; later only its status changes | Rewritten to reflect a new decision |
| Plan (`docs/plans/`) | How was this change designed and built? | Before any code, then rulings and status as the change runs | Kept current after the change merges; it is history |

Specs stay current, decisions stay true to their moment, plans stay attached to their change. Keeping the three apart is what lets an agent trust a spec as current behavior and a decision as the reason behind it.

## Naming

- Lowercase kebab-case everywhere.
- Specs: the feature's name, no date or number: `billing.md`, `csv-export.md`. A spec lives as long as its feature.
- Decisions: a four-digit sequence plus a short title in active voice: `0007-cap-free-tier-at-3-projects.md`. The next number is the highest on the base branch plus one. When several agents or branches run at once, also check open pull requests and renumber yours before merge if they collide.
- Plans: the date the change starts plus its topic: `2026-10-25-free-tier-cap.md`.
- Guides: the domain: `testing.md`, `security.md`. A domain with more than about 150 lines of real content becomes a folder with an `index.md`.
- Templates: `_template.md` in each folder.

## Format: Starlight-compatible Markdown

Write plain GitHub-flavored Markdown that Starlight can render unchanged, so adding a site later needs no rewrite:

- Frontmatter on every page under `docs/`: `title` (required; a Starlight build fails without it) and `description` (one line). The description doubles as the agent's relevance hint: an agent can read only the frontmatter of a folder to decide which file to open.
- No H1 in the body. Starlight renders `title` as the H1; start sections at `##`.
- Extra frontmatter keys (`status`, `date`, `decision-makers`, `supersedes`) are fine; Starlight ignores keys it does not know.
- Link other docs with relative paths to the `.md` file (`../decisions/0007-cap-free-tier-at-3-projects.md`). GitHub follows them as written; the Starlight recipe rewrites them to page URLs.
- No MDX components or Starlight `:::` asides; they show as raw text on GitHub. Mermaid blocks render on GitHub and show as code on the site unless a Mermaid integration is added.
- `CHANGELOG.md`, `AGENTS.md`, and `CLAUDE.md` live at the root, outside `docs/`, and need no frontmatter.

## Lifecycle rules

**Specs.** A new feature's spec arrives with the first commit that implements it. Each later behavior change edits the spec in the same commit. Planned behavior lives in the change's plan, as a spec delta (what will be added, modified, or removed), until the commit that ships it. `status: current` while the feature exists, `deprecated` when it is going away; delete the spec in the commit that removes the feature.

**Decisions.** Status moves `proposed` → `accepted` (or `rejected`). Until the pull request that adds a record merges, the record is part of that proposal and can be revised. Once merged, an accepted record is never edited except to change its status (or, format only, to add the frontmatter a docs site needs): to change course, write a new record with `supersedes: NNNN`, and set the old one to `status: superseded` with `superseded-by: NNNN`. Record who decided in `decision-makers`, by name (from the conversation, else `git config user.name`). An agent deciding on its own in an unattended run writes `agent (unattended run)`, and merging the pull request that adds the record ratifies it. The structure record agents-init writes is the exception: it names the person who asked for the setup, even in a headless run.

**Plans.** Written and committed before code, as the proposal the code commits implement. Frontmatter `status`: `draft` → `approved` (when a human approves it) → `in-progress` → `done` or `abandoned`; `size`: `trivial`, `bounded`, or `architectural`. Rulings and deferred items accumulate in the plan while the change runs. After merge the plan is history: do not update it to match later changes.

**Changelog.** Add the user-visible line under `## [Unreleased]` in the same commit as the change. When release tooling generates the changelog from Conventional Commits, the commit subject is the entry; do not edit the file by hand.

## Strong decisions: decision record or ruling

Write a decision record when a call is any of:

- Hard or costly to reverse: data model, storage, file or wire formats, migrations
- A new dependency, framework, service, or language, or replacing one
- A pattern other code will copy, or one that competes with an existing pattern
- A change to a public interface others depend on: API, CLI, URLs, events, config keys
- Security, privacy, auth, or compliance posture
- Business rules: pricing, plans, entitlements, limits, what each tier includes
- A departure: contradicting an accepted decision, or changing anything a spec states that the request did not ask to change (write the superseding record). Behavior a change sets out to alter goes through its plan's spec delta instead.

Everything else is a ruling: a one-line note in the plan's `## Rulings` section, `[scope] decision — why — cost if wrong: low|medium|high, what breaks`. Naming, internal structure, test layout, and library-internal choices are rulings. When unsure, ask "would someone reviewing this change want to second-guess it first?" If yes, it is a record.

## Atomic commits

One commit is one complete, reviewable change that leaves the repo consistent: the code, the tests that prove it, and every doc it makes true or stale (the spec section, a guide, the changelog line, the decision record for a strong call it embodies). No "docs later" commits, and no commit whose docs describe behavior it does not contain. The plan commit, made before any code, is the one docs-only commit a change starts with; decision records made while designing go in it. The only docs-after-code commit allowed is a fix-up for a gap found before the branch is pushed, named for the commit it completes (`docs(billing): complete 1a2b3c4`) and called out in the pull request.

Message: a Conventional Commits subject (`feat(billing): cap free plan at 3 projects`), then a body that says why and names the docs it touched, so `git log --grep 0007` finds every commit tied to a decision:

```
feat(billing): cap free plan at 3 projects

Support cost per free account rose past the plan's margin.

Spec: docs/specs/billing.md
Decision: docs/decisions/0007-cap-free-tier-at-3-projects.md
Plan: docs/plans/2026-10-25-free-tier-cap.md
```

## Product and pricing docs

`docs/product/vision.md` is one page: who it is for, the problem, what it is, what it is not, and how success is measured. The "what it is not" list is what stops scope creep.

`docs/product/pricing.md` exists only for commercial products. Give each fact one home: if the code holds a machine-readable catalog (`config/plans.yaml`, an entitlements module, the billing provider's product IDs), that catalog is the source of truth. The page names that file, and its tables are derived from it: generate them, or update them in the same commit as any catalog change; the code wins on disagreement. Keep three states apart: available in the product, included in a customer's plan, enabled for rollout. Every change to prices, plans, or limits gets a decision record.

## Customizing and existing structures

- Existing folders win: `docs/adr/` or `doc/architecture/decisions/` is the decisions folder, OpenSpec's `openspec/specs/` is the specs folder. Point the docs map at them instead of creating parallel folders.
- Existing records keep their format and their numbers. New records continue the sequence in the template's format, and the docs map notes the mix. A record that already adopted decision records (a classic "0001: Record architecture decisions") is built on, not superseded.
- An existing docs framework (Docusaurus, MkDocs, VitePress) stays as it is. When its source directory is the repo's `docs/`, put these folders inside it and follow its frontmatter rules. When it lives elsewhere (`website/docs/`), it holds user-facing docs; keep specs, decisions, and plans in the repo's `docs/` and do not move either.
- Folders left by older workflow runs (`docs/add/`, `docs/hdd/`, `docs/superpowers/`) stay where they are; list them in the docs map as history. New work goes to the resolved paths.
- Custom names only change the paths in the docs map. Keep the three kinds of doc and their rules.

## Why this shape

- Specs as current truth, changed with the code: spec-anchored development (Birgitta Böckeler, martinfowler.com) and OpenSpec's living specs with per-change deltas.
- Decision records: Michael Nygard's ADR format, MADR's frontmatter fields, Spotify's guidance on when to write one, and the supersede-don't-edit rule.
- Plans with goals, non-goals, appetite, and rejected alternatives: Google design docs and Basecamp's Shape Up.
- Atomic commits with code, tests, and docs together: Simon Willison's "The Perfect Commit".
- A short router plus on-demand docs, and specs written before code: Anthropic's Claude Code best practices.
- Keep a Changelog and Conventional Commits for release notes; Starlight for an optional rendered site.
