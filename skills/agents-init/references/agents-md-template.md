# AGENTS.md template

Section-by-section structure for the router file. Target 150–250 lines; shorter is better if the project is small. Fill every bracket with real project content — placeholders get ignored, real commands get run.

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
