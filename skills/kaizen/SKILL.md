---
name: kaizen
description: "Kaizen quality-first working mode and development-process audit, after the Toyota Production System. Use when the user runs /kaizen, says \"kaizen\", \"quality first\", \"stop the line\", \"fix it before moving on\", or \"clean as you go\", or wants failing tests, warnings, and deprecation notices dealt with instead of left behind while work continues, even if they only complain that loose ends keep piling up. Also use for /kaizen audit, or when asked where a repo's development process wastes time or hides problems. Not for reviewing a diff for bugs; use a code review skill. Not for a retro on the thread; use reflect."
argument-hint: "[on | off | audit [path]]"
---

# Kaizen (`/kaizen`)

Build quality in at the step that produces it. An abnormality is cheapest to handle the moment it appears, and every step built on top of it raises the price. So noticing is mandatory, while fixing is triaged: repairing everything in sight is overproduction, the waste this mode exists to prevent.

- `/kaizen` or `/kaizen on`: work in the mode below for the rest of the session.
- `/kaizen off`: stop.
- `/kaizen audit [path]`: audit a repo's development process instead. Read `references/audit.md` and follow it. The audit changes no files, so the mode below does not apply to it.

## The mode

### 1. Detect

Read the full output of every command, not only its exit code or last line. An abnormality is anything a healthy run would not print or do:

- a failing or erroring test, build, lint, or type check
- a warning or deprecation notice
- a non-zero exit hidden by a pipe, `|| true`, or a retry
- a skipped or disabled test, or a check that passed only on a second run
- anything worked around to keep going: a documented command that does not run, a broken script

Before the first edit, run the project's checks and keep the result as the baseline. Run the same checks again before calling the work done. Whatever is abnormal now and was not in the baseline is yours. When the full set is too slow to run twice, use the widest set that is affordable and say which.

### 2. Triage

| The abnormality is | Do |
|--------------------|-----|
| Introduced by you this session | Fix it before any other step. |
| Already there, small, and in the path of the task | Fix it, and say so in the report. |
| Already there, and large or outside the task | Leave the code alone. Record the evidence and report it. |

- **In the path** means the function or block the task already changes, or a command the task needs in order to be verified.
- **Small** means a few lines, no decision about intended behavior, and verifiable by the checks already being run.
- **Unknown origin counts as yours** until the baseline or the history shows otherwise.
- **The first row has no exceptions.** A failure your change caused stays yours when the test looks unrelated, flaky, or wrong. Fix the cause. Skipping the test, loosening the assertion, deleting it, silencing the warning, or re-running until it passes turns the signal off and leaves the defect in. When a test is wrong because the requested behavior changed, change the test and say so in the report.
- **Only the user can waive a row**, by saying so. A waived item still goes in the report as open.

### 3. Countermeasure

A fix removes one instance. When a defect got further than it should have (no check caught it, or it was found by luck), ask what would have caught it sooner and add the smallest such check that fits in the task: a test that fails on the bad case, an assertion, a type. Then search for the same pattern elsewhere; hits outside the path go in the report, unfixed.

A countermeasure that reaches outside the task (CI config, shared lint rules, docs) is a proposal in the report, not an edit.

### 4. Check the diff for waste

Before ending a turn, compare the diff with the request:

- Everything in it was asked for: no extra option, parameter, config, abstraction, or cleanup of code the task did not need to touch.
- Nothing is half done: no TODO stub, commented-out code, unused helper, debug print, or temp file. Finish it or remove it.
- One change is finished and verified before the next one starts, so a failure can be assigned to its cause.

### 5. Report

End the turn's final message with this section whenever something was fixed in passing or is still open. With nothing to report, leave the section out: a signal that is always on stops being read.

```markdown
## Kaizen

**Fixed in passing**
- <what>, <file:line>: <how it was confirmed gone>

**Open**
- <what>: `<command>` printed `<shortest decisive line>` (<file:line>). Not fixed because <outside the task | needs a decision: which one>. Next step: <the smallest one>.

**Proposed countermeasure**
- <the check that would stop a recurrence, and where it would live>
```

- Every open item carries its evidence: the command, the quoted line, the location. An item without evidence is an impression; leave it out.
- One line per cause. The same warning from forty call sites is one item with a count.
- Report an item in the turn it is found. When the task wraps up (final summary, before a commit or pull request), list everything still open from the session once more, so that nothing found early is lost.
- In an unattended run where nobody reads the turns, also record open items wherever that workflow keeps deferred work.

## Thoughts that mean stop

| Thought | What is true |
|---------|--------------|
| "The suite was already red, so this failure is not mine" | A red suite hides new failures. Compare with the baseline test by test. |
| "The tests for my change pass" | A change can break a check outside the files it touched. Run the same set as the baseline. |
| "It is only a warning" | A deprecation notice is a failure with a date on it. Triage it like one. |
| "It is one line; I will ask before fixing it" | Small and in the path is already decided: fix it and report it. Asking spends the user's attention on a decision the policy has made. |
| "While I am here I will clean up the rest" | Outside the path goes in the report. The user did not ask for that diff and would have to review it. |
| "It passed on the second run" | Then it is flaky, and flaky is a finding. |
| "The user is in a hurry" | The report is a few lines. A defect of yours passed downstream costs them more later than the fix costs now. |

## Gotchas

- **Filtered output hides the signal.** Quiet flags, `| tail`, `2>/dev/null`, and token-saving output wrappers drop warnings first. When output looks summarized or too clean, rerun the check once unfiltered.
- **An abnormality is something a run or a tool reported.** Style preferences and "I would have written this differently" are not findings.
- **The mode never widens the task.** When an in-path fix starts to grow (more files, a behavior question), back that part out and move it to Open.
- **A large pile of old warnings is one open item**, with a count and a proposal to cap it (fail when the count rises), not a cleanup inside an unrelated task.
- **No baseline is possible** when the checks cannot run before the first edit (missing dependencies, broken setup). That is the first abnormality: report it, and use version control to separate old from new.

## References and hand-offs

| Read when | File |
|-----------|------|
| Invoked with `audit` | `references/audit.md` |
| Choosing a countermeasure; findings about gates that cannot fail, flaky or skipped tests, warnings let through (stop and fix) | `references/jidoka.md` |
| Findings about slow feedback, batch size, or work in progress (flow) | `references/flow.md` |
| Naming or measuring a kind of waste, unevenness, or overburden (waste) | `references/waste.md` |
| Docs, scripts, or CI disagree with reality; running one improvement as plan-do-check-act (standards) | `references/standard-work.md` |

- When the cause of a failure is not obvious, use the project's debugging skill before fixing.
- To judge the code that was written, use a code review skill. For lessons from the thread itself, use `reflect`.
