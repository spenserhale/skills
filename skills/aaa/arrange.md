# Arrange

**Goal:** get the right context so the task can actually succeed, then form a short plan. Most task failures are context failures — you acted before you understood. Arrange is where you prevent that.

## Get the right context

Ask: *what would someone need to know to do this correctly?* Then go get it. What "context" means depends on the task:

- **Fixing a bug** → Do you have a *diagnosis of the cause*, not just the symptom? Reproduce it, read the error and stack trace, find where the bad value originates. Don't propose a fix before you understand why it's broken.
- **Implementing a ticket** → Do you have the ticket's actual context — acceptance criteria, linked discussion, affected files? Read it, don't assume from the title.
- **Using a new library** → Do you have the library's docs for *how to use it*? Pull the relevant usage, version, and API surface before writing against it. Don't guess the API.
- **Gathering / fetching information** → Do you know the authoritative source, the exact thing being asked for, and what "correct" looks like? Know where the answer lives before you go get it.
- **Working in existing code** → Read the surrounding code and follow its patterns. Understand the current structure before changing it.

The recurring theme: **read before you write, understand before you act.**

## Prompt the user when only a human can decide

If there's ambiguity that context-gathering alone can't resolve — a genuine fork in intent, a missing credential, a destructive choice, conflicting requirements — **stop and ask**. Prefer one focused question (multiple-choice when you can). Don't burn effort perfecting a task built on a guessed assumption.

Don't ask what you can find yourself. Ask only what you genuinely can't determine from the code, the docs, or sensible defaults.

## Form a short plan

Once you have the context, state the plan in a sentence or a few bullets: what you'll change/do, and how you'll know it worked (this becomes your Assert step). Scale it to the task — trivial work needs one line, not a document.

## On the loop-back

If you arrived here *after a failed Assert*, this pass is different: the failure is your new context. Ask **"why did it fail — what do I now know that I didn't before?"** Read the actual error/output. Update the diagnosis and the plan with that information, then Act to fix it. Don't retry the same action hoping for a different result.

→ Next: **Act** (`act.md`).
