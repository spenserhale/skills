---
name: ux-reviewer
description: Usability review of a UI flow, to find out whether a first-time user can find it, understand it, and finish it. Use after building or changing a settings screen, setup or onboarding flow, form, or empty state and before calling that UI work done, and whenever the user asks to review the UX, asks whether something is confusing or obvious, asks how many clicks a task takes, or reports that users get stuck, cannot find a setting, or cannot change one, even if they only share a screenshot and never say "UX". Not for code defects in a diff (use a code review skill), visual styling or accessibility-rule audits, or exploring new layouts (use mock-in-thread).
argument-hint: "[flow, screen, or URL]"
compatibility: Walks need a subagent tool plus browser or desktop automation; references/walks.md covers weaker fallbacks. The scoring script needs Python 3.8+.
---

# UX reviewer

Whoever built a screen cannot see it the way a newcomer does. You know where everything lives, your profile is already configured, and you read every word. Real users glance, act on the first thing that looks right, and leave. So collect evidence from someone who lacks your knowledge before you give an opinion: fresh subagents walk the flow as first-time users, then you inspect what they could not reach. A finding is something that happened in a walk or a named pattern rule that a state breaks, ranked by how badly it stops people.

## Steps

1. **Frame the task.** Before opening the code again, write down:
   - what a user comes here to get done (one to three outcomes, in their words);
   - who arrives and what they already know (table below);
   - where they really start, which is rarely the screen under review;
   - the states they can meet: nothing set up, a prerequisite missing, partly set up, working, failed.

   Then do the task yourself from a clean, unconfigured state and count the shortest correct path in actions (a click, a choice from a list, typing into one field, a toggle). Done when the goal, start, knowledge level, and shortest path are written down. A change with no task in it (a label, a colour) skips to step 4; say the walk was skipped.

2. **Brief the walkers.** Fill `assets/walker-brief.md` once per walker; its header holds the persona texts. Default to three, who differ in how much they read: hurried reads no small print, everyday reads it when stuck, careful reads it before acting. Two (hurried and careful) are enough for a single screen. Each walker is a fresh subagent, not a fork or a continuation, on the smallest model tier offered: a fork knows what you know, and a small model is cheap to run three times and less able to brute-force a confusing screen. Save each filled brief as `<walker>.brief.md` beside its log so the walk can be audited.

   | The walker knows | It is told | Use for |
   |------------------|------------|---------|
   | Cold | the goal only | first run, onboarding, anything public |
   | Familiar (default) | the goal and the names on the product's first screen | a feature inside a product people already use |
   | Briefed | the goal and the announcement or doc a user would really have read | features that ship with a guide |

   Check every brief for leaks before sending, because a leaked brief makes the walk worthless without looking wrong:

   ```bash
   python3 scripts/check_brief.py <walks-dir>/*.brief.md --labels "<every label, menu, section, and field name on the shortest path>"
   ```

   It flags those words anywhere in a brief, unfilled slots, and pointers to the source. Reword each flagged line, or pass `--allow` for a word the user would say without having seen the interface. Test data leaks too: "make up any value you are asked for" names nothing, where "use this passphrase" tells the walker a passphrase is coming. The script cannot see a hint about what you expect to go wrong, so leave that out yourself. Done when it prints "no leaks".

3. **Walk and score.** Run the walkers in parallel against the running product, each in its own clean session that starts unconfigured. No runnable product, only screenshots, or no subagent tool: read `references/walks.md` for the weaker variants. When the logs are in, compare each `done_evidence` with the real success condition and set `outcome` to `false_done` where a walker stopped short. Then:

   ```bash
   python3 scripts/score_walks.py <walks-dir> --shortest <n>
   ```

   Done when the table prints with a row per walker. Read it this way:
   - A walker that gave up, stopped short, hit a dead end, or needed the small print or a guess is strong evidence. It reads more, tires less, and knows more software than a real user.
   - A walker that finished cleanly is weak evidence: the path exists, which is not the same as people finding it.
   - Hurried gave up or stalled where careful finished: the wording is carrying the flow. Fix the structure, not the wording. (`stalled` is the script's mark for a walker that reads no small print and could only go on by using it.)
   - Actions against the shortest path describe the walk. They are not the verdict: one step taken on a guess costs a user more than three taken on a clear label.

4. **Inspect.** Now read the screens and code for what a walk cannot show: the states from step 1 that no walker reached, and these rules, on every screen of the shortest path and not only the one under review. `references/patterns.md` has the rest, with reasons.
   - **A section that cannot work yet shows one setup card in place of its controls:** what the section does, one button that goes straight to the exact place with the right option already chosen, and a line saying where that button leads and why. The card names no route to follow by hand. Finishing returns the user to the section, now working, with a line saying so.
   - **A route written in a sentence becomes a control.** "Go to Settings > Secrets" is navigation the user has to perform by hand.
   - **Nothing looks usable that is not:** no dropdown with one option, no editable field beside a warning that it has no effect, no toggle that flips itself back.
   - **Detect before asking.** What the product can find out (an installed tool, a signed-in account, a value entered elsewhere) it uses, shows, and lets the user change.
   - **Default to what most users want** when that is predictable and safe; require a choice when a wrong default is costly. First in the list is not a default.
   - **Three or more dependent steps, or steps in more than one place, get a guided flow** started from where the user already is. Independent settings stay a plain page.
   - **Every action answers where the user acted:** what changed, and on failure exactly what is missing with a control that goes there.

5. **Report.** Use the template below. Rank by severity, give at most five findings in detail, and put the rest in one line each.

   | Severity | Evidence that earns it |
   |----------|------------------------|
   | 4 blocker | most walkers gave up or stopped short, or a state has no way forward |
   | 3 major | the hurried walker gave up or stalled where readers finished, or walkers got through only by the small print, a guess, or a dead end |
   | 2 minor | a walker slowed and recovered at once, or a rule is broken that every walker got past cleanly |
   | 1 cosmetic | noticed, cost nothing |

   For a state no walker reached, rate what it would do to a walker there and mark the rating as predicted. Every finding cites its evidence: a walker and step, or a state and a rule. An item with neither is an impression; leave it out. A finding is its headline, its evidence, and its fix, a sentence or two each. When every walker finished and nothing rates above 2, use the short form of the template. A review that always finds ten things stops being read.

6. **Fix and walk again**, when the change is yours to make. Fix every 3 and 4, then repeat steps 2 and 3 with new walkers and show both tables. Judge the new walk like the first: a walker that gave up, stopped short, or left the new path for the small print, a guess, or a detour means another round. Done when a walk is clean, or after two rounds, with what remains in the report and its reason.

## Report template

```markdown
## UX review: <flow>

**Verdict:** <can a first-time user finish, and what stops them, in one or two sentences>

**Walks:** <surface>, <n> simulated walkers who knew <level>, shortest path <n> actions
<table from score_walks.py; its lists are for you, so cite the steps that matter as evidence below>

**Findings**
1. **[4] <what stops or slows people>.** Evidence: <walker and step, or state and rule>. Fix: <the change, naming the pattern>.

Also: <one line each for the rest>

**Proposed change:** <the top fix made concrete: the card's wording, the new order of steps, the default>

**Limits:** <what the walks cannot show here, and anything not tested>
```

Short form, when every walker finished and nothing rates above 2:

```markdown
## UX review: <flow>

**Verdict:** <a first-time user can finish, and what that rests on>

**Walks:** <surface>, <n> simulated walkers who knew <level>, shortest path <n> actions
<table from score_walks.py>

**Minor:** <one line each, five at most>

**Limits:** <clean simulated walks show the path exists, not that people find it; anything not tested>
```

Keep to these sections. A reader skims a review the way a user skims a screen.

## Gotchas

- **A walker in your working profile is not a first-time user.** The profile that built the feature already has the prerequisite connected, which is how a dead first-run screen ships unseen. Reset to the unconfigured state for every walker.
- **A text listing of the screen flattens it.** Accessibility snapshots print helper text at the same weight as headings, so a walker deciding from one "sees" instructions a person would skip. The brief tells walkers to decide from the picture; give them a tool that can take one.
- **A walker that has seen the flow is spent.** Use a new subagent for every run, including the walk after a fix.
- **Do not ask walkers whether it was easy.** They answer politely. Use what they did.
- **Simulated walkers are not a sample of users.** Write "2 of 3 simulated walkers gave up", never a share of users, and say what was not tested.
- **Stay on the question.** Code defects, visual polish, and accessibility-rule audits met along the way get one line under "Also" at most. A hard-coded list or a contrast ratio is not a usability finding unless a walker tripped on it.
- **A log records the tool as well as the product.** A selector that matched twice, or a menu that did not render in a screenshot, is not a finding. Reproduce a surprising step yourself before reporting it.

## Resources

- Read `references/walks.md` when the product cannot be driven live, when walkers need a clean state or separate sessions, or when a table is hard to interpret.
- Read `references/patterns.md` when writing a fix, or when a finding involves prerequisites, defaults, detection, multi-step setup, feedback, or wording.
- Run `python3 scripts/check_brief.py --help` and `python3 scripts/score_walks.py --help` before reading their source. The first checks filled briefs for leaks; the second validates the logs and prints the table and the moments worth reading.
- Fill `assets/walker-brief.md` and send it as each walker's whole prompt.
- To explore the redesign as mockups, use `mock-in-thread`. For defects in the code, use a code review skill.
