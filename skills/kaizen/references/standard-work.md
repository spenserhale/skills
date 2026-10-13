# Standards and plan-do-check-act

A standard is the written, current best-known way to do a piece of work: the documented commands, the scripts, the lint and format config, the CI definition, the agent docs. Kaizen improves the standard, not the single instance. An improvement that is not written into a standard is gone by the next session, and for an agent this is literal: nothing carries over except what the repo says.

## Signals of a weak standard

| Signal | How to confirm |
|--------|----------------|
| The docs do not run | Execute each documented command exactly as written |
| Two ways to do one thing | README, task runner, and CI each name a different command for the same check |
| CI and local disagree | Different flags, versions, or steps between the pipeline and the documented local command |
| Setup lives in heads | A clean checkout cannot run the checks by following the docs alone |
| Agent docs absent or stale | `AGENTS.md` or `CLAUDE.md` missing, or naming files and commands that no longer exist |
| Standards without enforcement | A written rule that no check verifies |

## One improvement as plan-do-check-act

Run one improvement at a time, so its effect can be measured.

1. **Plan.** State the problem with its measurement ("the suite takes 6.1 s; 6.0 s is two tests that sleep"), the cause, the one change, and the result expected ("under 0.2 s, same tests passing").
2. **Do.** Make the smallest version of the change.
3. **Check.** Measure again with the same command and compare against the expectation, not against a feeling.
4. **Act.** If it held, update the standard so the new way is the default. If it did not, revert it and record what was learned; a failed experiment that is written down is not waste.

## Where an improvement gets recorded

Prefer the strongest form that fits, and the narrowest scope that covers it.

1. **A check** that fails when the standard is broken: a test, a lint rule, a CI gate.
2. **A script or task** that makes the right way the easy way: one command instead of three remembered ones.
3. **A line of documentation** in a file that is already read on that path. Weakest, and always-loaded files cost every session, so add there last.

Correct a stale statement at its source, in every copy. A new note that says "ignore the old instructions" leaves two documents disagreeing.

## Keeping the workplace in order (5S)

- **Sort:** remove what is not used: dead code, unused dependencies, stale branches.
- **Set in order:** things live where the standard says, so they are found without searching.
- **Shine:** clean as part of the work: debug prints, temp files, and scratch scripts go before the change is called done.
- **Standardize:** write the above down as checks where possible.
- **Sustain:** the checks run on every change, so order does not depend on memory.

## Pitfalls

- **No standard, no improvement.** Without a baseline there is nothing to compare against, and each person's change overwrites the last.
- **A standard is the current best, not a rule forever.** One that cannot be changed stops being followed.
- **Standardize after the work is stable.** Automating or documenting a process that is still wasteful fixes the waste in place.
