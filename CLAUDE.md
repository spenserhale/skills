# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of Claude Code agent skills (SKILL.md files) for CLI tools and workflows. Each skill lives in `skills/<skill-name>/SKILL.md` and teaches Claude how to work with a specific CLI tool. This is not a traditional software project — there is no build system, no tests, and no application code.

## Repository Structure

```
skills/
  <skill-name>/
    SKILL.md          # required: YAML frontmatter + lean markdown body
    references/       # optional: docs the agent reads on demand, one level deep
    scripts/          # optional: deterministic tools the agent executes
    assets/           # optional: templates copied into output
    evals/evals.json  # test prompts + expectations
    agents/openai.yaml  # optional: Codex display metadata
```

The house standard for structure, descriptions, body rules, testing, and auditing lives in the `sh-skill-creator` skill (`skills/sh-skill-creator/`). Use it when creating or changing any skill here.

## Skill File Format

```markdown
---
name: <skill-name>            # equals the folder name
description: <what it does>. Use when <concrete triggers, phrases, file types>. Not for <near-miss>; use <sibling> instead.
---

# Title

<one or two sentences framing the core idea>

## <Rules or Steps>
<the guidance that changes decisions; reasons over shouting>

## Gotchas
<failure points found by iterating; highest-signal section>

## Resources / hand-offs
<"Read references/x.md when ..."; "Run scripts/y.py ..."; sibling skills by name>
```

The description carries all triggering: it is the only text loaded before the agent decides. A body "When to use" section is only for scope boundaries and hand-offs. Keep the body under 150 lines (hard cap 500) and move depth to `references/`.

## Adding a New Skill

1. Scaffold: `python3 skills/sh-skill-creator/scripts/init_skill.py <skill-name> --path skills [--resources scripts,references]`
2. Write the description first, then the body, per the `sh-skill-creator` rules
3. Validate: `python3 skills/sh-skill-creator/scripts/validate_skill.py skills/<skill-name>` (zero errors before committing)
4. Add three evals to `evals/evals.json` and test on a fresh agent with and without the skill
5. Add an entry to `readme.md`, in the table that matches the skill's scope:
   - **User skills** — agnostic, useful across projects (install once to the user profile). Also add the skill name to the `--skill` list in the "Install / update all user skills" command block.
   - **WordPress project skills** — WordPress-specific (installed per project). Also add the skill name to the `--skill` list in the "Install all WordPress skills" command block.
   - **Project skills** — tied to some other specific framework or task (installed per project).

## Conventions

- Skill names use lowercase kebab-case (e.g., `wordpress-cli`, `1password-cli`)
- Skills emphasize "start with help" patterns — teaching the agent to use built-in `--help` before guessing at flags
- Activation triggers live in the frontmatter description, not in a body section
- Skills speak in abstract verbs for anything that varies per repo (tracker, labels, doc locations) and read the specifics from the repo's `CLAUDE.md`/`AGENTS.md` at run time
- Skills provide practical command examples rather than exhaustive API references
