# Stop and fix (jidoka)

Jidoka is the half of the Toyota Production System that builds quality in: the process detects an abnormality, stops, fixes it, and then changes itself so the same abnormality cannot recur. The last step is the one usually skipped, and without it the same defect comes back.

The andon is the signal half of this: a light that turns on only when something is abnormal. Pulling the cord calls for help; the line stops only when the problem cannot be handled within the current step. That is why the mode separates noticing (always) from fixing (triaged).

## Signals that a process cannot stop itself

| Signal | How to confirm |
|--------|----------------|
| A gate that cannot fail | The CI step swallows the exit code (`\|\| true`, `continue-on-error`, `set +e`), or the check is not required to merge |
| Red is normal | The suite fails on a clean checkout of the main branch |
| Flaky tests | A check passes on re-run with no change; retries configured in the runner or CI |
| Tests switched off | Skip or disable markers, especially with reasons like "fix later" and no linked issue |
| Warnings let through | Count per run; a warnings-as-errors setting that is off or absent |
| The signal is filtered | Quiet flags, redirected stderr, or wrappers that summarize output in the documented commands |
| Suppressions | Inline ignores (`noqa`, `eslint-disable`, `@ts-ignore`) and their trend over time |

## Choosing a countermeasure

Pick the highest rung that fits inside the task. Lower rungs depend on someone noticing.

1. **Make the mistake impossible.** A type, a schema, a required argument, an API that cannot be called wrongly.
2. **Make it fail immediately.** A test that fails on the bad case, an assertion, a lint rule set to error, warnings treated as errors in the test run.
3. **Make it fail before merge.** The same check wired into CI as a required gate.
4. **Make it visible.** A warning, a log line, a line in the docs the agent reads. Weakest: it works only when read.

A countermeasure targets the cause of the escape, not the instance. Ask "what let this get this far?" rather than "how do I fix this one?". The answer is often a missing or disabled check rather than the code.

After a fix, look sideways for the same pattern elsewhere in the repo. Each hit is the same defect waiting.

## A pile of existing warnings

Fixing hundreds of pre-existing warnings inside an unrelated task is overproduction. Propose a ratchet instead: record the current count, fail the check when the count rises, and lower the number as warnings are fixed in the path of normal work. New ones are stopped at once; old ones drain without a cleanup project.

## Pitfalls

- **Silencing is not fixing.** Suppressing a warning, skipping a test, or retrying until green turns the light off and leaves the fault in place. A suppression is acceptable only with a reason and an owner written next to it.
- **A quarantined test with no owner is a deleted test.** It still counts as coverage in people's heads.
- **Stopping for everything stops nothing.** When every notice is reported with equal weight, the report gets skimmed. Group by cause and rank.
- **Fix the cause where the cause is.** A failing test caused by a wrong fixture is not fixed by changing the assertion.
