---
name: aaa
description: "Arrange · Act · Assert — a lightweight three-step loop for getting any task done right the first time, then proving it. Use for smaller one-shot tasks of any kind: fixing a bug, implementing a ticket, wiring up a library, or non-coding work like fetching, gathering, or transforming information. Triggers on /aaa, \"arrange act assert\", or when the user wants a quick task done carefully but without heavyweight spec-and-plan ceremony."
---

# Arrange · Act · Assert (`/aaa`)

A distilled, general-purpose loop for one-shot tasks. It's the lightweight cousin of a full spec → plan → implement → verify workflow: three steps instead of a pipeline, done inline instead of with subagents. Works for **any** task — writing code, but equally "go fetch this data," "gather this context," "transform this file."

The whole point is the loop:

```
       ┌──────────────────────────────────────────────┐
       │                                              │
   ARRANGE ───────►  ACT  ───────►  ASSERT ───► done ✓
  get context      do the work     prove it       │
  + a plan                          worked         │
       ▲                              │            │
       └──────── failed? why? ────────┘
         (feed the reason back as new context)
```

If **Assert** fails, you don't patch blindly — you return to **Arrange** with the failure as fresh context ("why did this fail? what do I now know that I didn't before?"), re-**Act** to fix it, and re-**Assert**. Loop until the task is genuinely complete.

## When to use

- Smaller, well-scoped tasks that still deserve to be done correctly the first time.
- Bug fixes, single tickets, adding/using a library, a focused change.
- Non-coding tasks: retrieving information, gathering context, validating or transforming data.
- Any time you'd otherwise "just do it" but want a quick guardrail that the work is set up right and actually worked.

For large, multi-subsystem efforts that need a written spec and a task-by-task plan, use a heavier workflow instead. `/aaa` is deliberately light.

## The three steps

Do them in order. Each has a companion file in this skill directory with the details — read it when you reach that step.

1. **Arrange** — `arrange.md`. Get the right context so success is possible, then form a short plan. Prompt the user if there's ambiguity only a human can resolve.
2. **Act** — `act.md`. Do the work inline. No subagent — these are one-shots; just make the change or take the action.
3. **Assert** — `assert.md`. Prove the action worked, using whatever validation fits (tests, dry run, browser check, data validation). If it fails, loop back to Arrange.

## How to run it

Announce the step you're on so the user can follow the loop: **"Arrange: gathering context on X."** → **"Act: making the change."** → **"Assert: running the tests."**

Create a TodoWrite with the three steps (Arrange / Act / Assert) so the loop is visible. On a failed Assert, add a new Arrange todo rather than silently retrying — the re-entry into Arrange is the whole discipline.

Keep it proportional. A truly trivial task might be one sentence of Arrange, a single edit for Act, and one command for Assert. The steps never disappear, but they scale down.

## The one rule that makes it work

**Never claim done from Act alone.** "I made the change" is not "it works." The Assert step, with real evidence, is what separates this loop from just-doing-it. If you haven't run the validation in this turn, you can't say it passed.
