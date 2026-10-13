---
name: reflect
description: Sprint retro on a thread, aimed at the agent's environment (docs, skills, memory, tooling, checks) rather than the work.
disable-model-invocation: true
argument-hint: "[focus, or path to another session's transcript]"
---

# Reflect (`/reflect`)

A sprint retro for a thread. Its subject is the environment the agent worked in (docs, skills, memory, tools, checks), so the next thread on similar work goes better; the work product is out of scope. Every finding points at a specific moment in the thread. A finding with no moment is generic advice: drop it.

If the user named a focus (a skill, a doc, one stretch of the thread) or another session's transcript, scope to that.

## Steps

1. **Recover the whole thread.** The conversation in context is the primary source, but after compaction or a long run the middle has faded, and the middle is where the struggles were. In Claude Code, run this from the skill's folder:

   ```bash
   python3 scripts/session_costs.py            # newest transcript for this directory
   python3 scripts/session_costs.py <path>     # a specific session
   ```

   It prints every user message in order, per-tool call counts and result sizes, the largest results, and failed calls, without the result bodies. Confirm the printed first prompt is this thread. In another harness, or when it finds nothing, work from context and say the numbers are estimates from memory. Done when you can list the user's corrections and the costly stretches.

2. **Ask the four questions.** Collect moments, not opinions.
   - **What worked?** Things that landed first try or that the user confirmed. Keep only what is worth protecting: it worked because of a doc, skill, or tool (leave that alone), or despite the lack of one (a candidate to write down).
   - **What didn't?** Corrections, redirects, repeated instructions, retries, abandoned approaches. Trace each one: what happened, why the agent did that, what in the environment caused or allowed it.
   - **What information was stale or wrong?** A doc, skill, memory, or comment that named a missing file, a renamed command, or a retired process, whether the user corrected it or you found out the hard way. Record the file and line, what it claims, and what is true.
   - **What was expensive to find?** A fact that took many calls or large results: a browser session where an API or CLI would have answered, ten searches where one pointer would have, a whole-file read for three lines. Estimate tokens spent, the cheaper path's cost, and the difference.

   Done when every candidate has its moment attached (a quote, or a message or call number).

3. **Check each candidate against the present.** Open the file. Confirm the stale line is still there, the cheaper tool does not already exist, the check is not already written but unwired, the preference is not already recorded. Search for other copies of a stale claim, because docs get pasted. Drop one-offs: a correction that applied only to this task teaches nothing durable. Done when every survivor is confirmed true right now.

4. **Route each to the smallest durable fix**, using the table below.

5. **Present ranked proposals and wait.** Use the format below, most payoff first, at most five. Nothing is edited until the user picks. A smooth thread has little to teach; "nothing worth changing" is a complete and correct result.

6. **Apply what was approved, then verify.** Make the edit, then prove it: the pointer resolves, the command runs, the check fails on the bad case, the skill validates. Report each as done, deferred, or declined. Commit only if the user asks, following the repo's conventions.

## Where each fix goes

| Finding | Fix | Lands in |
|---------|-----|----------|
| Stale or wrong statement | Correct or delete it at the source, in every copy | The doc, skill, or memory that said it |
| Slow to find a file or fact | A one-line pointer | A file the agent already reads on that path: the doc it started from, the relevant skill, the nearest `AGENTS.md`/`CLAUDE.md` |
| Mistake a tool could have caught | A check that fails: lint rule, type, test, hook, CI job. Wire an existing one before writing a new one | The repo's own check setup |
| Expensive route to information | A cheaper path: an existing CLI or API, a small script, an MCP server, read-only access, a log teed to a file | Tooling, plus one line in the relevant skill or doc naming the cheap path |
| A skill steered wrong or left a gap | Change that instruction | The skill's source |
| Durable user preference or correction | One line at the narrowest scope that covers it | Memory, project instructions, or user-level instructions |
| Multi-step process repeated by hand | A skill or script; sketch it only | Hand off to the skill-creation skill once approved |
| Instruction that changed nothing; bloated always-loaded file | Delete it or move it out | That file |
| One-off | Nothing | Listed under "Left alone" with the reason |

## Proposal format

Sensible default; adjust to the thread.

```markdown
## Reflect: <the thread in a few words>

**Worked**
- <what, and its moment>

**Proposals**
1. **<change>** in `<file or tool>`
   - Moment: <quote or call number, what happened>
   - Cause: <why the environment produced it>
   - Change: <exact before and after text, or the command or tool to add>
   - Payoff: <~N tokens, N calls, or one fewer correction per thread, with the arithmetic>

**Left alone**
- <one-off or unconfirmed candidate, and why>
```

## Gotchas

- **The end of the thread is vivid and the middle is not.** Without the transcript, a retro reports the last twenty minutes and invents the rest to fill the categories.
- **Always-loaded files cost every session.** `AGENTS.md`, `CLAUDE.md`, the memory index, and skill descriptions are read whether relevant or not. Adding a line there is the last resort, after fixing the source, adding a pointer, or adding a check. A deletion counts as a win.
- **Fix the source, not the symptom.** A new rule saying "ignore the old deploy doc" leaves two documents disagreeing. Edit the old doc.
- **Installed skills are copies.** A skill under a user or project skills folder is often a symlink or a managed install that the next update overwrites. Find its source (a lock file or the symlink target names it) and edit there, or hand the user the patch for an upstream they do not own.
- **Token figures are estimates.** Prefix them with `~` and show the arithmetic: `calls #14 to #19: ~18,000 tokens over 6 calls; one API call would return ~500`. Lead with the fresh figure. A result is also re-read on every later request (the script's `carried` column), so early waste costs more than late waste, but those re-reads are mostly cached and billed at a fraction: cite them as a multiplier, never as a second saving added to the first.
- **Scope widens the blast radius.** User-level instructions and shared team docs affect other projects and people. Name the scope in the proposal.
- **A defect in the work itself is not a finding.** Mention it and leave it to the thread; the finding is whatever let it through.
- **No retro file by default.** The fixes are the record. Write one only when the repo's agent docs name a place for it or the user asks.

## Resources and hand-offs

- Run `python3 scripts/session_costs.py --help` before reading its source. `--top N` lists more of the largest results; `--json` gives every call for drilling into one stretch.
- To record what was built, use the `doc-it` skill. To turn a proposal into a new skill, use the project's skill-creation skill (`sh-skill-creator` where installed).
