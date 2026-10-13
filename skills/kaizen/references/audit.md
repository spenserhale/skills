# Process audit (`/kaizen audit [path]`)

An audit of how work gets done in a repo: its checks, its feedback loop, its signals, and its written standards. The subject is the process, so that the next change is cheaper and safer. Whether the code is correct is a code review's job. Every finding carries a measurement or a quoted line; a finding without one is an opinion, so drop it.

The audit is read-only. It changes no file in the repo, not even a one-line fix, because the measurements taken here are the "before" that the first improvement is checked against.

## Steps

1. **Find the stated standard.** Read the repo's agent docs (`AGENTS.md`, `CLAUDE.md`), README, contributing guide, task runner or package manifest, and CI config. List each check the project claims to run (build, test, lint, type check, format), its documented command, and where CI runs it. Done when the list covers every check, including ones documented but not wired and ones wired but not documented.

2. **Go and see.** Run each check locally, exactly as documented, and read its full output: no quiet flag, no `tail`, no output-compressing wrapper. Record exit code, wall time, failures, skips, and warnings grouped by cause with a count. A documented command that does not run is a finding; find the command that works and carry on. Run only checks that are safe locally: nothing that deploys, publishes, migrates, or writes outside the repo. If dependencies are missing, say so and ask before installing. Done when every check has a measured row or a stated reason it could not run.

3. **Find where the time goes.** For any check slow enough that someone would avoid running it on every change, use the tool's own timing report to name the slowest items and the share of the total they account for. Done when each slow check has its top cost named.

4. **Compare CI with local.** For each check: does CI run the same command, and can a failure there stop a merge? Look for swallowed exit codes (`|| true`, `continue-on-error`, `set +e`), checks that exist locally but not in CI, and warnings allowed through. Done when each check is marked "gates", "runs but cannot fail", or "absent".

5. **Count the standing inventory.** Cheap searches, counts only: TODO/FIXME/HACK markers, skipped or disabled tests, and suppressions (`noqa`, `eslint-disable`, `@ts-ignore`, `-W ignore`, and the like). Where git history exists, add long-lived unmerged branches and the size of recent changes. Done when each has a number.

6. **Classify, then read up.** Put each finding under one of the four headings in SKILL.md's reference table (stop and fix, flow, waste, standards). Read a tenet's reference only when that heading has findings.

7. **Rank.** Order by what every future change pays: how often the cost recurs times what each occurrence costs. A gate that cannot fail outranks everything it would have caught. After that, feedback time and signal noise usually outrank standing inventory, because every change pays them and inventory is paid once.

8. **Report and stop.** Use the format below. Recommend one improvement to do first and wait for the user to choose. Several improvements made together cannot be measured separately, and a long action list is itself inventory that nobody works off.

## Report format

Sensible default; adjust to the repo.

```markdown
## Kaizen audit: <repo>

**Measured**
| Check | Command | Result | Time | Warnings | In CI |
|-------|---------|--------|------|----------|-------|
| tests | `<command>` | 9 run, 1 failed, 2 skipped | 6.1 s | 2 causes | runs, cannot fail |

**Findings** (ranked, at most five)
1. **<finding>** (<heading>)
   - Evidence: `<command or file:line>` and the shortest decisive line or number
   - Cost: <who pays it, and how often>

**Do first**
- Change: <one change>
- Check: <the metric, its value now, the value expected after>
- Standard: <the doc, script, or config that will record the new way>

**Later**
- <each remaining finding, one line>

**Left alone**
- <what already works and should not be touched>
```

## Gotchas

- **A missing practice is not a finding.** "No linter", "no type checker", "no coverage" are absences. Report one only when a measured problem in this repo points at it.
- **One cause, one finding.** The same warning printed 300 times is one finding with a count and one quoted line.
- **Cold runs lie.** When the first run includes a dependency download or an empty cache, time a second run and report that one.
- **Say what could not be seen.** No CI config, no git history, a check that needs credentials: state it in the Measured table instead of leaving the row out.
- **A healthy repo has little to find.** "Nothing worth changing" with the measurements that show it is a complete result. Do not pad the list to fill the headings.
- **Stay off the code.** A bug noticed while reading is worth one line under Later. A list of bugs or style notes means the audit has turned into a code review.
