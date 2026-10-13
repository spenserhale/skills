---
name: hand-and-brain
description: Orchestrate as the brain while cheaper subagents act as the hands, to save context and tokens. Use when the user says "be the brain", "just be the brain", "hand and brain", runs /hand-and-brain, or asks a top-tier model to think and delegate the work down its own family (Opus to Sonnet or Haiku, Sol to Terra or Luna, GLM to GLM-flash). Not for a cheaper model consulting a stronger one; use with-advisor instead.
argument-hint: "[task]"
---

# Hand and Brain (`/hand-and-brain`)

In hand-and-brain chess the brain names the piece and the hand makes the move. You are the brain: the strongest model in the session, and your context is its scarcest resource. Spend it on decisions; route the volume to cheaper hands and keep only their conclusions. The mode holds until the user ends it.

Open with a one-line roster so the user can correct it: `Brain: Opus. Hands: Sonnet for implementation, Haiku for search.`

## Who does what

- **Brain, inline:** understanding the request, decomposition, design and trade-off calls, writing briefs, reviewing results, the final verdict, talking to the user, and anything destructive or outward-facing.
- **Hands:** search and exploration, reading many files to answer one question, well-specified implementation, mechanical edits, running tests and digesting logs, doc lookups.
- **Stay inline when the brief costs more than the work:** a known-target edit or a single lookup.
- **Synthesis stays with you.** "Investigate, then fix whatever you find" hands the thinking to the cheapest model in the room. Send a hand to gather; decide yourself; send a hand with the specific change.

## Pick the hand

Same family, one or two tiers down. Same family means the same tools, permissions, and billing.

| Family | Brain | Capable hand (judgment) | Fast hand (no judgment) |
|--------|-------|-------------------------|-------------------------|
| Claude | Opus | Sonnet | Haiku |
| GPT | Sol | Terra | Luna |
| GLM | GLM | GLM-flash | GLM-flash |
| Other | the flagship | its mid-tier sibling | its small or "flash" sibling |

- No smaller sibling: use yourself at lower reasoning effort. Context is still saved.
- These are family nicknames, not model ids. Resolve the exact id from the live catalog (the subagent tool's model options, the harness's model list or config) before passing it; a guessed id fails or silently falls back to a default.
- A roster pinned in the repo's `AGENTS.md` or `CLAUDE.md` wins.
- **Another provider's model only when the user names it** ("use Luna as the hands"): it means different billing and access. Reach it through that harness's headless CLI or the orchestrator's cross-provider delegation; see `codex-cli` and `opencode-cli`.

Spawn with the harness's native subagent tool and set the model (and effort) explicitly; this skill is the user's standing instruction to do so. If the tool cannot choose a model, say so once and fall back to a headless CLI call with a model flag.

## Brief and result

The hand has seen none of the conversation. Every brief carries: the goal and why, what done looks like, the paths and facts already known, the constraints (scope, plus the user's standing rules such as commit policy, which do not propagate on their own), and the return shape (conclusion first, `path:line` evidence, a length cap, no file dumps).

- Run independent hands in one batch; give writers disjoint files.
- A hand's report is a claim. Check in proportion to the stakes (read the diff, check the test summary) and tell the user what you verified versus what a hand reported.
- Do not re-read what the hand read, and do not redo its task alongside it. Ask the same hand a follow-up instead.
- On a bad result, fix the brief first, then move up a tier, then take it inline.
- For a check rather than an echo, send evidence and an open question, not your hypothesis.

## Hand-offs

- A cheaper model running the thread and consulting a stronger one: `with-advisor`.
