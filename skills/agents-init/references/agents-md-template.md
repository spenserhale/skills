# AGENTS.md template

Section-by-section structure for the router file. Shorter is better: a small project needs 60 lines, a large one rarely more than 200. Fill every bracket with real project content; placeholders get ignored, real commands get run. For each line, ask whether removing it would cause an agent to make a mistake; if not, cut it.

The `## Documentation` section is a contract: `doc-it`, `agentic-driven-development`, and `human-driven-development` read its table to find specs, decisions, and plans. Keep the heading, the columns, and the Kind labels of the standard rows, because other skills look rows up by them. Adapt the paths, drop rows or clauses that do not apply (no pricing page, no guides yet), and add rows for other doc homes, such as customer-facing docs in `website/docs/`.

The `## Coding standards` section goes into every `AGENTS.md` as written, Minimal included; the cut test above does not apply to it. When the repo already states a rule that contradicts one of the standards (in an existing `AGENTS.md`, `CONTRIBUTING.md`, or a style guide), the repo's rule wins: leave that standard out and name the conflict in the report.

```markdown
# AGENTS.md

## Purpose
[One paragraph: what this repo does and who it serves]

## Quick start
[The real commands an agent needs: install, test, build, and any docs-site commands; warn on any that cannot run as configured]

## Repo layout
[The directories that matter for coding: source, tests, config, docs]

## Documentation
Durable project knowledge lives in `docs/` as Markdown with `title` and `description` frontmatter and no body H1 (Starlight-compatible). Before changing a feature's behavior, read its spec and the decisions that touch it.

| Kind | Path | Rule |
|---|---|---|
| Specs: what each feature does now | `docs/specs/<feature>.md` | Change in the same commit as the behavior; never ahead of the code |
| Decisions: why | `docs/decisions/NNNN-<title>.md` | New record for every strong decision; supersede, never rewrite |
| Plans: one change, designed and tasked | `docs/plans/YYYY-MM-DD-<topic>.md` | Write and commit before the code |
| Product | `docs/product/vision.md`[, `docs/product/pricing.md`] | Read before scoping a change[; price or plan changes need a decision record] |
| Guides | `docs/guides/<topic>.md` | See Progressive disclosure |
| Changelog | `CHANGELOG.md` | Add an `## [Unreleased]` line in the same commit as any user-visible change |

Templates: `_template.md` in `docs/specs/`, `docs/decisions/`, and `docs/plans/`. A decision is strong when it is hard to reverse, adds a dependency or a pattern others will copy, changes a public interface or data model, touches security, privacy, or pricing, or departs from an accepted decision (or changes something a spec states that the change did not set out to change). Smaller calls go in the plan's `## Rulings`. Never deviate silently from a spec or an accepted decision: ask first; only when no human is in the loop, write the superseding record and call it out in the pull request.
[History: `docs/add/`, `docs/hdd/`, or other legacy folders, if any, with one line saying they are kept as history]

## Progressive disclosure
Before editing, check whether the task touches one of these areas and read the guide first (a TODO line is a guide not written yet):
- [Domain]: `docs/guides/[topic].md`
[One line per guide that exists after this run, then the TODO lines for guides not written yet:]
- TODO [Domain] (`docs/guides/[topic].md`): [what the guide will cover, and when to write it]

## Skills
Use `.agents/skills/` when the task matches a documented workflow:
- `.agents/skills/[name]/`: [one-line description]
[Only include this section if skills exist]

## Coding standards
1. **YAGNI**: Don't build it until you need it
2. **DRY**: Extract patterns after second duplication, not before
3. **Fail Fast**: Explicit errors beat silent failures
4. **Simple First**: Write the obvious solution, optimize only if needed
5. **Delete Aggressively**: Less code = fewer bugs
6. **Semantic Naming**: Always name variables, parameters, and API endpoints with verbose, self-documenting names that optimize for comprehension by both humans and LLMs, not brevity (e.g., `wait_until_obs_is_saved=true` vs `wait=true`)

## Commits
A change starts with its plan, committed before any code together with the decision records made while designing. After that, one commit is one complete change: the code, its tests, and every doc it changes (spec, guide, changelog line, decision record). Conventional Commits subject (`feat(scope): ...`); the body says why and names the docs it touched (`Spec:`, `Decision:`, `Plan:`).

## Done criteria
Before finishing any task:
- Run [real test command] and fix failures before declaring done
- Behavior changed: the spec, changelog, and any affected guide changed in the same commit
- A strong decision was made: its decision record exists
- If a check was skipped, say why; flag risky assumptions explicitly
```

## Variants

- **Minimal structure** (user chose AGENTS.md + CLAUDE.md only): keep Purpose, Quick start, Repo layout, Coding standards, Commits, and Done criteria; replace the Documentation table with one line naming where docs live today, if anywhere.
- **Starlight site**: add `cd site && npm run dev` and `cd site && npm run build` to Quick start with "`docs/` is the source; `site/` only renders it".
- **Generated changelog**: the Changelog row says "Generated from Conventional Commits by [tool]; do not edit by hand".
