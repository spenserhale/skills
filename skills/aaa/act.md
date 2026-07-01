# Act

**Goal:** do the work. You've arranged the context and have a plan — now execute it.

## Do it inline

These are small, one-shot tasks, so **act directly — don't dispatch a subagent.** Make the edit, run the command, fetch the data, write the file. The overhead of delegating and reviewing a subagent isn't worth it at this size; that's what the heavier workflows are for. Here, you are the one doing it.

## Stay on the plan

Act on the plan you formed in Arrange — nothing more:

- **Do the smallest thing that accomplishes the task.** No "while I'm here" refactors, no speculative extras, no gold-plating. YAGNI.
- **One coherent change.** If you discover mid-Act that the plan was wrong or the task is bigger than it looked, stop and go back to Arrange rather than improvising a larger change.
- **Match the surroundings.** In code, follow the existing patterns, naming, and style. In any output, follow the conventions of where it's going.

## If the task is test-driven

If the project uses TDD and you're writing code, the test comes *first*: write the failing test, watch it fail for the right reason, then write the minimal code to pass. In that case the "prove it" part of Assert is already half-done — but you still verify in Assert with a fresh run.

## Don't declare victory here

Finishing the edit is not finishing the task. Resist the urge to say "done" or "that should do it" the moment the change is written. Making the change and *proving it worked* are two different steps — proving it is next.

→ Next: **Assert** (`assert.md`).
