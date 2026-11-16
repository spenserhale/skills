# Walks: surfaces, setup, and reading the result

## Contents

- Choosing the surface
- Clean state and separate sessions
- First-click walk (screenshots only)
- Screen pack (code only)
- No subagent tool
- Reading the table
- What a simulated walker can and cannot show

## Choosing the surface

Use the first row that is available and name it in the report, because the rows are not equally strong evidence.

| Surface | How the walker sees and acts | Strength |
|---------|------------------------------|----------|
| Running product | Browser or desktop automation, deciding from screenshots | Full walk |
| Screenshots only | Names its first action on each image; you say what happens | First-click only |
| Code only, cannot run | Opens one screen file at a time from a screen pack you write | Paper walk: wording and order, not layout |
| No subagent tool | You walk it under the brief's rules | Weakest; a clean finish proves nothing |

Look in the repository's `AGENTS.md` or `CLAUDE.md` for how to launch the product and reach a first-run state. When they do not say, work it out, and after the review offer to record the working commands there.

## Clean state and separate sessions

- Each walker starts where a newcomer starts: nothing configured, the prerequisite missing, lists empty. A profile that already has the provider connected hides the very state under review. Reset storage, use a fresh profile or data directory, or seed an empty account.
- Each walker gets its own session (a named browser session, a separate profile, its own data directory). Walkers that share one session click over each other and the logs become fiction.
- Close every walker's session once its log is in. A walker stops the moment it finishes and leaves its browser running.
- Many browser tools refuse `file://` addresses. Serve static pages over HTTP and give the walker the URL.
- Native dropdown lists, OS dialogs, and tooltips often do not render in a headless screenshot. The brief tells walkers to read a dropdown's choices from the listing; a stray guess or dead end around one is still the tool, so discount it.
- Give the walker a log path outside the repository. A walker that is handed a path into the source tree can read the answer from the code.

## First-click walk (screenshots only)

1. Give each walker the image and the filled brief, with the start slot saying "You are looking at this screen."
2. The walker returns its first action, what it expects, and its `basis`.
3. When you know what the product does next (from the user's description, another screenshot, or the code), tell the same walker and ask for the next action. Continue while you can supply the result. A harness that cannot continue a subagent stops after the first action.
4. Save the same log shape, with `outcome` set to `gave_up` when the walk ended on something that cannot work and `done` only when it could be continued to the end. Score it and call it a first-click walk in the report. First actions that disagree across walkers, or that land on a control that cannot work, are the finding.

## Screen pack (code only)

When the product cannot run, write the screens as files so walkers still meet them one at a time.

- One file per screen state, named without meaning (`s01.md`, `s02.md`): a file called `secrets-add-provider.md` gives the route away.
- List what is visible from top to bottom. Headings, control names, and current values go on plain lines. Put description and helper text on lines starting `(small print)`, so the walker's glance rule still has something to skip.
- After each control, say where it leads: `-> s07`, `-> nothing changes`, or `-> shows: "<the message>"`.
- A screen that changes after setup is a second file. Cover the main path, every screen one step off it, and the unconfigured state of each.
- The walker's start slot is "Open `s01.md`. After each action open only the file that action leads to."

A screen pack carries wording and order but not size, position, or colour. Say so in the report, and prefer a running build for anything where layout is the question.

## No subagent tool

Walk it yourself, once per persona, under the brief's rules, before reading the code again. Mark each log `"walker": "author-<persona>"`. You cannot forget what you know, so an author walk can show dead ends and missing feedback but cannot show that something is findable.

## Reading the table

| What the logs show | What it means | Where the fix lives |
|--------------------|---------------|---------------------|
| Hurried gave up or stalled, careful finished | The wording is carrying the flow | Structure: turn the sentence into a control |
| Every walker stopped at the same screen | That state has no way forward | A missing state: setup card, empty state, specific error |
| `false_done` | The screen looked finished before it was | Completion feedback, or a default that contradicts the goal |
| Walkers chose different first actions | The entry point does not match the user's words | Naming, placement, or an entry where they looked |
| Guesses on the correct path | The path exists and nothing points to it | Labels and affordances |
| Revisits to one screen | They expected the thing to be there | Put it there, or a control that goes to it |
| Many actions, no dead ends | The path is clear and long | Detection, defaults, a guided flow |
| Every walker finished cleanly | The path exists for a patient reader | Nothing proven; rely on inspection for states no walker reached |

Count actions as a description, not as a verdict. NN/g calls the "three-click rule" false: the number of clicks has not been shown to predict success. What costs users is the difficulty of each step, which `basis` and `progress` record.

## What a simulated walker can and cannot show

- **It is more capable than a user, so its failures count and its successes do not.** In a study comparing model-run cognitive walkthroughs with ten people on two mobile apps, the models completed more tasks (100% and 97.2% against 88.2%) and, taken together, identified 3 of the 10 failure points the people identified. A walker that gets stuck has found something real. A walker that sails through has shown only that the path exists.
- **People scan.** In NN/g's reading study 79% of users scanned a new page and 16% read it word by word. A model reads every word unless told otherwise, which is why the brief imposes glance-first reading and records every use of the small print.
- **Do not ask a walker for opinions.** Synthetic users over-report success and satisfaction, so "was that easy?" returns politeness. Use what the walker did.
- **It cannot show** how many real users will fail, trust, taste, emotional response, or what happens across days of use. Report "2 of 3 simulated walkers gave up", never "two thirds of users".
- **Model-only inspection invents problems.** A study of model-run heuristic evaluation matched 21.2% of the issues experts found and added false positives. That is the reason every finding needs a walk step or a named rule behind it.

A walk is a cheap filter before real usability testing, not a substitute for it. When a decision is expensive, say that people should be tested.

## Sources

- Zhong, McDonald, Hsieh, "Synthetic Cognitive Walkthrough": https://arxiv.org/abs/2512.03568
- Guerino et al., "Can GPT-4o Evaluate Usability Like Human Experts?": https://arxiv.org/abs/2506.16345
- "UXAgent: An LLM Agent-Based Usability Testing Framework for Web Design": https://arxiv.org/abs/2502.12561
- NN/g, "Synthetic Users": https://www.nngroup.com/articles/synthetic-users/
- NN/g, "How Users Read on the Web": https://www.nngroup.com/articles/how-users-read-on-the-web/
- NN/g, "Stop Counting Clicks": https://www.nngroup.com/videos/3-click-rule/
- NN/g, "Evaluate Interface Learnability with Cognitive Walkthroughs": https://www.nngroup.com/articles/cognitive-walkthroughs/
- NN/g, "Turn User Goals into Task Scenarios": https://www.nngroup.com/articles/task-scenarios-usability-testing/
