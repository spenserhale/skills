# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of Claude Code agent skills (SKILL.md files) for CLI tools and workflows. Each skill lives in `skills/<skill-name>/SKILL.md` and teaches Claude how to work with a specific CLI tool. This is not a traditional software project — there is no build system, no tests, and no application code.

## Repository Structure

```
skills/
  <skill-name>/
    SKILL.md          # The skill definition (YAML frontmatter + markdown body)
```

## Skill File Format

Each SKILL.md follows this structure:

```markdown
---
name: <skill-name>
description: <one-line description used for skill activation>
---

# Title

## When to use
<triggers for when the skill should activate>

## Content
<reference material, commands, examples, patterns>
```

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with the frontmatter and sections above
2. Add an entry to `readme.md`, in the table that matches the skill's scope:
   - **User skills** — agnostic, useful across projects (install once to the user profile). Also add the skill name to the `--skill` list in the "Install / update all user skills" command block.
   - **WordPress project skills** — WordPress-specific (installed per project). Also add the skill name to the `--skill` list in the "Install all WordPress skills" command block.
   - **Project skills** — tied to some other specific framework or task (installed per project).

## Conventions

- Skill names use lowercase kebab-case (e.g., `wordpress-cli`, `1password-cli`)
- Skills emphasize "start with help" patterns — teaching the agent to use built-in `--help` before guessing at flags
- Skills include a "When to use" section listing activation triggers
- Skills provide practical command examples rather than exhaustive API references
