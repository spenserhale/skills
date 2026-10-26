# Guides (policy docs)

Per-file template, the catalog of common domains, and the folder layout for large domains. Create only what is relevant to this project; a file with nothing real to say is worse than a TODO line in `AGENTS.md`.

## File template

Each guide lives at `docs/guides/<topic>.md` (or inside the existing docs framework's source directory, per `project-structure.md`):

```markdown
---
title: [Domain title]
description: [One line: which tasks should read this guide.]
---

## Purpose
Read this guide when [the task context that makes it relevant].

## Policy
[Actionable, project-specific rules, as bullets]

## Implementation notes
[Conventions, gotchas, and known patterns not obvious from reading the code]

## Related docs
- [Relative links to specs, decisions, or other guides that intersect]
```

The `description` line is what an agent reads to decide whether to open the file, so name the triggering tasks, not the topic in general.

## Common domains

| Domain | File | When relevant |
|---|---|---|
| Error handling | `error-handling.md` | Any backend or service project |
| Security | `security.md` | Auth, user data, APIs, financial data |
| Database | `database.md` | Projects with schema or query concerns |
| Logging | `logging.md` | Backend services with observability needs |
| Testing | `testing.md` | Projects with meaningful test conventions |
| Deployment / CI | `deployment.md` | Non-trivial deploy or branch rules |
| API conventions | `api.md` | REST or GraphQL APIs with versioning or auth patterns |
| Integration-specific | `sentry.md`, `hubspot.md`, ... | Discovered during the survey |

A guide states how to work in the codebase. What a feature does belongs in its spec, and why a choice was made belongs in a decision record; link to them instead of restating them.

## Large domains: use a folder

For domains with more than about 150 lines of real content, split into a folder:

```
docs/guides/sentry/
  index.md          summary, and when to use the skill
  cli.md            tool usage
  issue-triage.md   step-by-step diagnosis
```

Point `AGENTS.md` only to the `index.md`.
