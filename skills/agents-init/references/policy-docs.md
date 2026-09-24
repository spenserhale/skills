# Policy docs

Per-file template, the catalog of common domains, and the folder layout for large domains. Create only what's relevant to this project; a file with nothing real to say is worse than a TODO in AGENTS.md.

## File template

Structure each `docs/<topic>.md` (or wherever the docs path resolved to in Step 2):

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

## Common domains

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

## Large domains: use a folder

For domains with more than ~150 lines of real content, split into a folder:

```
docs/sentry/
  index.md          # summary + when to use the skill
  cli.md            # tool usage
  issue-triage.md   # step-by-step diagnosis
```

Point AGENTS.md only to the `index.md`.
