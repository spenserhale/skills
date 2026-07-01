---
name: repo-explorer
description: Clone and inspect external repositories in a reusable local exploration cache. Use this skill when the user asks to explore, inspect, investigate, compare, or answer questions about a repository that may not already be in the current workspace.
allowed-tools: Bash(mkdir -p ~/.explore/repos) Bash(ls -la ~/.explore/repos) Bash(git clone *) Bash(ln -s *) Bash(readlink *)
---

Use this skill to explore repositories without cluttering the active workspace.

## Repository Cache

Use `~/.explore/repos` as the local cache directory for repositories being explored.

## Current Cache Contents

```!
mkdir -p ~/.explore/repos
ls -la ~/.explore/repos
```

## Flow

1. List the current repository cache contents before deciding what to use.
   - In hosts that support skill shell injection, use the rendered `Current Cache Contents`
     section above.
   - Otherwise, run `ls -la ~/.explore/repos` before deciding what to use.

2. Check whether the target repository is already present in `~/.explore/repos`.
   - Prefer a stable directory name based on the repository owner and name, such as
     `owner__repo`.
   - If the repository is already present, use that local checkout for exploration.

3. If the repository is not present, clone it into `~/.explore/repos`, then explore it there.
   - Create `~/.explore/repos` first if it does not exist.
   - Clone with a clear destination path, for example:

```bash
mkdir -p ~/.explore/repos
git clone <repo-url> ~/.explore/repos/<owner>__<repo>
```

## Local Reference Repos (`/refs`)

Some projects vendor a local, gitignored `refs/` folder that holds reference checkouts of
example repositories. When present, expose these to the exploration cache so the IDE and
other tools can resolve references to them too.

1. Check whether the current project has a gitignored `refs/` folder containing an
   `example-repo` checkout:

```bash
[ -d refs/example-repo ] && git check-ignore -q refs && echo "refs/example-repo present and ignored"
```

2. If `refs/example-repo` exists, symlink it into the exploration cache under the stable
   name `source` so it appears alongside cloned repos in `~/.explore/repos`:

```bash
mkdir -p ~/.explore/repos
ln -sfn "$(cd refs/example-repo && pwd)" ~/.explore/repos/source
```

   - Use `ln -sfn` so re-running the skill safely re-points an existing `source` link
     rather than nesting a link inside a stale directory.
   - Use an absolute path (`$(cd ... && pwd)`) so the link resolves regardless of the
     caller's working directory.

3. Verify and then explore `~/.explore/repos/source` like any other cached repo:

```bash
readlink ~/.explore/repos/source
ls -la ~/.explore/repos/source
```

After opening the repository, inspect its local instructions and project metadata before
making assumptions. Prefer `rg`, `rg --files`, and targeted file reads for exploration.
