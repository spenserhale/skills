# Assert

**Goal:** prove the action actually worked, with real evidence — then close the loop or reopen it.

**The iron rule:** if you haven't run the validation *in this turn*, you can't claim it passed. "Should work," "looks right," and "I made the change" are not evidence. Run the check, read the output, then state the result.

## Pick the validation that fits the task

There's no single way to assert — choose what genuinely proves *this* task is done:

- **Code with a test framework** → run the tests. If the project is test-driven, this is the red→green confirmation. Run the full relevant suite, not a partial check; read exit code and failure count.
- **Code with no test framework, or when you want to be extra cautious** → do a **dry run**: execute the code path, run the CLI with `--dry-run`/`--help`, lint/build, or exercise the function on a sample input. Prove it runs and produces what you expect before calling it done.
- **A UI or other non-destructive change** → drive it. Use Playwright or the Chrome browser tools to load the page and confirm the change actually took — the element renders, the interaction works, the state updates.
- **Gathering / transforming data** → validate the data. Is it the right shape, count, and source? Spot-check values against the authoritative source. Confirm you got what was asked, not something plausible-looking.
- **An external or side-effecting action** → confirm the effect landed (the file exists with the right contents, the record was created, the request returned success).

When in doubt, prefer more validation. The whole value of this loop is the assurance that you got it right.

## Read the evidence honestly

- Report what the output *actually* says, including partial success or new warnings.
- Don't trust "it ran without error" as "it did the right thing" — check that the *result* is correct, not just that nothing crashed.
- If you can't validate something, say so plainly rather than implying success.

## Close the loop — or reopen it

- **Assert passed** → the task is done. State the claim *with* its evidence ("Tests pass: 12/12" / "Page renders the new banner, confirmed in browser" / "Fetched 340 records, spot-checked 5 against the source"). Done.
- **Assert failed** → **go back to Arrange, not straight back to Act.** The failure is new context. Ask *why* it failed and what you now understand that you didn't before — read the actual error, the wrong data, the broken test. Then Act to fix the real cause, and Assert again.

Keep looping — Arrange → Act → Assert — until Assert genuinely passes. Each loop should be smarter than the last because you're feeding real failure evidence back in. If you've looped several times and each fix reveals a new problem, stop and reconsider whether the approach (or the plan from Arrange) is fundamentally right — and pull the user in.

→ Loops back to: **Arrange** (`arrange.md`) on failure. Otherwise: done.
