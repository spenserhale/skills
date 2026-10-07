# GitHub Ref Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use add-subagent-driven-development (recommended) or add-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Publish an installable GitHub reference caching skill.

**Architecture:** One instruction-only workflow skill with four scenario evals; README registers it as a user skill. OS paths, concurrency, freshness, and preservation rules live in SKILL.md.

**Tech Stack:** Markdown, JSON, Git, existing Python skill validator.

## Task 1: Author and register

- [x] Create `skills/github-ref/SKILL.md` with the design's cache roots, owner/repo normalization, clone/update/read lock lifetime, clean default-branch fast-forward policy, separate worktrees for requested refs, and failure reporting.
- [x] Create `skills/github-ref/evals/evals.json` with new-clone, Windows-refresh, dirty-cache/explicit-ref comparison, and tag/refspec freshness prompts and measurable expectations.
- [x] Add the README user-skill row and `--skill github-ref` to the global install command.

## Task 2: Verify and publish

- [x] Run `python3 skills/sh-skill-creator/scripts/validate_skill.py skills/github-ref --strict`; expect zero errors.
- [x] Run fresh-agent scenarios with and without the skill. Record failures and improvements in the spec; scope these as instruction-following tests, not executed OS/Git integration tests.
- [x] Review spec compliance and instruction clarity. Run `git diff --check`; expect no output.
- [x] Commit only task files, push main, verify remote commit and `npx skills add spenserhale/skills --list` discovers github-ref.

## Assumptions & Decisions

Carry forward the design's decisions. Keep this documentation change free of helper scripts; examples supplement ordered instructions. Use fresh-agent dry runs and mechanical validation rather than a large statistical benchmark or browser viewer, because no new executable implementation is being shipped.
