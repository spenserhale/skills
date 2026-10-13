# Flow (just-in-time)

Just-in-time is the other half of the Toyota Production System: make only what is needed, when it is needed, in the amount needed. Work is pulled by a real request rather than pushed ahead on a guess, and it moves in small batches so that a problem surfaces after one item instead of after fifty.

In software the batch is the change, and the pace is set by the feedback loop: how long from an edit to knowing whether it works.

## Signals

| Signal | How to measure |
|--------|----------------|
| Slow feedback | Wall time of the check a developer runs on every change; time to the first failure when something is broken |
| One item dominates | The runner's per-test or per-step timing: the slowest items and their share of the total |
| Real waiting in tests | Sleeps, network calls, and real clocks inside unit tests |
| No focused check | The only documented command runs everything; there is no way to run just the area being changed |
| Large batches | Lines and files changed per commit or pull request over recent history |
| Work in progress piling up | Unmerged branches and their age; open pull requests and their age |
| Slow or serial CI | Total pipeline time; steps that could run in parallel but do not |
| Late checks | A check that runs only in CI and could run locally in seconds |

## Improvements, smallest first

- **Remove real waiting.** Inject the clock, the sleep, or the transport so tests do not wait in real time. This is usually the largest single saving for the least change.
- **Give the common case a fast path.** A documented focused command (one file, one package) beside the full one.
- **Fail fast.** Run the quick checks before the slow ones; stop on first failure in the local loop.
- **Split by speed.** Keep slow integration tests in their own target so the fast suite stays fast enough to run on every change.
- **Parallelize** only after the above; it hides waste rather than removing it.

## In a working session

- **Pull, do not push.** Build what the request asks for. An option, parameter, or abstraction added for a future need is inventory: it must be read, tested, and maintained before anyone has asked for it.
- **One piece at a time.** Finish and verify one change before starting the next. Two half-done changes cannot be verified separately, and a failure cannot be assigned to either.
- **Small batches.** A change that can be checked in seconds gets checked. One that takes minutes gets checked at the end, when the cause of a failure is hardest to find.

## Pitfalls

- **Speed bought by turning checks off is not flow.** A suite made fast by skipping tests has moved the cost downstream.
- **Measure before and after with the same command.** A timing claim without both numbers is a guess.
- **Level the load.** Steady small changes are easier to review and revert than rare large ones, even when the total is the same.
