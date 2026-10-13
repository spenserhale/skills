# Waste, unevenness, overburden (muda, mura, muri)

Waste is any activity that consumes time or attention without moving the requested outcome forward. The Toyota list of seven wastes has a standard software translation (Mary and Tom Poppendieck); the table gives each with what it looks like in a repo and in an agent's own session.

Two neighbors matter as much as waste itself. Unevenness (mura) is variation that makes work unpredictable. Overburden (muri) is asking a person, a tool, or a context window to hold more than it can. Both produce waste downstream, so removing waste while leaving them in place does not last.

## The wastes

| Waste | In a repo | In a session | Signal to count |
|-------|-----------|--------------|-----------------|
| Partially done work | TODO stubs, commented-out code, unmerged branches, flags never removed | Starting a second change before the first is verified; leaving a stub "for later" | Markers; branch count and age; dead flags |
| Extra features | Options, config, and abstractions nothing uses | Parameters nobody asked for; "while I'm here" refactors | Unused exports, options with one caller, config keys never set |
| Relearning | Commands and decisions that live in someone's head | Rediscovering the test command each session; re-reading the same files | Docs that do not match what works; repeated questions |
| Handoffs | Knowledge lost between people, teams, or tools | A thin brief to a subagent; a summary that drops the detail | Rework after handoff; questions the brief should have answered |
| Task switching | Many things in flight per person | Folding unrelated fixes into the task | Work in progress per owner; mixed-purpose changes |
| Delays | Slow checks, waiting on review or CI | Running the full suite when a focused check would answer | Check time; time waiting for review |
| Defects | Escaped bugs and the rework they cause | A failure passed downstream and fixed later at higher cost | Reverts and fix-of-a-fix commits; failing or flaky tests |

## Unevenness and overburden

| Kind | Looks like | Signal to count |
|------|-----------|-----------------|
| Unevenness | Flaky tests; two patterns for the same job; long quiet spells then one huge change | Re-runs needed to pass; variants of one pattern; spread in change size |
| Overburden | Files, functions, or tasks too large to hold in mind; a suite too slow to run per change; a context window filled with output nobody needed | Largest files and functions; check time; size of command output |

## Necessary and unnecessary

Some non-value work is required (a review, a compliance check, a migration step). Reduce its cost; do not remove it. The waste to eliminate is the kind that could vanish with nobody downstream noticing.

## Pitfalls

- **Overproduction is the worst waste, because it hides the others.** Extra code looks like progress, and it creates more to test, read, and maintain.
- **Removing waste by adding process is waste.** A new checklist, document, or meeting needs the same justification as a new feature.
- **Local gains can cost more elsewhere.** A faster step that produces work the next step cannot absorb has only moved the pile. Check the whole path.
- **Count before naming.** "There is a lot of dead code" is an impression. A number makes it a finding, and makes the improvement checkable.
