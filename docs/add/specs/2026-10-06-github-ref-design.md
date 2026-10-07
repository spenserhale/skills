# GitHub Reference Cache

Create a model-invoked workflow skill for inspecting GitHub projects through a machine-wide, per-user cache. Use `~/.github-refs/<owner>/<repo>` on macOS/Linux and `%LOCALAPPDATA%/github-refs/<owner>/<repo>` on Windows, falling back to `%USERPROFILE%/.github-refs` if LOCALAPPDATA is unavailable.

Clone absent repositories; validate existing repositories and refresh their default branch before reading. Serialize clone, update, and reading with an atomic directory lock outside each checkout, because threads share mutable files. Preserve local edits and fail visibly on failed updates. Use separate Git worktrees for explicit refs rather than switching the shared checkout.

## Assumptions & Decisions

- The request's initial “git checkout” means `git clone`; checkout requires an existing repository.
- Prefer a concise instruction-only skill over a platform-specific shell script or a Python cache manager: Git and each host's shell already supply the required operations, without adding a runtime dependency.
- Use the user's proposed Unix folder. Windows LOCALAPPDATA fits reusable local downloads and avoids roaming a repository cache.
- Keep cached checkouts read-only to consumers; use a lock through reads to prevent another cooperating thread changing files mid-inspection.
- Stop on dirty, divergent, mismatched, or unrefreshable caches. Do not reset, stash, delete, or silently read stale data.
- Publish directly to the existing skills repository's default branch as requested. Preserve unrelated untracked files.

## Verification

Validate frontmatter and house rules; run fresh-agent reference scenarios with and without the skill. Check install discovery and verify the published commit on GitHub.

## Verification results

- Strict skill validator: zero errors, warnings, or informational findings.
- Fresh-agent baseline used different cache paths; with-skill plans followed the requested cache roots, refresh policy, preservation rules, and three reference scenarios. Four trigger boundary cases matched the intended scope.
- Review identified case-sensitive identity, stale moved/deleted tags, and narrowed fetch refspecs. Revisions lowercase GitHub identity, explicitly fetch all remote heads, and fetch requested tags into unique task-owned refs. A fourth eval covers these cases.
- Independent quality reviewer reproduced branch and tag freshness using local Git repositories and approved the revised instructions.
- Authoring-session Unix smoke test executed the published Bash example in a temporary cache against octocat/hello-world: initial clone and existing-checkout refresh succeeded; dirty-cache inspection failed while preserving the untracked note; all three runs released their locks.
- Windows behavior was evaluated as instruction-following plans; no native Windows execution was available. Statistical triggering benchmarks and browser review were omitted for this focused instruction-only change.
