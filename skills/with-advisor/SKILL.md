---
name: with-advisor
description: Keep the main thread on a cheaper model while a stronger model stays on call as a read-only advisor for planning, hard decisions, and getting unstuck. Use when the user says "use Opus as an advisor", "use X as an advisor", "with an advisor", "ask the bigger model if you get stuck", runs /with-advisor, or wants a long task kept on a mid-tier model with occasional escalation (Sonnet to Opus, Terra to Sol, GLM-flash to GLM). Not for a top-tier model delegating work down; use hand-and-brain instead.
argument-hint: "[task]"
---

# With Advisor (`/with-advisor`)

You are the executor: cheap enough to run a long thread, doing the work yourself. A stronger model is on call. One consult costs a fraction of running the task on that model, so the saving comes from spending it only where better judgment changes the outcome. The mode holds until the user ends it.

Open with a one-line roster so the user can correct it: `Executor: Sonnet. Advisor: Opus, for plan review and when stuck.` Then start working; learn the task before the first consult.

## Pick the advisor

Same family, one tier up. Same family means the same tools, permissions, and billing.

| Family | Executor | Advisor |
|--------|----------|---------|
| Claude | Haiku or Sonnet | Opus (Sonnet is enough for Haiku's easier questions) |
| GPT | Luna or Terra | Sol (Terra is enough for Luna's easier questions) |
| GLM | GLM-flash | GLM |
| Other | the mid or "flash" model | its flagship sibling |

- No stronger sibling: consult yourself at higher reasoning effort in a fresh context, which is not anchored on your failed attempts.
- These are family nicknames, not model ids. Resolve the exact id from the live catalog (the subagent tool's model options, the harness's model list or config) before passing it; a guessed id fails or silently falls back to a default.
- An advisor pinned in the repo's `AGENTS.md` or `CLAUDE.md` wins.
- **Another provider's model only when the user names it** ("use Sol as the advisor"): it means different billing and access. Reach it through that harness's headless CLI or the orchestrator's cross-provider delegation; see `codex-cli` and `opencode-cli`.

Spawn with the harness's native subagent tool and set the model (or effort) explicitly; this skill is the user's standing instruction to do so. If the tool cannot choose a model, say so once and fall back to a headless CLI call with a model flag.

## When to consult

- Before committing to something costly to undo: schema, public API, migration, architecture. Ask before writing the code.
- Stuck: two real attempts at the same problem have failed. A third try with no new information is the signal.
- The evidence contradicts your model of the system and you cannot explain it.
- Before a high-blast-radius step you are unsure of. This informs the step; it never replaces the user's confirmation.
- Before calling a large task done, when a miss would be expensive.
- The user asks.

Otherwise do it yourself: not when a test run, a doc lookup, or one more file would answer it, and not for reassurance. Expect zero to three consults per task. Needing one every few steps means the task belongs on the stronger model; tell the user rather than turning the advisor into the worker.

## Ask, then use

The advisor has seen nothing. Send the goal, the current state with paths (let it read rather than pasting files), each attempt with its exact result and error text verbatim, the constraints, the one decision or diagnosis you need, and the answer shape you want (a decision with risks, a plan, or ranked hypotheses with a test for each) with a length cap.

- For a diagnosis, send the evidence and hold back your theory; an advisor handed a hypothesis tends to confirm it.
- The advisor advises, you edit. "Here is the bug, fix it" erases the saving.
- You still own the outcome: the advisor reasons better and knows less. Treat advice as a hypothesis and test it before building on it. If it conflicts with evidence, send that evidence back once.
- For a follow-up, continue the same advisor conversation rather than re-briefing a new one.
- Tell the user in a line when a consult changed the course.

## Hand-offs

- A top-tier model orchestrating cheaper workers: `hand-and-brain`.
